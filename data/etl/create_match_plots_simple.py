import json
import logging
import pandas as pd
import numpy as np
import time
from typing import List, Dict, Any
import warnings
from statsbombpy import sb
from flask import Flask
from app import app
from utils.db import db
from models import Match, MatchPlot, Season
from utils.plots.plot_factory import MatchDataProcessor, generate_all_plots_sync


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles numpy data types"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif pd.isna(obj):
            return None
        return super().default(obj)

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
logger = logging.getLogger("create_match_plots_simple")

print(f"Using DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")


def process_single_match(match: Match) -> Dict[str, Any]:
    """Process a single match and return plot data"""
    try:
        logger.info(f"Processing match {match.id}...")
        
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
            try:
                plot_dict[plot_type] = json.dumps(plot_data, cls=NumpyEncoder)
            except Exception as json_error:
                logger.error(f"JSON serialization failed for {plot_type}: {json_error}")
                raise
        
        return {
            'match_id': match.id,
            'plots': plot_dict,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to process match {match.id}: {e}")
        import traceback
        traceback.print_exc()
        return {
            'match_id': match.id,
            'plots': {},
            'success': False,
            'error': str(e)
        }


def update_database_with_plots(match_id: int, plots: Dict[str, str]):
    """Update database with plots for a single match"""
    try:
        # Get existing plots for this match
        existing_plots = {
            plot.plot_type: plot 
            for plot in MatchPlot.query.filter_by(match_id=match_id).all()
        }
        
        for plot_type, plot_json in plots.items():
            if plot_type in existing_plots:
                # Update existing
                existing_plots[plot_type].plot_json = plot_json
                logger.debug(f"Updated {plot_type} for match {match_id}")
            else:
                # Insert new
                new_plot = MatchPlot(
                    match_id=match_id, 
                    plot_type=plot_type, 
                    plot_json=plot_json
                )
                db.session.add(new_plot)
                logger.debug(f"Inserted {plot_type} for match {match_id}")
        
        # Commit changes for this match
        db.session.commit()
        logger.info(f"✅ Successfully saved plots for match {match_id}")
        
    except Exception as e:
        logger.error(f"❌ Database update failed for match {match_id}: {e}")
        db.session.rollback()
        raise


def create_all_match_plots_simple():
    """Simple, robust version of match plot creation"""
    with app.app_context():
        start_time = time.time()
        
        # Get all matches
        matches = Match.query.all()
        total_matches = len(matches)
        logger.info(f"🚀 Starting SIMPLE processing of {total_matches} matches...")
        
        processed_count = 0
        failed_count = 0
        
        # Process matches one by one (simple and reliable)
        for i, match in enumerate(matches, 1):
            try:
                logger.info(f"📦 Processing match {i}/{total_matches} (ID: {match.id})")
                
                # Process the match
                result = process_single_match(match)
                
                if result['success']:
                    # Update database immediately
                    update_database_with_plots(result['match_id'], result['plots'])
                    processed_count += 1
                    logger.info(f"✅ Match {match.id} completed successfully")
                else:
                    failed_count += 1
                    logger.error(f"❌ Match {match.id} failed: {result.get('error', 'Unknown error')}")
                
                # Progress update every 10 matches
                if i % 10 == 0:
                    elapsed = time.time() - start_time
                    progress = i / total_matches * 100
                    avg_time = elapsed / i
                    remaining_time = avg_time * (total_matches - i)
                    
                    logger.info(f"📈 Progress: {progress:.1f}% ({i}/{total_matches})")
                    logger.info(f"⏱️  Elapsed: {elapsed:.1f}s, Remaining: ~{remaining_time:.1f}s")
                    logger.info(f"📊 Success: {processed_count}, Failed: {failed_count}")
                
            except Exception as e:
                failed_count += 1
                logger.error(f"❌ Unexpected error processing match {match.id}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Final statistics
        total_time = time.time() - start_time
        total_plots_in_db = MatchPlot.query.count()
        
        logger.info(f"🎉 ETL Complete!")
        logger.info(f"⏱️  Total time: {total_time:.2f}s ({total_time/60:.1f} minutes)")
        logger.info(f"📊 Matches processed: {processed_count}/{total_matches}")
        logger.info(f"❌ Failed matches: {failed_count}")
        logger.info(f"💾 Total plots in database: {total_plots_in_db}")
        if processed_count > 0:
            logger.info(f"🚀 Average speed: {total_time/processed_count:.2f} seconds/match")


if __name__ == "__main__":
    create_all_match_plots_simple()
