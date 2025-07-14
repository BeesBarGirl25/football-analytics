// Plot management service for handling Plotly plots
class PlotManager {
    constructor() {
        this.cachedPlots = {};
        this.renderedPlots = new Set();
        this.teamHeatmapState = {
            home_team: { phase: 'possession', half: 'full' },
            away_team: { phase: 'possession', half: 'full' }
        };
    }

    /**
     * Cache plot data
     */
    cachePlots(plotData) {
        Object.assign(this.cachedPlots, plotData);
        
        // Ensure backward compatibility keys are available
        Object.assign(this.cachedPlots, {
            dominance_heatmap: plotData.dominance_heatmap,
            dominance_heatmap_first: plotData.dominance_heatmap_first,
            dominance_heatmap_second: plotData.dominance_heatmap_second,
            home_team_heatmap: plotData.home_team_heatmap,
            home_team_heatmap_first: plotData.home_team_heatmap_first,
            home_team_heatmap_second: plotData.home_team_heatmap_second,
            away_team_heatmap: plotData.away_team_heatmap,
            away_team_heatmap_first: plotData.away_team_heatmap_first,
            away_team_heatmap_second: plotData.away_team_heatmap_second
        });

        Utils.log('Plot data cached successfully', 'PLOT_MANAGER');
        
        // Make cached plots globally available for backward compatibility
        window.cachedPlots = this.cachedPlots;
    }

    /**
     * Clear all cached plots and rendered state
     */
    clearCache() {
        this.cachedPlots = {};
        this.renderedPlots.clear();
        window.cachedPlots = {};
        Utils.log('Plot cache cleared', 'PLOT_MANAGER');
    }

    /**
     * Lazy render plot with visibility check
     */
    lazyRenderPlot(containerId, plotKey, force = false) {
        const el = document.getElementById(containerId);
        const plot = this.cachedPlots[plotKey];

        if (!el || (!force && this.renderedPlots.has(containerId))) {
            return;
        }

        if (!plot) {
            Utils.log(`Plot data missing for ${plotKey}`, 'PLOT_MANAGER', 'error');
            return;
        }

        setTimeout(() => {
            if (!Utils.isElementVisible(el)) {
                Utils.log(`${containerId} not visible yet. Skipping render.`, 'PLOT_MANAGER', 'warn');
                return;
            }

            try {
                if (window.Plotly) {
                    window.Plotly.newPlot(containerId, plot.data, plot.layout, {
                        responsive: true,
                        displayModeBar: false
                    });
                    this.renderedPlots.add(containerId);
                    Utils.log(`✅ ${containerId} (${plotKey})`, 'LAZY_PLOT');
                } else {
                    Utils.log('Plotly not available', 'PLOT_MANAGER', 'error');
                }
            } catch (err) {
                Utils.log(`❌ Failed for ${containerId}: ${err.message}`, 'LAZY_PLOT', 'error');
            }
        }, AppConfig.UI.PLOT_RENDER_DELAY);
    }

    /**
     * Render main plots (XG, Momentum, and Radar)
     */
    renderMainPlots() {
        const xgPlot = this.cachedPlots[AppConfig.PLOT_TYPES.XG_GRAPH];
        const momentumPlot = this.cachedPlots[AppConfig.PLOT_TYPES.MOMENTUM_GRAPH];
        const radarPlot = this.cachedPlots[AppConfig.PLOT_TYPES.RADAR_CHART];

        if (xgPlot?.data && xgPlot?.layout && window.Plotly) {
            window.Plotly.newPlot(AppConfig.CONTAINERS.XG_PLOT, xgPlot.data, xgPlot.layout, {
                responsive: true,
                displayModeBar: false
            });
            Utils.log('XG plot rendered', 'PLOT_MANAGER');
        }

        if (momentumPlot?.data && momentumPlot?.layout && window.Plotly) {
            window.Plotly.newPlot(AppConfig.CONTAINERS.MOMENTUM_PLOT, momentumPlot.data, momentumPlot.layout, {
                responsive: true,
                displayModeBar: false
            });
            Utils.log('Momentum plot rendered', 'PLOT_MANAGER');
        }

        if (radarPlot?.data && radarPlot?.layout && window.Plotly) {
            window.Plotly.newPlot(AppConfig.CONTAINERS.RADAR_PLOT, radarPlot.data, radarPlot.layout, {
                responsive: true,
                displayModeBar: false
            });
            Utils.log('Radar plot rendered', 'PLOT_MANAGER');
        }
    }

