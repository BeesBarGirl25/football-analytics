// Main application initialization
class FootballDashboardApp {
    constructor() {
        this.currentPage = null;
        this.components = {};
        this.services = {};
        this.pageInstance = null;
        this.dropdownService = null;
    }

    /**
     * Initialize the application
     */
    async init() {
        Utils.log('Initializing Football Dashboard App...', 'APP');
        
        // Initialize dropdown service first (needed by all pages)
        await this.initializeDropdownService();
        
        // Set up global event listeners
        this.setupGlobalEvents();
        
        // Initialize page-specific logic
        this.initializePage();
        
        Utils.log('App initialized successfully', 'APP');
    }

    /**
     * Initialize dropdown service
     */
    async initializeDropdownService() {
        if (typeof DropdownService !== 'undefined') {
            this.dropdownService = new DropdownService();
            await this.dropdownService.initialize();
            this.services.dropdownService = this.dropdownService;
            Utils.log('Dropdown service initialized', 'APP');
        } else {
            Utils.log('DropdownService not available - check script loading order', 'APP', 'warn');
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
        
        // Handle dropdown changes (for existing dropdowns.js compatibility)
        if (typeof $ !== 'undefined') {
            $('.searchable-dropdown').on('change', (e) => {
                this.handleDropdownChange(e);
            });
        }

        // Handle visibility change (for performance optimization)
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.pageInstance) {
                // Page became visible, refresh plots if needed
                setTimeout(() => this.handleResize(), 100);
            }
        });
    }

    /**
     * Initialize page-specific logic
     */
    initializePage() {
        const path = window.location.pathname;
        
        if (path.includes('match-analysis')) {
            this.currentPage = 'match-analysis';
            this.pageInstance = new MatchAnalysisPage();
            this.pageInstance.initialize();
            
            // Store components for global access
            this.components = this.pageInstance.getComponents();
            
        } else if (path.includes('competition-analysis')) {
            this.currentPage = 'competition-analysis';
            this.pageInstance = new CompetitionAnalysisPage();
            this.pageInstance.initialize();
            
            // Store components for global access
            this.components = this.pageInstance.getComponents();
            
        } else if (path.includes('team-analysis')) {
            this.currentPage = 'team-analysis';
            // Team analysis page can be implemented later
            Utils.log('Team analysis page not yet modularized', 'APP', 'warn');
            
        } else if (path.includes('player-analysis')) {
            this.currentPage = 'player-analysis';
            // Player analysis page can be implemented later
            Utils.log('Player analysis page not yet modularized', 'APP', 'warn');
        }
        
        Utils.log(`Page initialized: ${this.currentPage}`, 'APP');
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Trigger resize on page instance
        if (this.pageInstance && typeof this.pageInstance.handleResize === 'function') {
            this.pageInstance.handleResize();
        }
        
        // Trigger resize on all Plotly plots (fallback)
        if (window.Plotly) {
            document.querySelectorAll('.js-plotly-plot').forEach(plotDiv => {
                try {
                    window.Plotly.Plots.resize(plotDiv);
                } catch (e) {
                    // Ignore resize errors for plots that aren't ready
                }
            });
        }
        
        Utils.log('Window resized, plots updated', 'APP');
    }

    /**
     * Handle dropdown changes (for backward compatibility)
     */
    handleDropdownChange(event) {
        const dropdown = event.target;
        const dropdownType = dropdown.id;
        
        Utils.log(`Dropdown changed: ${dropdownType} = ${dropdown.value}`, 'APP');
        
        // Trigger page-specific handlers if available
        if (this.components.plotManager) {
            // This can be extended for specific dropdown handling
        }
    }

    /**
     * Get current page instance
     */
    getCurrentPage() {
        return this.pageInstance;
    }

    /**
     * Get component by name
     */
    getComponent(name) {
        return this.components[name] || null;
    }

    /**
     * Get all components
     */
    getComponents() {
        return this.components;
    }

    /**
     * Refresh current page
     */
    async refreshPage() {
        if (this.pageInstance && typeof this.pageInstance.refreshCurrentMatch === 'function') {
            await this.pageInstance.refreshCurrentMatch();
            Utils.log('Page refreshed', 'APP');
        }
    }

    /**
     * Clear current page data
     */
    clearPageData() {
        if (this.pageInstance && typeof this.pageInstance.clearMatchData === 'function') {
            this.pageInstance.clearMatchData();
            Utils.log('Page data cleared', 'APP');
        }
    }

    /**
     * Handle errors globally
     */
    handleError(error, context = 'APP') {
        Utils.log(`Error: ${error.message}`, context, 'error');
        
        // You can add global error handling here
        // For example, show a toast notification or error modal
    }

    /**
     * Check if app is ready
     */
    isReady() {
        return !!(this.currentPage && this.pageInstance);
    }

    /**
     * Get app status
     */
    getStatus() {
        return {
            currentPage: this.currentPage,
            isReady: this.isReady(),
            components: Object.keys(this.components),
            hasPageInstance: !!this.pageInstance
        };
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Check if required dependencies are loaded
    if (typeof Utils === 'undefined') {
        console.error('Utils not loaded - check script loading order');
        return;
    }
    
    if (typeof AppConfig === 'undefined') {
        console.error('AppConfig not loaded - check script loading order');
        return;
    }
    
    // Initialize the app
    window.app = new FootballDashboardApp();
    window.app.init();
    
    // Make app globally accessible for debugging
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        window.debugApp = () => {
            console.log('App Status:', window.app.getStatus());
            console.log('Components:', window.app.getComponents());
            if (window.app.getCurrentPage()) {
                console.log('Current Page:', window.app.getCurrentPage());
            }
        };
        Utils.log('Debug mode enabled. Use debugApp() in console for debugging.', 'APP');
    }
});

// Export for use in other modules
window.FootballDashboardApp = FootballDashboardApp;
