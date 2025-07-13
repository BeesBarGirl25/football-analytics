# Football Dashboard Architecture

This document provides a comprehensive overview of the Football Dashboard's system architecture, design patterns, and component interactions.

## 🏗️ System Overview

The Football Dashboard follows a **Model-View-Controller (MVC)** architecture with a **component-based frontend** and **service-oriented backend**.

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                       │
├─────────────────────────────────────────────────────────────┤
│  Browser (HTML/CSS/JavaScript)                             │
│  ├── Pages (match-analysis.js, competition-analysis.js)    │
│  ├── Components (navigation.js, stats-table.js)           │
│  ├── Services (plot-manager.js, dropdown-service.js)      │
│  └── Core (utils.js, config.js, app.js)                   │
└─────────────────────────────────────────────────────────────┘
                              │ HTTP/AJAX
┌─────────────────────────────────────────────────────────────┐
│                        Backend Layer                        │
├─────────────────────────────────────────────────────────────┤
│  Flask Application (app.py)                                │
│  ├── Routes (match_routes.py, competition_routes.py)       │
│  ├── Models (models.py)                                    │
│  ├── Analytics (match_analysis_utils.py)                   │
│  └── Plot Generation (unified_heatmap.py, xG_per_game.py)  │
└─────────────────────────────────────────────────────────────┘
                              │ SQL/ORM
┌─────────────────────────────────────────────────────────────┐
│                        Data Layer                           │
├─────────────────────────────────────────────────────────────┤
│  Database (PostgreSQL/SQLite)                              │
│  ├── Matches Table                                         │
│  ├── MatchPlots Table (Cached Visualizations)              │
│  └── Competitions Table                                     │
└─────────────────────────────────────────────────────────────┘
                              │ API Calls
┌─────────────────────────────────────────────────────────────┐
│                      External Data                          │
├─────────────────────────────────────────────────────────────┤
│  StatsBomb API                                              │
│  ├── Match Events                                          │
│  ├── Competition Data                                       │
│  └── Player Statistics                                      │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Design Principles

### 1. **Separation of Concerns**
- **Frontend**: Pure presentation and user interaction
- **Backend**: Business logic and data processing
- **Database**: Data persistence and retrieval
- **ETL**: Data transformation and plot generation

### 2. **Component-Based Architecture**
- **Modular JavaScript**: Each component handles specific functionality
- **Reusable CSS**: Component-specific styles with global utilities
- **Template Partials**: Reusable HTML components

### 3. **Performance Optimization**
- **Plot Caching**: Pre-generated plots stored in database
- **Lazy Loading**: Components loaded on demand
- **Efficient Queries**: Optimized database access patterns

### 4. **Scalability**
- **Stateless Backend**: Easy horizontal scaling
- **Database Abstraction**: SQLAlchemy ORM for database independence
- **Modular Frontend**: Easy to extend with new features

## 🔧 Backend Architecture

### Flask Application Structure

```python
# app.py - Main application entry point
from flask import Flask
from utils.extensions import db, cache
from routes.match_routes import match_bp
from routes.competition_routes import competition_bp

app = Flask(__name__)
app.register_blueprint(match_bp)
app.register_blueprint(competition_bp)
```

### Database Models

```python
# models.py - SQLAlchemy models
class Match(db.Model):
    """Core match data"""
    match_id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.String(100))
    away_team = db.Column(db.String(100))
    # ... other fields

class MatchPlot(db.Model):
    """Cached plot data for performance"""
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.match_id'))
    plot_type = db.Column(db.String(50))
    plot_json = db.Column(db.Text)  # Serialized plot data
```

### Route Handlers

```python
# routes/match_routes.py - Match-specific endpoints
@match_bp.route('/api/matches/<int:match_id>/plots')
def get_match_plots(match_id):
    """Return all plots for a specific match"""
    plots = MatchPlot.query.filter_by(match_id=match_id).all()
    return jsonify({plot.plot_type: json.loads(plot.plot_json) 
                   for plot in plots})
```

### Analytics Engine

```python
# utils/analytics/match_analytics/match_analysis_utils.py
def generate_team_stats(team_data: pd.DataFrame, team_name: str):
    """Generate comprehensive team statistics"""
    stats = []
    
    # Goals calculation
    goals = len(team_data[(team_data['type'] == 'Shot') & 
                         (team_data['shot_outcome'] == 'Goal')])
    stats.append({"stat_name": "Goals", "value": goals})
    
    # ... other statistics
    
    return {"team_stats": {"team_name": team_name, "stats": stats}}
```