    /**
     * Render current team heatmap based on state
     */
    renderCurrentTeamHeatmap(teamPrefix) {
        const state = this.teamHeatmapState[teamPrefix];
        const plotKey = `${teamPrefix}_${state.phase}_${state.half}`;
        
        // Determine container ID based on team
        const containerId = teamPrefix === AppConfig.TEAMS.HOME ? 
            AppConfig.CONTAINERS.HEATMAP_HOME : 
            AppConfig.CONTAINERS.HEATMAP_AWAY;
        
        // Check if plot data exists
        if (!this.cachedPlots[plotKey]) {
            Utils.log(`Plot data missing for ${plotKey}`, 'TEAM_HEATMAP', 'error');
            Utils.log(`Available plots: ${Object.keys(this.cachedPlots).join(', ')}`, 'TEAM_HEATMAP');
            return;
        }
        
        // Check if container exists and is visible
        const container = document.getElementById(containerId);
        if (!container) {
            Utils.log(`Container ${containerId} not found`, 'TEAM_HEATMAP', 'error');
            return;
        }
        
        Utils.log(`Rendering ${plotKey} in ${containerId}`, 'TEAM_HEATMAP');
        Utils.log(`Container dimensions: ${container.offsetWidth}x${container.offsetHeight}`, 'TEAM_HEATMAP');
        
        setTimeout(() => this.lazyRenderPlot(containerId, plotKey, true), 50);
    }

    /**
     * Update team heatmap state
     */
    updateTeamHeatmapState(teamPrefix, property, value) {
        if (!this.teamHeatmapState[teamPrefix]) {
            this.teamHeatmapState[teamPrefix] = { phase: 'possession', half: 'full' };
        }
        
        this.teamHeatmapState[teamPrefix][property] = value;
        Utils.log(`Updated ${teamPrefix} ${property} to ${value}`, 'TEAM_HEATMAP');
    }

    /**
     * Get team heatmap state
     */
    getTeamHeatmapState(teamPrefix) {
        return this.teamHeatmapState[teamPrefix] || { phase: 'possession', half: 'full' };
    }

    /**
     * Show containers for overview tab
     */
    showOverviewContainers() {
        const containerIds = [
            'graph-container-xg',
            'graph-container-momentum', 
            'graph-container-summary',
            'graph-container-radar',
            'graph-container-heatmap'
        ];
        
        containerIds.forEach(id => {
            const container = document.getElementById(id);
            if (container) {
                container.classList.remove('hidden');
            }
        });
    }

    /**
     * Resize all plots
     */
    resizeAllPlots() {
        if (window.Plotly) {
            document.querySelectorAll('.js-plotly-plot').forEach(plotDiv => {
                window.Plotly.Plots.resize(plotDiv);
            });
            Utils.log('All plots resized', 'PLOT_MANAGER');
        }
    }

    /**
     * Check if plot exists in cache
     */
    hasPlot(plotKey) {
        return !!this.cachedPlots[plotKey];
    }

    /**
     * Get plot data
     */
    getPlot(plotKey) {
        return this.cachedPlots[plotKey];
    }

    /**
     * Get all cached plot keys
     */
    getCachedPlotKeys() {
        return Object.keys(this.cachedPlots);
    }
}

window.PlotManager = PlotManager;
