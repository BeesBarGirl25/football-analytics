// Application configuration constants
const AppConfig = {
    // API endpoints
    API: {
        MATCH_PLOTS: '/api/plots',
        COMPETITION_DATA: '/api/competition-data',
        TEAM_DATA: '/api/team-data'
    },
    
    // Plot types and their configurations
    PLOT_TYPES: {
        XG_GRAPH: 'xg_graph',
        MOMENTUM_GRAPH: 'momentum_graph',
        RADAR_CHART: 'radar_chart',
        DOMINANCE_HEATMAP: 'dominance_heatmap',
        HOME_TEAM_STATS: 'home_team_stats',
        AWAY_TEAM_STATS: 'away_team_stats'
    },
    
    // UI constants
    UI: {
        LOADING_DELAY: 300,
        ANIMATION_DURATION: 200,
        DEBOUNCE_DELAY: 250,
        PLOT_RENDER_DELAY: 100,
        TAB_SWITCH_DELAY: 20
    },
    
    // Heatmap configurations
    HEATMAP: {
        PHASES: ['possession', 'attack', 'defense'],
        HALVES: ['full', 'first', 'second'],
        DEFAULT_PHASE: 'possession',
        DEFAULT_HALF: 'full'
    },
    
    // Team configurations
    TEAMS: {
        HOME: 'home_team',
        AWAY: 'away_team'
    },
    
    // Container IDs
    CONTAINERS: {
        XG_PLOT: 'xg-plot-container',
        MOMENTUM_PLOT: 'momentum-plot-container',
        RADAR_PLOT: 'radar-plot-container',
        DOMINANCE_PLOT: 'dominance-plot-container',
        HEATMAP_HOME: 'heatmap-home-plot-container',
        HEATMAP_AWAY: 'heatmap-away-plot-container'
    },
    
    // Dropdown configurations
    DROPDOWNS: {
        AUTO_SELECT_DEFAULTS: true,    // Auto-select first available options
        SELECTION_DELAY: 100           // Delay between auto-selections (ms)
    }
};

// Export for use in other modules
window.AppConfig = AppConfig;
