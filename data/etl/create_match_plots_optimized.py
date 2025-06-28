import json
import logging
import pandas as pd
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
import warnings
from statsbombpy import sb
from flask import Flask
from app import app
from utils.db import db
from models import Match, MatchPlot, Season
from utils.plots.plot_factory import MatchDataProcessor, generate_all_plots_async, generate_all_plots_sync

# Suppress common warning spam
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)

# Quiet noisy libs
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.WARNING)

# Set up logger for this ETL script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("create_match_plots_optimized")

print(f"Using DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")


class MatchPlotProcessor:
    """Optimized match plot processor with batching and concurrency"""
    
    def __init__(self, batch_size: int = 10, max_workers: int = 4):
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.processed_count = 0
        self.failed_count = 0
        self.start_time = None
    
    def process_single_match(self, match: Match) -> Dict[str, Any]:
        """Process a single match and return plot data"""
        try:
            logger.debug(f"Processing match {match.id}...")
            
            # Fetch events data
            events = sb.events(match.id).fillna(-999)
            match_df = pd.DataFrame(events)
            
            # Create processor for shared data preprocessing
            processor = MatchDataProcessor(match_df)
            
            # Generate all plots using the factory
            all_plots = generate_all_plots_sync(processor)
            
            # Convert to JSON strings for database storage
            plot_dict = {}
            for plot_type, plot_data in all_plots.items():
                plot_dict[plot_type] = json.dumps(plot_data)
            
            return {
                'match_id': match.id,
                'plots': plot_dict,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process match {match.id}: {e}")
            return {
                'match_id': match.id,
                'plots': {},
                'success': False,
                'error': str(e)
            }
    
    async def process_single_match_async(self, match: Match) -> Dict[str, Any]:
        """Async version of single match processing"""
        try:
            logger.debug(f"Processing match {match.id} (async)...")
            
            # Fetch events data (this is the main I/O bottleneck)
            loop = asyncio.get_event_loop()
            events = await loop.run_in_executor(
                None, lambda: sb.events(match.id).fillna(-999)
            )
            match_df = pd.DataFrame(events)
            
            # Create processor for shared data preprocessing
            processor = MatchDataProcessor(match_df)
            
            # Generate all plots concurrently
            all_plots = await generate_all_plots_async(processor)
            
            # Convert to JSON strings for database storage
            plot_dict = {}
            for plot_type, plot_data in all_plots.items():
                plot_dict[plot_type] = json.dumps(plot_data)
            
            return {
                'match_id': match.id,
                'plots': plot_dict,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process match {match.id}: {e}")
            return {
                'match_id': match.id,
                'plots': {},
                'success': False,
                'error': str(e)
            }
    
    def batch_update_database(self, results: List[Dict[str, Any]]):
        """Efficiently update database with batch of results"""
        try:
            # Prepare bulk operations
            updates = []
            inserts = []
            
            for result in results:
                if not result['success']:
                    continue
                
                match_id = result['match_id']
                plots = result['plots']
                
                # Get existing plots for this match
                existing_plots = {
                    plot.plot_type: plot 
                    for plot in MatchPlot.query.filter_by(match_id=match_id).all()
                }
                
                for plot_type, plot_json in plots.items():
                    if plot_type in existing_plots:
                        # Update existing
                        existing_plots[plot_type].plot_json = plot_json
                        updates.append(existing_plots[plot_type])
                    else:
                        # Insert new
                        new_plot = MatchPlot(
                            match_id=match_id, 
                            plot_type=plot_type, 
                            plot_json=plot_json
                        )
                        inserts.append(new_plot)
            
            # Bulk operations
            if inserts:
                db.session.bulk_save_objects(inserts)
                logger.debug(f"📥 Bulk inserted {len(inserts)} plots")
            
            if updates:
                # SQLAlchemy doesn't have bulk_update_objects, so we commit the changes
                logger.debug(f"🔄 Updated {len(updates)} plots")
            
            # Commit all changes
            db.session.commit()
            
            successful_matches = sum(1 for r in results if r['success'])
            logger.info(f"✅ Batch committed: {successful_matches} matches processed")
            
        except Exception as e:
            logger.error(f"❌ Database batch update failed: {e}")
            db.session.rollback()
            raise
    
    def process_matches_concurrent(self, matches: List[Match]) -> List[Dict[str, Any]]:
        """Process matches concurrently using ThreadPoolExecutor"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_match = {
                executor.submit(self.process_single_match, match): match 
                for match in matches
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_match):
                match = future_to_match[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result['success']:
                        self.processed_count += 1
                        logger.debug(f"✅ Completed match {match.id}")
                    else:
                        self.failed_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ Exception processing match {match.id}: {e}")
                    self.failed_count += 1
                    results.append({
                        'match_id': match.id,
                        'plots': {},
                        'success': False,
                        'error': str(e)
                    })
        
        return results
    
    async def process_matches_async(self, matches: List[Match]) -> List[Dict[str, Any]]:
        """Process matches asynchronously"""
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def process_with_semaphore(match):
            async with semaphore:
                return await self.process_single_match_async(match)
        
        # Process all matches concurrently with semaphore limiting
        tasks = [process_with_semaphore(match) for match in matches]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Exception processing match {matches[i].id}: {result}")
                self.failed_count += 1
                processed_results.append({
                    'match_id': matches[i].id,
                    'plots': {},
                    'success': False,
                    'error': str(result)
                })
            else:
                if result['success']:
                    self.processed_count += 1
                else:
                    self.failed_count += 1
                processed_results.append(result)
        
        return processed_results
    
    def create_all_match_plots(self, use_async: bool = True):
        """Main method to create all match plots with optimizations"""
        with app.app_context():
            self.start_time = time.time()
            
            # Get all matches
            matches = Match.query.all()
            total_matches = len(matches)
            logger.info(f"🚀 Starting optimized processing of {total_matches} matches...")
            logger.info(f"📊 Configuration: batch_size={self.batch_size}, max_workers={self.max_workers}, async={use_async}")
            
            # Process in batches
            for i in range(0, total_matches, self.batch_size):
                batch = matches[i:i + self.batch_size]
                batch_num = (i // self.batch_size) + 1
                total_batches = (total_matches + self.batch_size - 1) // self.batch_size
                
                logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} matches)")
                batch_start = time.time()
                
                try:
                    if use_async:
                        # Use async processing
                        results = asyncio.run(self.process_matches_async(batch))
                    else:
                        # Use concurrent processing
                        results = self.process_matches_concurrent(batch)
                    
                    # Update database with batch results
                    self.batch_update_database(results)
                    
                    batch_time = time.time() - batch_start
                    avg_time_per_match = batch_time / len(batch)
                    
                    logger.info(f"⏱️  Batch {batch_num} completed in {batch_time:.2f}s ({avg_time_per_match:.2f}s/match)")
                    
                    # Progress update
                    progress = (self.processed_count + self.failed_count) / total_matches * 100
                    logger.info(f"📈 Progress: {progress:.1f}% ({self.processed_count} success, {self.failed_count} failed)")
                    
                except Exception as e:
                    logger.error(f"❌ Batch {batch_num} failed: {e}")
                    continue
            
            # Final statistics
            total_time = time.time() - self.start_time
            total_processed = MatchPlot.query.count()
            
            logger.info(f"🎉 ETL Complete!")
            logger.info(f"⏱️  Total time: {total_time:.2f}s")
            logger.info(f"📊 Matches processed: {self.processed_count}/{total_matches}")
            logger.info(f"❌ Failed matches: {self.failed_count}")
            logger.info(f"💾 Total plots in database: {total_processed}")
            logger.info(f"🚀 Average speed: {total_matches/total_time:.2f} matches/second")


def create_all_match_plots_optimized(batch_size: int = 10, max_workers: int = 4, use_async: bool = True):
    """Entry point for optimized match plot creation"""
    processor = MatchPlotProcessor(batch_size=batch_size, max_workers=max_workers)
    processor.create_all_match_plots(use_async=use_async)


if __name__ == "__main__":
    # Configuration - adjust these based on your system
    BATCH_SIZE = 10      # Number of matches to process in each batch
    MAX_WORKERS = 4      # Number of concurrent workers
    USE_ASYNC = True     # Use async processing (recommended)
    
    create_all_match_plots_optimized(
        batch_size=BATCH_SIZE,
        max_workers=MAX_WORKERS,
        use_async=USE_ASYNC
    )
