# Phase 2: JavaScript Modularization Implementation Guide

## Step 1: Create New JavaScript Directory Structure

```bash
mkdir -p static/js/core
mkdir -p static/js/components
mkdir -p static/js/pages
mkdir -p static/js/services
```

## Step 2: Extract Core Modules

### A. App Configuration (static/js/core/config.js)
```javascript
// Application configuration constants
const AppConfig = {
    // API endpoints
    API: {
        MATCH_PLOTS: '/api/match-plots',
        COMPETITION_DATA: '/api/competition-data',
        TEAM_DATA: '/api/team-data'
    },
    
    // Plot types and their configurations
    PLOT_TYPES: {
        XG_GRAPH: 'xg_graph',
        MOMENTUM_GRAPH: 'momentum_graph',
        DOMINANCE_HEATMAP: 'dominance_heatmap',
        HOME_TEAM_STATS: 'home_team_stats',
        AWAY_TEAM_STATS: 'away_team_stats'
    },
    
    // UI constants
    UI: {
        LOADING_DELAY: 300,
        ANIMATION_DURATION: 200,
        DEBOUNCE_DELAY: 250
    },
    
    // Heatmap configurations
    HEATMAP: {
        PHASES: ['possession', 'attack', 'defense'],
        HALVES: ['full', 'first', 'second'],
        DEFAULT_PHASE: 'possession',
        DEFAULT_HALF: 'full'
    }
};

// Export for use in other modules
window.AppConfig = AppConfig;
```

### B. Utility Functions (static/js/core/utils.js)
```javascript
// Utility functions used across the application
const Utils = {
    /**
     * Debounce function calls
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Show loading state for an element
     */
    showLoading(elementId, message = 'Loading...') {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `<div class="loading-spinner">${message}</div>`;
        }
    },

    /**
     * Hide loading state
     */
    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            const spinner = element.querySelector('.loading-spinner');
            if (spinner) {
                spinner.remove();
            }
        }
    },

    /**
     * Safe JSON parse
     */
    safeJsonParse(jsonString, defaultValue = null) {
        try {
            return JSON.parse(jsonString);
        } catch (e) {
            console.warn('Failed to parse JSON:', e);
            return defaultValue;
        }
    },

    /**
     * Format numbers for display
     */
    formatNumber(num, decimals = 1) {
        if (typeof num !== 'number') return num;
        return num.toFixed(decimals);
    },

    /**
     * Get team color based on team type
     */
    getTeamColor(teamType) {
        const colors = {
            home: '#2196f3',
            away: '#f44336',
            home_team: '#2196f3',
            away_team: '#f44336'
        };
        return colors[teamType] || '#90caf9';
    }
};

window.Utils = Utils;
```

### C. Main App Initialization (static/js/core/app.js)
```javascript
// Main application initialization
class FootballDashboardApp {
    constructor() {
        this.currentPage = null;
        this.cachedPlots = null;
        this.components = {};
        this.services = {};
    }

    /**
     * Initialize the application
     */
    init() {
        console.log('Initializing Football Dashboard App...');
        
        // Initialize services
        this.services.api = new ApiService();
        this.services.cache = new CacheService();
        
        // Initialize components
        this.initializeComponents();
        
        // Set up global event listeners
        this.setupGlobalEvents();
        
        // Initialize page-specific logic
        this.initializePage();
        
        console.log('App initialized successfully');
    }

    /**
     * Initialize all components
     */
    initializeComponents() {
        // Navigation component
        if (typeof Navigation !== 'undefined') {
            this.components.navigation = new Navigation();
        }
        
        // Plot manager
        if (typeof PlotManager !== 'undefined') {
            this.components.plotManager = new PlotManager();
        }
        
        // Stats table component
        if (typeof StatsTable !== 'undefined') {
            this.components.statsTable = new StatsTable();
        }
        
        // Heatmap controls
        if (typeof HeatmapControls !== 'undefined') {
            this.components.heatmapControls = new HeatmapControls();
        }
    }

    /**
     * Set up global event listeners
     */
    setupGlobalEvents() {
        // Handle window resize
        window.addEventListener('resize', Utils.debounce(() => {
            this.handleResize();
        }, AppConfig.UI.DEBOUNCE_DELAY));
        
        // Handle dropdown changes
        $('.searchable-dropdown').on('change', (e) => {
            this.handleDropdownChange(e);
        });
    }

    /**
     * Initialize page-specific logic
     */
    initializePage() {
        const path = window.location.pathname;
        
        if (path.includes('match-analysis')) {
            this.currentPage = 'match-analysis';
            if (typeof MatchAnalysisPage !== 'undefined') {
                new MatchAnalysisPage().init();
            }
        } else if (path.includes('competition-analysis')) {
            this.currentPage = 'competition-analysis';
            if (typeof CompetitionAnalysisPage !== 'undefined') {
                new CompetitionAnalysisPage().init();
            }
        }
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Trigger resize on all Plotly plots
        if (window.Plotly) {
            $('.plotly-wrapper').each(function() {
                const plotDiv = this.querySelector('.js-plotly-plot');
                if (plotDiv) {
                    window.Plotly.Plots.resize(plotDiv);
                }
            });
        }
    }

    /**
     * Handle dropdown changes
     */
    handleDropdownChange(event) {
        const dropdown = event.target;
        const dropdownType = dropdown.id;
        
        console.log(`Dropdown changed: ${dropdownType} = ${dropdown.value}`);
        
        // Trigger page-specific handlers
        if (this.components.plotManager) {
            this.components.plotManager.handleDropdownChange(dropdownType, dropdown.value);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new FootballDashboardApp();
    window.app.init();
});
```

