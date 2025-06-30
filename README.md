# Football Dashboard

A comprehensive football analytics dashboard built with Flask, featuring match analysis, team statistics, and interactive visualizations using StatsBomb data.

## 🏆 Features

- **Match Analysis**: Detailed match breakdowns with xG graphs, momentum tracking, and heatmaps
- **Team Statistics**: Comprehensive team performance metrics and comparisons
- **Interactive Heatmaps**: Possession, attack, and defense heatmaps with half-time filtering
- **Player Analysis**: Individual player contributions and statistics
- **Competition Overview**: Season-wide analytics and trends
- **Responsive Design**: Works seamlessly across desktop, tablet, and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (for production) or SQLite (for development)
- Node.js (optional, for frontend development)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Football_Dashboard
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database**
   ```bash
   python create_tables.py
   ```

5. **Generate plot data**
   ```bash
   python data/etl/create_match_plots.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Open browser**
   Navigate to `http://localhost:5000`

## 📁 Project Structure

```
Football_Dashboard/
├── app.py                          # Main Flask application
├── models.py                       # Database models
├── create_tables.py               # Database initialization
├── requirements.txt               # Python dependencies
├── Procfile                       # Heroku deployment config
│
├── data/                          # Data processing and ETL
│   ├── xT_Grid.csv               # Expected Threat grid data
│   └── etl/                      # ETL scripts
│       ├── create_match_plots.py # Main plot generation
│       ├── benchmark_etl.py      # Performance testing
│       └── competition_season_matches.py
│
├── docs/                          # Documentation
│   ├── README.md                 # This file
│   ├── ARCHITECTURE.md           # System architecture
│   ├── API.md                    # API documentation
│   ├── DEPLOYMENT.md             # Deployment guide
│   └── tutorials/                # Step-by-step guides
│
├── routes/                        # Flask route handlers
│   ├── competition_routes.py     # Competition endpoints
│   └── match_routes.py           # Match analysis endpoints
│
├── static/                        # Frontend assets
│   ├── css/                      # Stylesheets
│   │   ├── base.css             # Global styles
│   │   ├── components/          # Component-specific styles
│   │   └── layouts/             # Page layout styles
│   ├── js/                       # JavaScript
│   │   ├── core/                # Core utilities
│   │   ├── components/          # UI components
│   │   ├── pages/               # Page-specific logic
│   │   └── services/            # Data services
│   └── images/                   # Static images
│
├── templates/                     # Jinja2 templates
│   ├── base.html                # Base template
│   ├── match_analysis.html      # Match analysis page
│   ├── competition_analysis.html # Competition page
│   └── partials/                # Reusable template parts
│
└── utils/                         # Utility modules
    ├── db.py                     # Database utilities
    ├── extensions.py             # Flask extensions
    ├── statsbomb_utils.py        # StatsBomb API utilities
    ├── analytics/                # Analytics functions
    └── plots/                    # Plot generation
```

## 🔧 Core Components

### Backend (Flask)

- **Flask Application** (`app.py`): Main application with route registration
- **Database Models** (`models.py`): SQLAlchemy models for data persistence
- **Route Handlers** (`routes/`): API endpoints for different features
- **Analytics Engine** (`utils/analytics/`): Statistical calculations and data processing
- **Plot Generation** (`utils/plots/`): Plotly-based visualization creation

### Frontend (JavaScript/CSS)

- **Modular Architecture**: Component-based JavaScript with clear separation of concerns
- **Responsive Design**: CSS Grid and Flexbox for adaptive layouts
- **Interactive Components**: Dynamic plot updates, filtering, and navigation
- **Service Layer**: Centralized data fetching and state management

### Data Pipeline

- **ETL Process**: Automated data extraction, transformation, and loading
- **StatsBomb Integration**: Direct API integration for match data
- **Plot Caching**: Pre-generated plots stored in database for performance
- **Data Validation**: Comprehensive error handling and data quality checks

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and component interactions
- **[API Documentation](docs/API.md)** - Complete API reference
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Development Tutorials](docs/tutorials/)** - Step-by-step development guides

## 🛠️ Development

### Adding New Features

1. **Backend**: Add routes in `routes/`, models in `models.py`, analytics in `utils/analytics/`
2. **Frontend**: Create components in `static/js/components/`, styles in `static/css/`
3. **Templates**: Add HTML templates in `templates/`
4. **Documentation**: Update relevant docs in `docs/`

### Code Style

- **Python**: Follow PEP 8, use type hints where appropriate
- **JavaScript**: ES6+ features, modular design, comprehensive logging
- **CSS**: BEM methodology, CSS custom properties, mobile-first approach
- **HTML**: Semantic markup, accessibility considerations

### Testing

```bash
# Run ETL performance tests
python data/etl/benchmark_etl.py

# Test plot generation
python data/etl/create_match_plots.py --test

# Validate database integrity
python create_tables.py --validate
```

## 🚀 Deployment

### Local Development

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### Production (Heroku)

```bash
git push heroku main
heroku run python create_tables.py
heroku run python data/etl/create_match_plots.py
```

See [Deployment Guide](docs/DEPLOYMENT.md) for detailed instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **StatsBomb** for providing comprehensive football data
- **Plotly** for interactive visualization capabilities
- **Flask** community for excellent documentation and examples

## 📞 Support

For questions, issues, or contributions:

1. Check existing [Issues](../../issues)
2. Review [Documentation](docs/)
3. Create a new issue with detailed description

---

**Built with ⚽ and 💻 for football analytics enthusiasts**
