// Navigation component for tab switching and UI interactions
class Navigation {
    constructor(plotManager) {
        this.plotManager = plotManager;
        this.currentTab = 'overview';
        this.setupEventListeners();
    }

    /**
     * Set up navigation event listeners
     */
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Layout toggle
        const layoutToggle = document.getElementById('layout-toggle-checkbox');
        if (layoutToggle) {
            layoutToggle.addEventListener('change', (e) => {
                this.toggleLayout(e.target.checked);
            });
        }
    }

    /**
     * Switch between tabs
     */
    switchTab(tabName) {
        if (this.currentTab === tabName) return;

        Utils.log(`Switching to tab: ${tabName}`, 'NAVIGATION');

        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.analysis-content').forEach(content => content.classList.add('hidden'));
        
        const selectedTab = document.querySelector(`.tab-btn[data-tab="${tabName}"]`);
        const tabEl = document.getElementById(tabName);
        
        if (selectedTab) selectedTab.classList.add('active');
        if (tabEl) tabEl.classList.remove('hidden');

        // Update current tab
        this.currentTab = tabName;

        // Handle tab-specific logic
        this.onTabActivated(tabName);

        // Trigger resize for plots after animation
        setTimeout(() => {
            if (this.plotManager) {
                this.plotManager.resizeAllPlots();
            }
        }, AppConfig.UI.ANIMATION_DURATION);
    }

    /**
     * Handle tab activation
     */
    onTabActivated(tabName) {
        switch (tabName) {
            case 'home':
                this.showTeamTab(AppConfig.TEAMS.HOME);
                break;
            case 'away':
                this.showTeamTab(AppConfig.TEAMS.AWAY);
                break;
            case 'overview':
                this.showOverviewTab();
                break;
            case 'player':
                // Player-specific logic can be added here
                break;
        }
    }

    /**
     * Show team tab
     */
    showTeamTab(teamPrefix) {
        const containerId = teamPrefix === AppConfig.TEAMS.HOME ? 
            'graph-container-home-team-4' : 
            'graph-container-away-team-4';
        
        const container = document.getElementById(containerId);
        if (container) {
            container.classList.remove('hidden');
            Utils.log(`${teamPrefix.toUpperCase()} tab container shown`, 'NAVIGATION');
            
            // Also unhide any elements with the team plot group
            const plotGroupName = `${teamPrefix}_heatmap`;
            document.querySelectorAll(`[data-plot-group="${plotGroupName}"]`).forEach(el => {
                el.classList.remove('hidden');
                Utils.log(`Unhiding plot group element for ${plotGroupName}`, 'NAVIGATION');
            });
        }
        
        // Render with current state
        setTimeout(() => {
            if (this.plotManager) {
                this.plotManager.renderCurrentTeamHeatmap(teamPrefix);
            }
        }, AppConfig.UI.PLOT_RENDER_DELAY);

        // Load team stats if available
        if (window.app && window.app.components && window.app.components.statsTable) {
            window.app.components.statsTable.loadTeamStats(teamPrefix);
        }
    }

    /**
     * Show overview tab
     */
    showOverviewTab() {
        if (this.plotManager) {
            this.plotManager.showOverviewContainers();
            
            // Render dominance heatmap
            setTimeout(() => {
                this.plotManager.lazyRenderPlot(
                    AppConfig.CONTAINERS.DOMINANCE_PLOT, 
                    AppConfig.PLOT_TYPES.DOMINANCE_HEATMAP
                );
            }, AppConfig.UI.TAB_SWITCH_DELAY);
        }
    }

    /**
     * Toggle between wide and compact layout
     */
    toggleLayout(isCompact) {
        document.querySelectorAll('.graphs-container').forEach(container => {
            container.classList.toggle('compact-mode', isCompact);
            container.classList.toggle('wide-mode', !isCompact);
        });
        
        const toggleLabel = document.querySelector('.toggle-label');
        if (toggleLabel) {
            toggleLabel.textContent = isCompact ? 'Wide Layout' : 'Compact Layout';
        }
        
        Utils.log(`Layout toggled to ${isCompact ? 'compact' : 'wide'} mode`, 'NAVIGATION');
        
        // Trigger resize after layout change
        setTimeout(() => {
            if (this.plotManager) {
                this.plotManager.resizeAllPlots();
            }
        }, AppConfig.UI.ANIMATION_DURATION);
    }

    /**
     * Update tab button text (for team names)
     */
    updateTabButtonText(tabName, text) {
        const tabButton = document.querySelector(`.tab-btn[data-tab="${tabName}"]`);
        if (tabButton) {
            tabButton.textContent = text;
            Utils.log(`Updated ${tabName} tab text to: ${text}`, 'NAVIGATION');
        }
    }

    /**
     * Get current active tab
     */
    getCurrentTab() {
        return this.currentTab;
    }

    /**
     * Show/hide graph containers based on active tab
     */
    updateGraphVisibility(tabName) {
        // Hide all graph containers first
        document.querySelectorAll('.graph-container').forEach(container => {
            container.classList.add('hidden');
        });

        // Show relevant containers based on tab
        switch (tabName) {
            case 'overview':
                const overviewContainers = [
                    'graph-container-xg',
                    'graph-container-momentum',
                    'graph-container-summary',
                    'graph-container-heatmap'
                ];
                overviewContainers.forEach(id => {
                    const container = document.getElementById(id);
                    if (container) container.classList.remove('hidden');
                });
                break;
            case 'home':
                const homeContainer = document.getElementById('graph-container-home-team-4');
                if (homeContainer) homeContainer.classList.remove('hidden');
                break;
            case 'away':
                const awayContainer = document.getElementById('graph-container-away-team-4');
                if (awayContainer) awayContainer.classList.remove('hidden');
                break;
        }
    }

    /**
     * Initialize navigation with default state
     */
    initialize() {
        // Set default tab
        this.switchTab('overview');
        Utils.log('Navigation initialized', 'NAVIGATION');
    }
}

window.Navigation = Navigation;