## Step 3: Create Component Modules

### A. Navigation Component (static/js/components/navigation.js)
```javascript
// Navigation component for tab switching and UI interactions
class Navigation {
    constructor() {
        this.currentTab = 'overview';
        this.setupEventListeners();
    }

    /**
     * Set up navigation event listeners
     */
    setupEventListeners() {
        // Tab switching
        $('.tab-btn').on('click', (e) => {
            this.switchTab(e.target.dataset.tab);
        });

        // Layout toggle
        $('#layout-toggle-checkbox').on('change', (e) => {
            this.toggleLayout(e.target.checked);
        });
    }

    /**
     * Switch between tabs
     */
    switchTab(tabName) {
        if (this.currentTab === tabName) return;

        console.log(`Switching to tab: ${tabName}`);

        // Update tab buttons
        $('.tab-btn').removeClass('active');
        $(`.tab-btn[data-tab="${tabName}"]`).addClass('active');

        // Hide all content
        $('.analysis-content').addClass('hidden');
        
        // Show selected content
        $(`#${tabName}`).removeClass('hidden');

        // Update current tab
        this.currentTab = tabName;

        // Trigger tab-specific logic
        this.onTabActivated(tabName);

        // Trigger resize for plots
        setTimeout(() => {
            if (window.app && window.app.handleResize) {
                window.app.handleResize();
            }
        }, AppConfig.UI.ANIMATION_DURATION);
    }

    /**
     * Handle tab activation
     */
    onTabActivated(tabName) {
        // Load team stats when team tabs are activated
        if (tabName === 'home' && window.app.components.statsTable) {
            window.app.components.statsTable.loadTeamStats('home_team');
        } else if (tabName === 'away' && window.app.components.statsTable) {
            window.app.components.statsTable.loadTeamStats('away_team');
        }

        // Show/hide relevant graph containers
        this.updateGraphVisibility(tabName);
    }

    /**
     * Update graph container visibility based on active tab
     */
    updateGraphVisibility(tabName) {
        $('.graph-container').addClass('hidden');

        switch (tabName) {
            case 'overview':
                $('#graph-container-xg, #graph-container-momentum, #graph-container-summary, #graph-container-heatmap').removeClass('hidden');
                break;
            case 'home':
                $('#graph-container-home-team-4').removeClass('hidden');
                break;
            case 'away':
                $('#graph-container-away-team-4').removeClass('hidden');
                break;
            case 'player':
                // Player-specific containers
                break;
        }
    }

    /**
     * Toggle between wide and compact layout
     */
    toggleLayout(isCompact) {
        $('.graphs-container').each(function() {
            $(this).toggleClass('compact-mode', isCompact);
            $(this).toggleClass('wide-mode', !isCompact);
        });
        
        $('.toggle-label').text(isCompact ? 'Wide Layout' : 'Compact Layout');
        
        // Trigger resize after layout change
        setTimeout(() => {
            if (window.app && window.app.handleResize) {
                window.app.handleResize();
            }
        }, AppConfig.UI.ANIMATION_DURATION);
    }

    /**
     * Get current active tab
     */
    getCurrentTab() {
        return this.currentTab;
    }
}

window.Navigation = Navigation;
```

### B. Stats Table Component (static/js/components/stats-table.js)
```javascript
// Team stats table component
class StatsTable {
    constructor() {
        this.highlightStats = ['Goals', 'Shots on Target', 'Passes', 'xG'];
    }

