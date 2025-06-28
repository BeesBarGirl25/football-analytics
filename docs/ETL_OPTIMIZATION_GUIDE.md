# ETL Optimization Guide

## Overview

This guide covers the optimized ETL system for generating match plots with significant performance improvements over the original implementation.

## Performance Improvements

### 🚀 Speed Optimizations

1. **Concurrent Processing**: Multiple matches processed simultaneously using ThreadPoolExecutor or async/await
2. **Shared Data Preprocessing**: Match data processed once and reused across all plot types
3. **Batch Database Operations**: Bulk inserts/updates instead of individual transactions
4. **Plot Factory Pattern**: Centralized plot generation with optimized data flow

### 📊 Expected Performance Gains

- **2-4x faster** processing speed depending on system resources
- **Reduced memory usage** through shared data preprocessing
- **Better error handling** with individual match failure isolation
- **Progress tracking** with detailed logging and statistics

## Usage

### Quick Start - Optimized ETL

```bash
# Run the optimized ETL with default settings
python data/etl/create_match_plots_optimized.py
```

### Custom Configuration

```python
from data.etl.create_match_plots_optimized import create_all_match_plots_optimized

# Custom settings for your system
create_all_match_plots_optimized(
    batch_size=10,      # Matches per batch
    max_workers=4,      # Concurrent workers
    use_async=True      # Use async processing
)
```

### Benchmark Performance

```bash
# Test different configurations and find optimal settings
python data/etl/benchmark_etl.py
```

## Configuration Options

### Batch Size
- **Small systems**: 5-10 matches per batch
- **Medium systems**: 10-20 matches per batch  
- **Large systems**: 20+ matches per batch

### Max Workers
- **CPU cores**: Generally 2-4 workers optimal
- **Memory**: More workers = more memory usage
- **I/O bound**: Can use more workers than CPU cores

### Async vs Sync
- **Async**: Better for I/O heavy operations (recommended)
- **Sync**: Simpler, good for CPU-bound tasks

## Architecture

### Plot Factory Pattern

```
utils/plots/plot_factory.py
├── MatchDataProcessor     # Shared data preprocessing
├── PlotFactory           # Centralized plot generation
├── generate_all_plots_async()  # Concurrent plot generation
└── generate_all_plots_sync()   # Sequential plot generation
```

### Optimized ETL Flow

```
1. Load matches in batches
2. For each batch:
   ├── Process matches concurrently
   ├── Share preprocessed data across plots
   ├── Generate all plots for each match
   └── Bulk update database
3. Progress tracking and error handling
```

## Files Created/Modified

### New Files
- `utils/plots/plot_factory.py` - Plot factory with shared preprocessing
- `data/etl/create_match_plots_optimized.py` - Optimized ETL script
- `data/etl/benchmark_etl.py` - Performance benchmarking
- `docs/ETL_OPTIMIZATION_GUIDE.md` - This guide

### Modified Files
- `utils/plots/match_plots/unified_heatmap.py` - Consolidated heatmap logic
- `utils/plots/match_plots/heatmap_per_game.py` - Wrapper function
- `utils/plots/match_plots/team_possesion_heatmap.py` - Wrapper function
- `data/etl/create_match_plots.py` - Fixed serialization issues
- `static/js/match_analysis.js` - Fixed button functionality

## Monitoring and Logging

The optimized ETL provides detailed logging:

```
🚀 Starting optimized processing of 50 matches...
📊 Configuration: batch_size=10, max_workers=4, async=True
📦 Processing batch 1/5 (10 matches)
⏱️  Batch 1 completed in 15.23s (1.52s/match)
📈 Progress: 20.0% (10 success, 0 failed)
...
🎉 ETL Complete!
⏱️  Total time: 75.45s
📊 Matches processed: 50/50
🚀 Average speed: 0.66 matches/second
```

## Troubleshooting

### Common Issues

1. **Memory errors**: Reduce batch_size or max_workers
2. **Database timeouts**: Reduce batch_size for smaller transactions
3. **API rate limits**: Reduce max_workers to avoid overwhelming StatsBomb API
4. **Import errors**: Ensure all dependencies are installed

### Performance Tuning

1. **Run benchmark**: `python data/etl/benchmark_etl.py`
2. **Monitor system resources**: CPU, memory, network usage
3. **Adjust configuration**: Based on benchmark results
4. **Test with small samples**: Before running full ETL

## Migration from Original ETL

The optimized ETL is a drop-in replacement:

```bash
# Old way
python data/etl/create_match_plots.py

# New way (recommended)
python data/etl/create_match_plots_optimized.py
```

Both produce identical results, but the optimized version is significantly faster and more robust.

## Future Enhancements

Potential further optimizations:

1. **Caching**: Cache StatsBomb API responses
2. **Database indexing**: Add indexes for faster queries
3. **Parallel databases**: Use read replicas for queries
4. **Plot compression**: Compress plot JSON data
5. **Incremental updates**: Only process new/changed matches
