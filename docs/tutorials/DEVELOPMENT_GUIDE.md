# Football Dashboard Development Guide

This comprehensive guide covers everything you need to know about developing and extending the Football Dashboard application.

## 📚 Table of Contents

- [Getting Started](#getting-started)
- [Project Structure Deep Dive](#project-structure-deep-dive)
- [Adding New Features](#adding-new-features)
- [Frontend Development](#frontend-development)
- [Backend Development](#backend-development)
- [Database Operations](#database-operations)
- [Plot Development](#plot-development)
- [Testing and Debugging](#testing-and-debugging)
- [Best Practices](#best-practices)

## 🚀 Getting Started

### Development Environment Setup

```bash
# 1. Clone and setup
git clone <repository-url>
cd Football_Dashboard
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Environment configuration
cp .env.example .env  # Create from template
export FLASK_ENV=development
export FLASK_DEBUG=1

# 3. Database setup
python create_tables.py

# 4. Generate sample data (optional)
python data/etl/create_match_plots.py --sample

# 5. Run development server
python app.py
```

### Development Tools

**Recommended IDE Extensions:**
- Python (Microsoft)
- Pylance
- Flask Snippets
- JavaScript (ES6) code snippets
- CSS Peek
- Auto Rename Tag

**Browser Developer Tools:**
- Chrome DevTools / Firefox Developer Tools
- Vue.js devtools (if using Vue components)
- React Developer Tools (if using React components)

## 🏗️ Project Structure Deep Dive

### Backend Structure

```
├── app.py                    # Flask application entry point
├── models.py                 # SQLAlchemy database models
├── create_tables.py          # Database initialization script
├── routes/                   # Route handlers (controllers)
│   ├── __init__.py
│   ├── match_routes.py       # Match-related endpoints
│   └── competition_routes.py # Competition-related endpoints
├── utils/                    # Utility modules
│   ├── db.py                # Database utilities
│   ├── extensions.py        # Flask extensions setup
│   ├── statsbomb_utils.py   # StatsBomb API integration
│   ├── analytics/           # Analytics and calculations
│   │   └── match_analytics/
│   │       └── match_analysis_utils.py
│   └── plots/               # Plot generation modules
│       ├── plot_factory.py  # Plot factory pattern
│       └── match_plots/     # Match-specific plots
│           ├── unified_heatmap.py
│           ├── xG_per_game.py
│           └── momentum_per_game.py
└── data/                    # Data processing and ETL
    ├── xT_Grid.csv         # Expected Threat grid data
    └── etl/                # ETL scripts
        └── create_match_plots.py
```

### Frontend Structure

```
static/
├── css/                     # Stylesheets
│   ├── base.css            # Global styles and CSS variables
│   ├── components/         # Component-specific styles
│   │   ├── controls.css    # Form controls and buttons
│   │   ├── graphs.css      # Plot containers and styling
│   │   ├── navigation.css  # Navigation components
│   │   └── tables.css      # Table styling
│   └── layouts/            # Page layout styles
│       ├── overview.css    # Overview page layout
│       └── team-analysis.css # Team analysis layout
├── js/                     # JavaScript modules
│   ├── core/               # Core utilities
│   │   ├── app.js         # Main application initialization
│   │   ├── config.js      # Configuration constants
│   │   └── utils.js       # Utility functions
│   ├── components/         # UI components
│   │   ├── heatmap-controls.js # Heatmap control panel
│   │   ├── navigation.js   # Tab navigation
│   │   └── stats-table.js  # Statistics table
│   ├── pages/              # Page-specific controllers
│   │   ├── match-analysis.js
│   │   └── competition-analysis.js
│   └── services/           # Data services
│       ├── dropdown-service.js
│       └── plot-manager.js
└── images/                 # Static images
```

### Template Structure

```
templates/
├── base.html               # Base template with common layout
├── match_analysis.html     # Match analysis page
├── competition_analysis.html # Competition analysis page
└── partials/               # Reusable template components
    ├── competition_dropdowns.html
    └── match_team_analysis.html
```

## ➕ Adding New Features

### 1. Adding a New Plot Type

#### Step 1: Create Plot Generator

```python
# utils/plots/match_plots/new_plot_type.py
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_new_plot(match_data, home_team, away_team):
    """
    Create a new type of plot for match analysis
    
    Args:
        match_data (pd.DataFrame): Match event data
        home_team (str): Home team name
        away_team (str): Away team name
    
    Returns:
        dict: Plotly figure as JSON-serializable dict
    """
    
    # Process data for your specific plot
    processed_data = process_match_data(match_data)
    
    # Create Plotly figure
    fig = go.Figure()
    
    # Add traces for home team
    fig.add_trace(go.Scatter(
        x=processed_data['home']['x'],
        y=processed_data['home']['y'],
        name=home_team,
        line=dict(color='#28a745')
    ))
    
    # Add traces for away team
    fig.add_trace(go.Scatter(
        x=processed_data['away']['x'],
        y=processed_data['away']['y'],
        name=away_team,
        line=dict(color='#dc3545')
    ))
    
    # Update layout
    fig.update_layout(
        title="New Plot Type",
        xaxis_title="X Axis Label",
        yaxis_title="Y Axis Label",
        template="plotly_dark",
        height=400,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig.to_dict()

def process_match_data(match_data):
    """Process raw match data for the new plot"""
    # Your data processing logic here
    return {
        'home': {'x': [1, 2, 3], 'y': [1, 4, 2]},
        'away': {'x': [1, 2, 3], 'y': [2, 1, 3]}
    }
```

#### Step 2: Update ETL Process

```python
# data/etl/create_match_plots.py
from utils.plots.match_plots.new_plot_type import create_new_plot

def create_all_plots_for_match(match_id):
    # ... existing code ...
    
    # Add your new plot
    try:
        new_plot_data = create_new_plot(match_data, home_team, away_team)
        save_plot(match_id, 'new_plot_type', new_plot_data)
        print(f"✓ New plot type created for match {match_id}")
    except Exception as e:
        print(f"✗ Failed to create new plot type for match {match_id}: {e}")
```

#### Step 3: Add Frontend Component

```javascript
// static/js/components/new-plot.js
class NewPlot {
    constructor(plotManager) {
        this.plotManager = plotManager;
    }
    
    /**
     * Render the new plot type
     */
    async render(containerId, plotData) {
        try {
            const container = document.getElementById(containerId);
            if (!container) {
                throw new Error(`Container ${containerId} not found`);
            }
            
            // Configure Plotly
            const config = {
                responsive: true,
                displayModeBar: false,
                staticPlot: false
            };
            
            // Render plot
            await Plotly.newPlot(container, plotData.data, plotData.layout, config);
            
            Utils.log(`New plot rendered in ${containerId}`, 'NEW_PLOT');
            
        } catch (error) {
            Utils.log(`Failed to render new plot: ${error.message}`, 'NEW_PLOT', 'error');
            throw error;
        }
    }
    
    /**
     * Update plot with new data
     */
    async update(containerId, newData) {
        try {
            await Plotly.react(containerId, newData.data, newData.layout);
            Utils.log(`New plot updated in ${containerId}`, 'NEW_PLOT');
        } catch (error) {
            Utils.log(`Failed to update new plot: ${error.message}`, 'NEW_PLOT', 'error');
        }
    }
}

window.NewPlot = NewPlot;
```

#### Step 4: Integrate into Plot Manager

```javascript
// static/js/services/plot-manager.js
class PlotManager {
    constructor() {
        // ... existing code ...
        this.newPlot = new NewPlot(this);
    }
    
    async renderPlot(containerId, plotData, plotType) {
        switch (plotType) {
            // ... existing cases ...
            case 'new_plot_type':
                await this.newPlot.render(containerId, plotData);
                break;
            default:
                throw new Error(`Unknown plot type: ${plotType}`);
        }
    }
}
```

#### Step 5: Add HTML Container

```html
<!-- templates/match_analysis.html or relevant template -->
<div class="graph-container new-plot">
    <div class="graph-header">
        <h4>New Plot Type</h4>
    </div>
    <div class="graph-inner">
        <div id="new-plot-container" class="plot-container"></div>
    </div>
</div>
```

#### Step 6: Add CSS Styling

```css
/* static/css/components/graphs.css */
.graph-container.new-plot {
    /* Specific styling for your new plot */
    min-height: 400px;
}

.graph-container.new-plot .plot-container {
    height: 350px;
}
```

### 2. Adding a New Page

#### Step 1: Create Route Handler

```python
# routes/new_page_routes.py
from flask import Blueprint, render_template, jsonify
from models import Match, MatchPlot
import json

new_page_bp = Blueprint('new_page', __name__)

@new_page_bp.route('/new-page')
def new_page():
    """Render the new page"""
    return render_template('new_page.html')

@new_page_bp.route('/api/new-page/data')
def get_new_page_data():
    """API endpoint for new page data"""
    try:
        # Your data processing logic
        data = process_new_page_data()
        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def process_new_page_data():
    """Process data for the new page"""
    # Your logic here
    return {'example': 'data'}
```

#### Step 2: Register Blueprint

```python
# app.py
from routes.new_page_routes import new_page_bp

app.register_blueprint(new_page_bp)
```

#### Step 3: Create Template

```html
<!-- templates/new_page.html -->
{% extends "base.html" %}

{% block title %}New Page - Football Dashboard{% endblock %}

{% block content %}
<div class="container">
    <div class="page-header">
        <h1>New Page</h1>
        <p>Description of your new page</p>
    </div>
    
    <div class="new-page-content">
        <!-- Your page content here -->
        <div id="new-page-data-container">
            <div class="loading">Loading...</div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/pages/new-page.js') }}"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const newPage = new NewPage();
        newPage.initialize();
    });
</script>
{% endblock %}
```

#### Step 4: Create Page Controller

```javascript
// static/js/pages/new-page.js
class NewPage {
    constructor() {
        this.dataContainer = null;
    }
    
    /**
     * Initialize the new page
     */
    initialize() {
        this.dataContainer = document.getElementById('new-page-data-container');
        this.loadData();
        Utils.log('New page initialized', 'NEW_PAGE');
    }
    
    /**
     * Load data for the page
     */
    async loadData() {
        try {
            this.showLoading();
            
            const response = await fetch('/api/new-page/data');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            if (result.status === 'success') {
                this.renderData(result.data);
            } else {
                throw new Error(result.message);
            }
            
        } catch (error) {
            Utils.log(`Failed to load new page data: ${error.message}`, 'NEW_PAGE', 'error');
            this.showError(error.message);
        }
    }
    
    /**
     * Render data on the page
     */
    renderData(data) {
        if (!this.dataContainer) return;
        
        // Your rendering logic here
        this.dataContainer.innerHTML = `
            <div class="data-display">
                <h3>Data Loaded Successfully</h3>
                <pre>${JSON.stringify(data, null, 2)}</pre>
            </div>
        `;
        
        Utils.log('New page data rendered', 'NEW_PAGE');
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        if (this.dataContainer) {
            this.dataContainer.innerHTML = '<div class="loading">Loading...</div>';
        }
    }
    
    /**
     * Show error state
     */
    showError(message) {
        if (this.dataContainer) {
            this.dataContainer.innerHTML = `
                <div class="error">
                    <h3>Error Loading Data</h3>
                    <p>${message}</p>
                    <button onclick="location.reload()">Retry</button>
                </div>
            `;
        }
    }
}

window.NewPage = NewPage;
```

#### Step 5: Add Navigation Link

```html
<!-- templates/base.html -->
<nav class="main-nav">
    <ul>
        <li><a href="/">Match Analysis</a></li>
        <li><a href="/competition">Competition Analysis</a></li>
        <li><a href="/new-page">New Page</a></li>
    </ul>
</nav>
```

#### Step 6: Add CSS Styling

```css
/* static/css/layouts/new-page.css */
.new-page-content {
    padding: 2rem;
}

.data-display {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem;
}

.loading, .error {
    text-align: center;
    padding: 2rem;
}

.error {
    color: var(--error-color);
}

.error button {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background-color: var(--accent-blue);
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
```

## 🎨 Frontend Development

### Component Development Pattern

```javascript
// Component template
class ComponentName {
    constructor(dependencies) {
        this.dependency = dependencies;
        this.state = {};
        this.elements = {};
    }
    
    /**
     * Initialize component
     */
    initialize() {
        this.bindElements();
        this.attachEventListeners();
        this.loadInitialData();
        Utils.log('Component initialized', 'COMPONENT_NAME');
    }
    
    /**
     * Bind DOM elements
     */
    bindElements() {
        this.elements = {
            container: document.getElementById('component-container'),
            button: document.getElementById('component-button')
        };
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        if (this.elements.button) {
            this.elements.button.addEventListener('click', (e) => {
                this.handleButtonClick(e);
            });
        }
    }
    
    /**
     * Handle button click
     */
    handleButtonClick(event) {
        // Handle click logic
        Utils.log('Button clicked', 'COMPONENT_NAME');
    }
    
    /**
     * Load initial data
     */
    async loadInitialData() {
        try {
            // Load data logic
        } catch (error) {
            Utils.log(`Failed to load data: ${error.message}`, 'COMPONENT_NAME', 'error');
        }
    }
    
    /**
     * Update component state
     */
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.render();
    }
    
    /**
     * Render component
     */
    render() {
        if (!this.elements.container) return;
        
        // Render logic
        this.elements.container.innerHTML = this.getTemplate();
    }
    
    /**
     * Get component template
     */
    getTemplate() {
        return `
            <div class="component-content">
                <!-- Your template here -->
            </div>
        `;
    }
    
    /**
     * Cleanup component
     */
    destroy() {
        // Remove event listeners
        // Clear intervals/timeouts
        // Clean up resources
        Utils.log('Component destroyed', 'COMPONENT_NAME');
    }
}
```

### CSS Development Guidelines

```css
/* Component-based CSS structure */

/* 1. Component base styles */
.component-name {
    /* Base component styles */
    display: flex;
    flex-direction: column;
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem;
}

/* 2. Component variants */
.component-name.variant-large {
    padding: 2rem;
    font-size: 1.2em;
}

.component-name.variant-compact {
    padding: 0.5rem;
    font-size: 0.9em;
}

/* 3. Component states */
.component-name.loading {
    opacity: 0.6;
    pointer-events: none;
}

.component-name.error {
    border-color: var(--error-color);
    background-color: var(--error-bg);
}

/* 4. Component elements */
.component-name__header {
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-light);
}

.component-name__content {
    flex: 1;
}

.component-name__footer {
    margin-top: 1rem;
    padding-top: 0.5rem;
    border-top: 1px solid var(--border-light);
}

/* 5. Responsive design */
@media (max-width: 768px) {
    .component-name {
        padding: 0.5rem;
    }
    
    .component-name__header {
        font-size: 0.9em;
    }
}
```

## 🔧 Backend Development

### Route Handler Pattern

```python
# routes/example_routes.py
from flask import Blueprint, request, jsonify, render_template
from models import Match, MatchPlot, db
from utils.analytics.example_analytics import process_example_data
import json
import logging

example_bp = Blueprint('example', __name__)
logger = logging.getLogger(__name__)

@example_bp.route('/api/example')
def get_example_data():
    """
    Get example data with proper error handling
    """
    try:
        # Validate request parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if per_page > 100:
            return jsonify({
                'status': 'error',
                'message': 'per_page cannot exceed 100'
            }), 400
        
        # Process data
        data = process_example_data(page, per_page)
        
        # Log successful request
        logger.info(f"Example data requested: page={page}, per_page={per_page}")
        
        return jsonify({
            'status': 'success',
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(data)
            }
        })
        
    except ValueError as e:
        logger.warning(f"Invalid request parameters: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Invalid request parameters'
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in get_example_data: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@example_bp.route('/api/example/<int:item_id>')
def get_example_item(item_id):
    """
    Get specific example item
    """
    try:
        # Validate item_id
        if item_id <= 0:
            return jsonify({
                'status': 'error',
                'message': 'Invalid item ID'
            }), 400
        
        # Query database
        item = Match.query.get(item_id)
        if not item:
            return jsonify({
                'status': 'error',
                'message': 'Item not found'
            }), 404
        
        # Serialize data
        item_data = {
            'id': item.match_id,
            'home_team': item.home_team,
            'away_team': item.away_team,
            'match_date': item.match_date.isoformat() if item.match_date else None
        }
        
        return jsonify({
            'status': 'success',
            'data': item_data
        })
        
    except Exception as e:
        logger.error(f"Error getting example item {item_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@example_bp.route('/api/example', methods=['POST'])
def create_example_item():
    """
    Create new example item
    """
    try:
        # Validate request data
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        required_fields = ['name', 'type']
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create new item
        new_item = create_new_example_item(data)
        
        return jsonify({
            'status': 'success',
            'data': new_item,
            'message': 'Item created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating example item: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

def create_new_example_item(data):
    """Helper function to create new item"""
    # Implementation here
    pass
```

### Database Model Pattern

```python
# models.py
from utils.extensions import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

class ExampleModel(db.Model):
    """
    Example model with common patterns
    """
    __tablename__ = 'example'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Required fields
    name = db.Column(db.String(100), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)
    
    # Optional fields
    description = db.Column(db.Text)
    value = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'))
    
    # Relationships
    parent = db.relationship('Parent', backref='examples')
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('name', 'type', name='unique_name_type'),
        db.CheckConstraint('value >= 0', name='positive_value'),
    )
    
    def __repr__(self):
        return f'<ExampleModel {self.name}>'
    
    @hybrid_property
    def display_name(self):
        """Computed property for display"""
        return f"{self.name} ({self.type})"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'value': self.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_active(cls):
        """Get all active records"""
        return cls.query.filter_by(is_active=True).all()
    
    @classmethod
    def find_by_name(cls, name):
        """Find record by name"""
        return cls.query.filter_by(name=name).first()
    
    def update(self, **kwargs):
        """Update model with keyword arguments"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def delete(self):
        """Soft delete by setting is_active to False"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
        db.session.commit()
```

## 🧪 Testing and Debugging

### Frontend Debugging

```javascript
// Debug utilities
class DebugUtils {
    static enableDebugMode() {
        window.DEBUG_MODE = true;
        console.log('Debug mode enabled');
    }
    
    static logState(component, state) {
        if (window.DEBUG_MODE) {
            console.group(`${component} State`);
            console.table(state);
            console.groupEnd();
        }
    }
    
    static logPerformance(label, fn) {
        if (window.DEBUG_MODE) {
            console.time(label);
            const result = fn();
            console.timeEnd(label);
            return result;
        }
        return fn();
    }
    
    static inspectElement(selector) {
        const element = document.querySelector(selector);
        if (element) {
            console.log('Element:', element);
            console.log('Computed styles:', getComputedStyle(element));
            console.log('Event listeners:', getEventListeners(element));
        }
    }
}

// Usage in components
class MyComponent {
    setState(newState) {
        this.state = { ...this.state, ...newState };
        DebugUtils.logState('MyComponent', this.state);
        this.render();
    }
    
    performExpensiveOperation() {
        return DebugUtils.logPerformance('Expensive Operation', () => {
            // Your expensive operation here
            return result;
        });
    }
}
```

### Backend Testing

```python
# tests/test_routes.py
import unittest
import json
from app import app, db
from models import Match

class RouteTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test data
        self.create_test_data()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def create_test_data(self):
        """Create test data"""
        match = Match(
            match_id=12345,
            home_team='Test Home',
            away_team='Test Away',
            home_score=2,
            away_score=1
        )
        db.session.add(match)
        db.session.commit()
    
    def test_get_matches(self):
        """Test getting all matches"""
        response = self.app.get('/api/matches')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
    
    def test_get_match_plots(self):
        """Test getting match plots"""
        response = self.app.get('/api/matches/12345/plots')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('match_summary', data)
    
    def test_invalid_match_id(self):
        """Test invalid match ID"""
        response = self.app.get('/api/matches/99999/plots')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')

if __name__ == '__main__':
    unittest.main()
```

## 📋 Best Practices

### Code Organization

1. **Separation of Concerns**: Keep business logic separate from presentation
2. **Single Responsibility**: Each function/class should have one clear purpose
3. **DRY Principle**: Don't repeat yourself - create reusable components
4. **Consistent
