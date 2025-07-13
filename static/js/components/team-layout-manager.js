// Team layout manager for configurable team analysis grid layouts
class TeamLayoutManager {
    constructor(teamPrefix) {
        this.teamPrefix = teamPrefix; // 'home_team' or 'away_team'
        this.currentLayout = 'classic';
        this.gridContainer = null;
        this.layoutButtons = [];
    }

    /**
     * Initialize the team layout manager
     */
    initialize() {
        // Find the team-specific grid container by ID
        this.gridContainer = document.getElementById(`${this.teamPrefix}-analysis-grid`);
        
        // Find team-specific layout buttons
        this.layoutButtons = document.querySelectorAll(`.team-layout-btn[data-team="${this.teamPrefix}"]`);
        
        if (!this.gridContainer) {
            Utils.log(`Team grid container not found for ${this.teamPrefix}`, 'TEAM_LAYOUT_MANAGER', 'warn');
            return;
        }

        this.setupLayoutControls();
        Utils.log(`Team layout manager initialized for ${this.teamPrefix}`, 'TEAM_LAYOUT_MANAGER');
    }

    /**
     * Set up layout control buttons
     */
    setupLayoutControls() {
        this.layoutButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const layout = e.target.dataset.layout;
                if (layout) {
                    this.switchLayout(layout);
                }
            });
        });
    }

    /**
     * Switch to a different layout
     */
    switchLayout(layoutName) {
        if (!this.gridContainer) return;

        // Remove current layout class
        this.gridContainer.classList.remove(`layout-${this.currentLayout}`);
        
        // Add new layout class
        this.gridContainer.classList.add(`layout-${layoutName}`);
        
        // Update current layout
        this.currentLayout = layoutName;
        
        // Update button states
        this.updateButtonStates(layoutName);
        
        // Save layout preference
        this.saveLayoutPreference(layoutName);
        
        // Trigger plot resize after layout change
        setTimeout(() => {
            if (window.app && window.app.getComponent('plotManager')) {
                window.app.getComponent('plotManager').resizeAllPlots();
            }
        }, 300);
        
        Utils.log(`Switched ${this.teamPrefix} to layout: ${layoutName}`, 'TEAM_LAYOUT_MANAGER');
    }

    /**
     * Update button active states
     */
    updateButtonStates(activeLayout) {
        this.layoutButtons.forEach(button => {
            const layout = button.dataset.layout;
            if (layout === activeLayout) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
    }

    /**
     * Get current layout
     */
    getCurrentLayout() {
        return this.currentLayout;
    }

    /**
     * Set custom grid positioning for elements
     */
    setCustomPosition(elementId, gridColumn, gridRow) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.gridColumn = gridColumn;
            element.style.gridRow = gridRow;
            Utils.log(`Set custom position for ${elementId}: ${gridColumn}, ${gridRow}`, 'TEAM_LAYOUT_MANAGER');
        }
    }

    /**
     * Reset all custom positioning
     */
    resetCustomPositioning() {
        const containers = this.gridContainer?.querySelectorAll('.graph-container');
        containers?.forEach(container => {
            container.style.gridColumn = '';
            container.style.gridRow = '';
        });
        Utils.log(`Reset custom positioning for ${this.teamPrefix}`, 'TEAM_LAYOUT_MANAGER');
    }

    /**
     * Apply size class to an element
     */
    applySizeClass(elementId, sizeClass) {
        const element = document.getElementById(elementId);
        if (element) {
            // Remove existing size classes
            element.classList.remove('team-grid-size-small', 'team-grid-size-medium', 'team-grid-size-large', 
                                   'team-grid-size-xlarge', 'team-grid-size-wide', 'team-grid-size-tall', 'team-grid-size-full');
            
            // Add new size class
            if (sizeClass) {
                element.classList.add(`team-grid-size-${sizeClass}`);
            }
            
            Utils.log(`Applied size class ${sizeClass} to ${elementId}`, 'TEAM_LAYOUT_MANAGER');
        }
    }

    /**
     * Get available layouts
     */
    getAvailableLayouts() {
        return [
            { id: 'classic', name: 'Classic', description: 'Stats left, heatmap right' },
            { id: 'vertical', name: 'Vertical', description: 'Stats on top, heatmap below' },
            { id: 'heatmap-focus', name: 'Heatmap Focus', description: 'Small stats, large heatmap' },
            { id: 'stats-focus', name: 'Stats Focus', description: 'Large stats, smaller heatmap' },
            { id: 'balanced', name: 'Balanced', description: 'Equal width columns' },
            { id: 'wide-stats', name: 'Wide Stats', description: 'Stats take more space' }
        ];
    }

    /**
     * Save layout preference to localStorage
     */
    saveLayoutPreference(layoutName) {
        try {
            const key = `football-dashboard-team-layout-${this.teamPrefix}`;
            localStorage.setItem(key, layoutName);
            Utils.log(`Saved ${this.teamPrefix} layout preference: ${layoutName}`, 'TEAM_LAYOUT_MANAGER');
        } catch (error) {
            Utils.log(`Failed to save ${this.teamPrefix} layout preference: ${error.message}`, 'TEAM_LAYOUT_MANAGER', 'error');
        }
    }

    /**
     * Load layout preference from localStorage
     */
    loadLayoutPreference() {
        try {
            const key = `football-dashboard-team-layout-${this.teamPrefix}`;
            const saved = localStorage.getItem(key);
            if (saved && this.getAvailableLayouts().some(layout => layout.id === saved)) {
                this.switchLayout(saved);
                Utils.log(`Loaded ${this.teamPrefix} layout preference: ${saved}`, 'TEAM_LAYOUT_MANAGER');
                return saved;
            }
        } catch (error) {
            Utils.log(`Failed to load ${this.teamPrefix} layout preference: ${error.message}`, 'TEAM_LAYOUT_MANAGER', 'error');
        }
        return null;
    }

    /**
     * Handle responsive layout changes
     */
    handleResize() {
        const width = window.innerWidth;
        
        // Auto-switch to vertical layout on mobile
        if (width <= 768 && this.currentLayout !== 'vertical') {
            this.switchLayout('vertical');
            Utils.log(`Auto-switched ${this.teamPrefix} to vertical layout for mobile`, 'TEAM_LAYOUT_MANAGER');
        }
        
        // Trigger plot resize
        setTimeout(() => {
            if (window.app && window.app.getComponent('plotManager')) {
                window.app.getComponent('plotManager').resizeAllPlots();
            }
        }, 100);
    }

    /**
     * Get team prefix
     */
    getTeamPrefix() {
        return this.teamPrefix;
    }

    /**
     * Update team name in headers
     */
    updateTeamName(teamName) {
        const headers = this.gridContainer?.querySelectorAll('.stats-header h4, .heatmap-header h4');
        headers?.forEach(header => {
            if (header.textContent.includes('Team Stats')) {
                header.textContent = `${teamName} Stats`;
            } else if (header.textContent.includes('Team Heatmap')) {
                header.textContent = `${teamName} Heatmap`;
            }
        });
        Utils.log(`Updated team name to ${teamName} for ${this.teamPrefix}`, 'TEAM_LAYOUT_MANAGER');
    }

    /**
     * Destroy team layout manager
     */
    destroy() {
        this.layoutButtons.forEach(button => {
            button.removeEventListener('click', this.switchLayout);
        });
        
        this.gridContainer = null;
        this.layoutButtons = [];
        this.currentLayout = 'classic';
        
        Utils.log(`Team layout manager destroyed for ${this.teamPrefix}`, 'TEAM_LAYOUT_MANAGER');
    }
}

window.TeamLayoutManager = TeamLayoutManager;