    /**
     * Populate team stats table
     */
    populateTeamStatsTable(teamPrefix, statsData) {
        const container = document.getElementById(`${teamPrefix}-stats-container`);
        
        if (!container) {
            console.error(`Stats container not found for ${teamPrefix}`);
            return;
        }
        
        if (!statsData || !statsData.team_stats || !statsData.team_stats.stats) {
            container.innerHTML = '<div class="stats-loading">No stats available</div>';
            return;
        }
        
        const stats = statsData.team_stats.stats;
        const teamName = statsData.team_stats.team_name;
        
        // Create table HTML
        let tableHTML = `<table class="team-stats-table"><tbody>`;
        
        stats.forEach(stat => {
            const isHighlight = this.highlightStats.includes(stat.stat_name);
            const rowClass = isHighlight ? 'highlight-stat' : '';
            
            tableHTML += `
                <tr class="${rowClass}">
                    <td class="stat-name">${stat.stat_name}</td>
                    <td class="stat-value">${stat.value}</td>
                </tr>
            `;
        });
        
        tableHTML += `</tbody></table>`;
        container.innerHTML = tableHTML;
    }

    /**
     * Load stats for a specific team
     */
    loadTeamStats(teamType) {
        if (!window.cachedPlots) {
            console.log('No cached plots available for team stats');
            return;
        }
        
        const statsKey = `${teamType}_stats`;
        if (window.cachedPlots[statsKey]) {
            this.populateTeamStatsTable(teamType, window.cachedPlots[statsKey]);
        } else {
            console.log(`${teamType} stats not available`);
            const container = document.getElementById(`${teamType}-stats-container`);
            if (container) {
                container.innerHTML = '<div class="stats-loading">Stats not available</div>';
            }
        }
    }

    /**
     * Load and display team stats for both teams
     */
    loadAllTeamStats() {
        this.loadTeamStats('home_team');
        this.loadTeamStats('away_team');
    }

    /**
     * Refresh stats tables
     */
    refresh() {
        this.loadAllTeamStats();
    }
}

window.StatsTable = StatsTable;
```

### C. Heatmap Controls Component (static/js/components/heatmap-controls.js)
```javascript
// Heatmap controls component for phase and half switching
class HeatmapControls {
    constructor() {
        this.currentPhase = AppConfig.HEATMAP.DEFAULT_PHASE;
        this.currentHalf = AppConfig.HEATMAP.DEFAULT_HALF;
        this.setupEventListeners();
    }

    /**
     * Set up event listeners for heatmap controls
     */
    setupEventListeners() {
        // Phase buttons
        $(document).on('click', '.phase-btn', (e) => {
            const phase = e.target.dataset.phase;
            const team = $(e.target).closest('.heatmap-controls-bar').data('team');
            this.switchPhase(team, phase);
        });

        // Half buttons
        $(document).on('click', '.toggle-btn[data-half]', (e) => {
            const half = e.target.dataset.half;
            const team = $(e.target).closest('.heatmap-controls-bar').data('team');
            this.switchHalf(team, half);
        });

        // Dominance heatmap buttons
        $(document).on('click', '.toggle-btn[data-view]', (e) => {
            const view = e.target.dataset.view;
            this.switchDominanceView(view);
        });
    }

    /**
     * Switch heatmap phase (possession/attack/defense)
     */
    switchPhase(team, phase) {
        if (!AppConfig.HEATMAP.PHASES.includes(phase)) {
            console.error(`Invalid phase: ${phase}`);
            return;
        }

        console.log(`Switching ${team} to phase: ${phase}`);

        // Update button states
        $(`.heatmap-controls-bar[data-team="${team}"] .phase-btn`).removeClass('active');
        $(`.heatmap-controls-bar[data-team="${team}"] .phase-btn[data-phase="${phase}"]`).addClass('active');

        // Update current phase
        this.currentPhase = phase;

        // Load the appropriate heatmap
        this.loadTeamHeatmap(team, phase, this.currentHalf);
    }

    /**
     * Switch heatmap half (full/first/second)
     */
    switchHalf(team, half) {
        if (!AppConfig.HEATMAP.HALVES.includes(half)) {
            console.error(`Invalid half: ${half}`);
            return;
        }

        console.log(`Switching ${team} to half: ${half}`);

        // Update button states
        $(`.heatmap-controls-bar[data-team="${team}"] .toggle-btn[data-half]`).removeClass('active');
        $(`.heatmap-controls-bar[data-team="${team}"] .toggle-btn[data-half="${half}"]`).addClass('active');

        // Update current half
        this.currentHalf = half;

        // Load the appropriate heatmap
        this.loadTeamHeatmap(team, this.currentPhase, half);
    }

