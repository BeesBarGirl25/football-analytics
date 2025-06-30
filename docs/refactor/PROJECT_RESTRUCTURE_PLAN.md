# Football Dashboard - Modular Restructure Plan

## Current Issues
- Large monolithic files (base.css ~500+ lines, match_analysis.js likely large)
- Mixed concerns in single files
- Difficult to maintain and extend
- Hard to debug specific features

## Proposed Modular Structure

### 1. Frontend Assets Restructure

#### CSS Modularization
```
static/css/
├── base.css                    # Core layout & variables only
├── components/
│   ├── navigation.css          # Sidebar, navbar, tabs
│   ├── graphs.css              # Graph containers, plotly wrappers
│   ├── tables.css              # All table styles
│   ├── controls.css            # Buttons, toggles, dropdowns
│   └── stats-sidebar.css       # Team stats sidebar
├── layouts/
│   ├── overview.css            # Overview tab layout
│   ├── team-analysis.css       # Team tab layouts
│   └── responsive.css          # All responsive breakpoints
└── themes/
    ├── dark-theme.css          # Dark theme variables
    └── light-theme.css         # Future light theme
```

#### JavaScript Modularization
```
static/js/
├── core/
│   ├── app.js                  # Main app initialization
│   ├── config.js               # Configuration constants
│   └── utils.js                # Utility functions
├── components/
│   ├── navigation.js           # Tab switching, sidebar
│   ├── dropdowns.js            # Existing dropdown logic
│   ├── plot-manager.js         # Plot loading & caching
│   ├── stats-table.js          # Team stats table logic
│   └── heatmap-controls.js     # Heatmap phase/half controls
├── pages/
│   ├── match-analysis.js       # Match analysis page logic
│   ├── competition-analysis.js # Competition page logic
│   └── team-analysis.js        # Team analysis page logic
└── services/
    ├── api-service.js          # API calls
    └── cache-service.js        # Data caching logic
```

### 2. Backend Modularization

#### Analytics Restructure
```
utils/analytics/
├── __init__.py
├── base/
│   ├── __init__.py
│   ├── base_analytics.py       # Base analytics class
│   └── data_processor.py       # Common data processing
├── match/
│   ├── __init__.py
│   ├── match_stats.py          # Team stats calculation
│   ├── player_stats.py         # Player-level analytics
│   └── match_events.py         # Event-based analytics
├── team/
│   ├── __init__.py
│   ├── team_performance.py     # Team performance metrics
│   └── team_comparison.py      # Team vs team analytics
└── competition/
    ├── __init__.py
    ├── season_stats.py         # Season-level analytics
    └── league_tables.py        # League table generation
```

#### Plots Restructure
```
utils/plots/
├── __init__.py
├── base/
│   ├── __init__.py
│   ├── base_plot.py            # Base plot class
│   ├── plot_config.py          # Plot configuration
│   └── plot_utils.py           # Common plot utilities
├── match/
│   ├── __init__.py
│   ├── heatmaps.py             # All heatmap types
│   ├── timeseries.py           # xG, momentum plots
│   └── summary.py              # Match summary plots
├── team/
│   ├── __init__.py
│   ├── performance_plots.py    # Team performance viz
│   └── comparison_plots.py     # Team comparison viz
├── player/
│   ├── __init__.py
│   └── player_plots.py         # Player visualization
└── factories/
    ├── __init__.py
    ├── match_factory.py        # Match plot factory
    ├── team_factory.py         # Team plot factory
    └── competition_factory.py  # Competition plot factory
```

### 3. Template Modularization

#### Component-Based Templates
```
templates/
├── base.html                   # Main layout
├── pages/
│   ├── match_analysis.html     # Match analysis page
│   ├── team_analysis.html      # Team analysis page
│   └── competition_analysis.html
├── components/
│   ├── navigation/
│   │   ├── sidebar.html        # Main sidebar
│   │   ├── top-navbar.html     # Top navigation
│   │   └── tab-navigation.html # Tab switching
│   ├── plots/
│   │   ├── plot-container.html # Generic plot container
│   │   ├── heatmap-controls.html # Heatmap controls
│   │   └── plot-loading.html   # Loading states
│   ├── tables/
│   │   ├── stats-table.html    # Team stats table
│   │   ├── player-table.html   # Player tables
│   │   └── summary-table.html  # Match summary
│   └── forms/
│       └── dropdowns.html      # Competition dropdowns
└── layouts/
    ├── overview-layout.html    # Overview tab layout
    ├── team-layout.html        # Team analysis layout
    └── comparison-layout.html  # Team comparison layout
```

### 4. Configuration & Settings

#### New Configuration Structure
```
config/
├── __init__.py
├── app_config.py               # Flask app configuration
├── plot_config.py              # Plot default settings
├── ui_config.py                # UI configuration
└── database_config.py          # Database settings
```

### 5. Feature Modules

#### Organized by Feature
```
features/
├── __init__.py
├── match_analysis/
│   ├── __init__.py
│   ├── routes.py               # Match analysis routes
│   ├── services.py             # Business logic
│   ├── models.py               # Data models
│   └── templates/              # Feature-specific templates
├── team_analysis/
│   ├── __init__.py
│   ├── routes.py
│   ├── services.py
│   └── templates/
└── competition_analysis/
    ├── __init__.py
    ├── routes.py
    ├── services.py
    └── templates/
```

## Implementation Benefits

### 1. **Maintainability**
- Single responsibility per file
- Easy to locate specific functionality
- Reduced merge conflicts

### 2. **Scalability**
- Easy to add new plot types
- Simple to extend analytics
- Modular feature development

### 3. **Performance**
- Selective loading of CSS/JS
- Better caching strategies
- Reduced bundle sizes

### 4. **Developer Experience**
- Clear file organization
- Easier debugging
- Better code reuse

### 5. **Testing**
- Unit test individual modules
- Mock specific components
- Isolated feature testing

## Migration Strategy

### Phase 1: CSS Modularization
1. Split base.css into component files
2. Create CSS build process
3. Update templates to load modular CSS

### Phase 2: JavaScript Modularization
1. Extract component logic from match_analysis.js
2. Create service layer for API calls
3. Implement module loading system

### Phase 3: Backend Restructure
1. Split analytics into feature modules
2. Refactor plot factory into specialized factories
3. Create base classes for common functionality

### Phase 4: Template Components
1. Extract reusable template components
2. Create layout templates
3. Implement component-based rendering

### Phase 5: Feature