## 🎨 Frontend Architecture

### Component System

```javascript
// static/js/components/stats-table.js
class StatsTable {
    constructor() {
        this.highlightStats = ['Goals', 'Shots on Target', 'Passes', 'xG'];
    }
    
    populateTeamStatsTable(teamPrefix, statsData) {
        // Render team statistics table
    }
    
    loadTeamStats(teamType) {
        // Load and display team stats
    }
}
```

### Page Controllers

```javascript
// static/js/pages/match-analysis.js
class MatchAnalysisPage {
    constructor() {
        this.plotManager = new PlotManager();
        this.navigation = new Navigation(this.plotManager);
        this.heatmapControls = new HeatmapControls(this.plotManager);
        this.statsTable = new StatsTable();
    }
    
    async handleMatchSelection(matchId) {
        // Coordinate all components for match loading
    }
}
```

### Service Layer

```javascript
// static/js/services/plot-manager.js
class PlotManager {
    constructor() {
        this.cachedPlots = {};
        this.activeContainers = new Set();
    }
    
    async renderPlot(containerId, plotData, plotType) {
        // Handle plot rendering with error handling
    }
    
    cachePlots(plotData) {
        // Cache plot data for performance
    }
}
```

## 📊 Data Flow

### 1. **ETL Process**

```
StatsBomb API → Raw Match Data → Analytics Processing → Plot Generation → Database Storage
```

```python
# data/etl/create_match_plots.py
def create_all_match_plots():
    matches = get_matches_from_api()
    for match in matches:
        # Process match data
        match_data = fetch_match_events(match.match_id)
        
        # Generate analytics
        home_stats = generate_team_stats(home_team_data, home_team)
        away_stats = generate_team_stats(away_team_data, away_team)
        
        # Create visualizations
        xg_plot = create_xg_plot(match_data)
        heatmap = create_heatmap(match_data)
        
        # Store in database
        save_plots_to_db(match.match_id, plots)
```

### 2. **Request Flow**

```
User Interaction → Frontend Component → AJAX Request → Flask Route → Database Query → JSON Response → Frontend Update
```

```javascript
// Frontend request flow
async handleMatchSelection(matchId) {
    // 1. User selects match
    const response = await fetch(`/api/matches/${matchId}/plots`);
    
    // 2. Receive plot data
    const plotData = await response.json();
    
    // 3. Update components
    this.plotManager.cachePlots(plotData);
    this.statsTable.loadAllTeamStats();
    this.updateMatchSummary(plotData.match_summary);
}
```

### 3. **Plot Rendering Flow**

```
Cached Plot Data → Plotly Configuration → DOM Manipulation → Interactive Visualization
```

```javascript
// Plot rendering process
async renderPlot(containerId, plotData, plotType) {
    const container = document.getElementById(containerId);
    
    // Configure Plotly
    const config = {
        responsive: true,
        displayModeBar: false,
        staticPlot: false
    };
    
    // Render plot
    await Plotly.newPlot(container, plotData.data, plotData.layout, config);
}
```

## 🗄️ Database Design

### Core Tables

```sql
-- Matches table
CREATE TABLE match (
    match_id INTEGER PRIMARY KEY,
    competition_id INTEGER,
    season_id INTEGER,
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    match_date DATE,
    home_score INTEGER,
    away_score INTEGER
);

-- Cached plots table
CREATE TABLE match_plot (
    id INTEGER PRIMARY KEY,
    match_id INTEGER REFERENCES match(match_id),
    plot_type VARCHAR(50),
    plot_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Competitions table
CREATE TABLE competition (
    competition_id INTEGER PRIMARY KEY,
    competition_name VARCHAR(100),
    country_name VARCHAR(100),
    season_name VARCHAR(50)
);
```

### Indexing Strategy

```sql
-- Performance indexes
CREATE INDEX idx_match_plot_match_id ON match_plot(match_id);
CREATE INDEX idx_match_plot_type ON match_plot(plot_type);
CREATE INDEX idx_match_competition ON match(competition_id);
CREATE INDEX idx_match_date ON match(match_date);
```

## 🎨 CSS Architecture

### Component-Based Styling

