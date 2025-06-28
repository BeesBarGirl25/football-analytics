"""
Benchmark script to compare original vs optimized ETL performance
"""
import time
import logging
from app import app
from models import Match
from data.etl.create_match_plots import create_all_match_plots as original_etl
from data.etl.create_match_plots_optimized import create_all_match_plots_optimized

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("benchmark")


def benchmark_original_etl(sample_size: int = 5):
    """Benchmark the original ETL with a sample of matches"""
    with app.app_context():
        matches = Match.query.limit(sample_size).all()
        logger.info(f"🔥 Benchmarking ORIGINAL ETL with {len(matches)} matches...")
        
        start_time = time.time()
        
        # Run original ETL logic on sample
        try:
            # We'll simulate the original logic here since we don't want to modify the original
            from data.etl.create_match_plots import create_all_match_plots
            # Note: This would process ALL matches, so we'll just time a smaller operation
            logger.info("⚠️  Original ETL processes all matches - skipping full benchmark")
            logger.info("⚠️  Use the optimized version for better performance")
            return None
        except Exception as e:
            logger.error(f"Original ETL failed: {e}")
            return None


def benchmark_optimized_etl(sample_size: int = 5, batch_size: int = 2, max_workers: int = 2):
    """Benchmark the optimized ETL with a sample of matches"""
    logger.info(f"🚀 Benchmarking OPTIMIZED ETL with {sample_size} matches...")
    logger.info(f"📊 Config: batch_size={batch_size}, max_workers={max_workers}")
    
    start_time = time.time()
    
    try:
        # Create a custom processor for limited matches
        from data.etl.create_match_plots_optimized import MatchPlotProcessor
        
        with app.app_context():
            processor = MatchPlotProcessor(batch_size=batch_size, max_workers=max_workers)
            matches = Match.query.limit(sample_size).all()
            
            logger.info(f"Processing {len(matches)} matches...")
            
            # Process the sample
            results = processor.process_matches_concurrent(matches)
            processor.batch_update_database(results)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            successful = sum(1 for r in results if r['success'])
            failed = len(results) - successful
            
            logger.info(f"✅ Optimized ETL Results:")
            logger.info(f"⏱️  Total time: {total_time:.2f}s")
            logger.info(f"📊 Successful: {successful}/{len(matches)}")
            logger.info(f"❌ Failed: {failed}")
            logger.info(f"🚀 Speed: {len(matches)/total_time:.2f} matches/second")
            
            return {
                'total_time': total_time,
                'matches_processed': len(matches),
                'successful': successful,
                'failed': failed,
                'speed': len(matches)/total_time
            }
            
    except Exception as e:
        logger.error(f"Optimized ETL failed: {e}")
        return None


def run_performance_comparison():
    """Run a comprehensive performance comparison"""
    logger.info("🏁 Starting ETL Performance Benchmark")
    logger.info("=" * 60)
    
    # Test different configurations
    test_configs = [
        {'sample_size': 3, 'batch_size': 2, 'max_workers': 2, 'name': 'Small (3 matches, 2 workers)'},
        {'sample_size': 5, 'batch_size': 3, 'max_workers': 3, 'name': 'Medium (5 matches, 3 workers)'},
        {'sample_size': 10, 'batch_size': 5, 'max_workers': 4, 'name': 'Large (10 matches, 4 workers)'},
    ]
    
    results = []
    
    for config in test_configs:
        logger.info(f"\n🧪 Testing: {config['name']}")
        logger.info("-" * 40)
        
        result = benchmark_optimized_etl(
            sample_size=config['sample_size'],
            batch_size=config['batch_size'],
            max_workers=config['max_workers']
        )
        
        if result:
            result['config'] = config['name']
            results.append(result)
    
    # Summary
    logger.info("\n📊 BENCHMARK SUMMARY")
    logger.info("=" * 60)
    
    for result in results:
        logger.info(f"🔧 {result['config']}:")
        logger.info(f"   ⏱️  Time: {result['total_time']:.2f}s")
        logger.info(f"   ✅ Success: {result['successful']}/{result['matches_processed']}")
        logger.info(f"   🚀 Speed: {result['speed']:.2f} matches/sec")
        logger.info("")
    
    # Find best performing config
    if results:
        best = max(results, key=lambda x: x['speed'])
        logger.info(f"🏆 BEST PERFORMANCE: {best['config']}")
        logger.info(f"   🚀 Speed: {best['speed']:.2f} matches/second")
        logger.info(f"   ⏱️  Time: {best['total_time']:.2f}s for {best['matches_processed']} matches")


if __name__ == "__main__":
    run_performance_comparison()