    /**
     * Switch dominance heatmap view
     */
    switchDominanceView(view) {
        console.log(`Switching dominance view: ${view}`);

        // Update button states
        $('.dominance-toggle-buttons .toggle-btn').removeClass('active');
        $(`.dominance-toggle-buttons .toggle-btn[data-view="${view}"]`).addClass('active');

        // Load the dominance heatmap
        this.loadDominanceHeatmap(view);
    }

    /**
     * Load team heatmap
     */
    loadTeamHeatmap(team, phase, half) {
        if (!window.cachedPlots) {
            console.error('No cached plots available');
            return;
        }

        const plotKey = `${team}_${phase}_${half}`;
        const plotData = window.cachedPlots[plotKey];

        if (plotData) {
            const containerId = team === 'home_team' ? 'heatmap-home-plot-container' : 'heatmap-away-plot-container';
            this.renderPlot(containerId, plotData);
        } else {
            console.warn(`Plot data not found for: ${plotKey}`);
        }
    }

    /**
     * Load dominance heatmap
     */
    loadDominanceHeatmap(view) {
        if (!window.cachedPlots || !window.cachedPlots[view]) {
            console.error(`Dominance heatmap data not found: ${view}`);
            return;
        }

        this.renderPlot('dominance-plot-container', window.cachedPlots[view]);
    }

    /**
     * Render plot using Plotly
     */
    renderPlot(containerId, plotData) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Plot container not found: ${containerId}`);
            return;
        }

        if (window.Plotly) {
            window.Plotly.newPlot(container, plotData.data, plotData.layout, {
                responsive: true,
                displayModeBar: false
            });
        } else {
            console.error('Plotly not loaded');
        }
    }
}

window.HeatmapControls = HeatmapControls;
```

## Step 4: Create Service Modules

### A. API Service (static/js/services/api-service.js)
```javascript
// API service for handling server communication
class ApiService {
    constructor() {
        this.baseUrl = '';
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }

    /**
     * Make HTTP request
     */
    async request(url, options = {}) {
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        try {
            const response = await fetch(this.baseUrl + url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        
        return this.request(fullUrl, { method: 'GET' });
    }

    /**
     * POST request
     */
    async post(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * Fetch match plots
     */
    async fetchMatchPlots(matchId, competitionId, seasonId) {
        return this.get(AppConfig.API.MATCH_PLOTS, {
            match_id: matchId,
            competition_id: competitionId,
            season_id: seasonId
        });
    }

    /**
     * Fetch competition data
     */
    async fetchCompetitionData(competitionId) {
        return this.get(AppConfig.API.COMPETITION_DATA, {
            competition_id: competitionId
        });
    }
}

window.ApiService = ApiService;
```

## Step 5: Update HTML Templates

### Update base.html to load modular JavaScript:
```html
<!-- Core modules (load first) -->
<script src="{{ url_for('static', filename='js/core/config.js') }}"></script>
<script src="{{ url_for('static', filename='js/core/utils.js') }}"></script>

<!-- Services -->
<script src="{{ url_for('static', filename='js/services/api-service.js') }}"></script>
<script src="{{ url_for('static', filename='js/services/cache-service.js') }}"></script>

<!-- Components -->
<script src="{{ url_for('static', filename='js/components/navigation.js') }}"></script>
<script src="{{ url_for('static', filename='js/components/stats-table.js') }}"></script>
<script src="{{ url_for('static', filename='js/components/heatmap-controls.js') }}"></script>
<script src="{{ url_for('static', filename='js/components/plot-manager.js') }}"></script>

<!-- Page-specific scripts -->
{% block page_scripts %}{% endblock %}

<!-- Main app initialization (load last) -->
<script src="{{ url_for('static', filename='js/core/app.js') }}"></script>
```

## Benefits of This Modular Approach

1. **Maintainability**: Each component has a single responsibility
2. **Reusability**: Components can be used across different pages
3. **Testing**: Individual modules can be unit tested
4. **Performance**: Selective loading of only needed modules
5. **Debugging**: Easier to locate and fix issues
6. **Scalability**: Easy to add new features without affecting existing code

## Next Steps
- Migrate existing match_analysis.js logic to these modules
- Create page-specific modules for complex interactions
- Add error handling and loading states
- Implement caching service for better performance