```css
/* static/css/components/graphs.css */
.graph-container {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    /* Base graph container styles */
}

.graph-container.summary {
    /* Summary-specific styles */
}

.graph-container.heatmap {
    /* Heatmap-specific styles */
}
```

### Layout System

```css
/* static/css/layouts/overview.css */
.graphs-container.wide-mode {
    display: grid;
    grid-template-columns: 1fr 2fr 2fr;
    grid-template-rows: 1fr 1fr;
    grid-template-areas:
        "momentum summary heatmap"
        "xg       summary heatmap";
}
```

### CSS Custom Properties

```css
/* static/css/base.css */
:root {
    --bg-primary: #1a1a1a;
    --bg-secondary: #2d2d2d;
    --text-primary: #ffffff;
    --accent-blue: #007bff;
    --accent-home: #28a745;
    --accent-away: #dc3545;
}
```

## 🔄 State Management

### Frontend State

```javascript
// Global state management
window.cachedPlots = {};           // Plot data cache
window.currentMatchId = null;      // Active match
window.activeTab = 'overview';     // Current view
window.heatmapSettings = {         // Heatmap configuration
    half: 'full',
    phase: 'possession'
};
```

### Backend State

```python
# Flask application context
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

# Database connection pooling
db.engine.pool_size = 10
db.engine.max_overflow = 20
```

## 🚀 Performance Optimizations

### 1. **Database Optimizations**
- **Plot Caching**: Pre-generated plots stored as JSON
- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Indexed lookups and efficient joins

### 2. **Frontend Optimizations**
- **Lazy Loading**: Components loaded on demand
- **Plot Reuse**: Cached plot data prevents regeneration
- **Efficient DOM Updates**: Minimal DOM manipulation

### 3. **Network Optimizations**
- **JSON Compression**: Gzipped API responses
- **Static Asset Caching**: Browser caching for CSS/JS
- **CDN Integration**: External library delivery

## 🔒 Security Considerations

### 1. **Input Validation**
```python
# Route parameter validation
@match_bp.route('/api/matches/<int:match_id>/plots')
def get_match_plots(match_id):
    if not isinstance(match_id, int) or match_id <= 0:
        abort(400, 'Invalid match ID')
```

### 2. **SQL Injection Prevention**
```python
# SQLAlchemy ORM prevents SQL injection
plots = MatchPlot.query.filter_by(match_id=match_id).all()
```

### 3. **XSS Prevention**
```javascript
// Sanitize user input
const sanitizeInput = (input) => {
    return input.replace(/[<>]/g, '');
};
```

## 📈 Monitoring and Logging

### Backend Logging

```python
# utils/analytics/match_analytics/match_analysis_utils.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_team_stats(team_data, team_name):
    logger.info(f"Generating stats for {team_name}")
    # ... processing
    logger.info(f"Generated {len(stats)} stats for {team_name}")
```

### Frontend Logging

```javascript
// static/js/core/utils.js
class Utils {
    static log(message, component = 'GENERAL', level = 'info') {
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] [${component}] ${message}`;
        
        if (level === 'error') {
            console.error(logMessage);
        } else if (level === 'warn') {
            console.warn(logMessage);
        } else {
            console.log(logMessage);
        }
    }
}
```

## 🔧 Extension Points

### Adding New Plot Types

1. **Create Plot Generator**
```python
# utils/plots/match_plots/new_plot.py
def create_new_plot(match_data, home_team, away_team):
    # Plot generation logic
    return plot_json
```

2. **Update ETL Process**
```python
# data/etl/create_match_plots.py
new_plot = create_new_plot(match_data, home_team, away_team)
save_plot(match_id, 'new_plot', new_plot)
```

3. **Add Frontend Component**
```javascript
// static/js/components/new-plot.js
class NewPlot {
    render(containerId, plotData) {
        // Rendering logic
    }
}
```

### Adding New Pages

1. **Create Route Handler**
```python
# routes/new_routes.py
@new_bp.route('/new-page')
def new_page():
    return render_template('new_page.html')
```

2. **Create Template**
```html
<!-- templates/new_page.html -->
{% extends "base.html" %}
{% block content %}
<!-- Page content -->
{% endblock %}
```

3. **Add Page Controller**
```javascript
// static/js/pages/new-page.js
class NewPage {
    initialize() {
        // Page initialization
    }
}
```

This architecture provides a solid foundation for extending the Football Dashboard with new features while maintaining code quality, performance, and maintainability.
