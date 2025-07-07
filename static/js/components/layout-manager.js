// Layout manager for configurable grid layouts
class LayoutManager {
    constructor() {
        this.currentLayout = 'classic';
        this.gridContainer = null;
        this.layoutButtons = [];
    }

    /**
     * Initialize the layout manager
     */
    initialize() {
        this.gridContainer = document.getElementById('overview-grid');
        this.layoutButtons = document.querySelectorAll('.layout-btn');
        
        if (!this.gridContainer) {
            Utils.log('Grid container not found', 'LAYOUT_MANAGER', 'warn');
            return;
        }

        this.setupLayoutControls();
        Utils.log('Layout manager initialized', 'LAYOUT_MANAGER');
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
        
        Utils.log(`Switched to layout: ${layoutName}`, 'LAYOUT_MANAGER');
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
            Utils.log(`Set custom position for ${elementId}: ${gridColumn}, ${gridRow}`, 'LAYOUT_MANAGER');
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
        Utils.log('Reset custom positioning', 'LAYOUT_MANAGER');
    }

    /**
     * Apply size class to an element
     */
    applySizeClass(elementId, sizeClass) {
        const element = document.getElementById(elementId);
        if (element) {
            // Remove existing size classes
            element.classList.remove('grid-size-small', 'grid-size-medium', 'grid-size-large', 
                                   'grid-size-xlarge', 'grid-size-wide', 'grid-size-tall', 'grid-size-full');
            
            // Add new size class
            if (sizeClass) {
                element.classList.add(`grid-size-${sizeClass}`);
            }
            
            Utils.log(`Applied size class ${sizeClass} to ${elementId}`, 'LAYOUT_MANAGER');
        }
    }

    /**
     * Get available layouts
     */
    getAvailableLayouts() {
        return [
            { id: 'classic', name: 'Classic', description: 'Traditional 3-column layout' },
            { id: 'horizontal', name: 'Horizontal', description: 'All items in a row' },
            { id: 'vertical', name: 'Vertical', description: 'All items stacked vertically' },
            { id: 'summary-focus', name: 'Summary Focus', description: 'Large summary area' },
            { id: 'charts-focus', name: 'Charts Focus', description: 'Emphasis on charts' },
            { id: 'balanced', name: 'Balanced', description: '2x2 balanced grid' }
        ];
    }

    /**
     * Save layout preference to localStorage
     */
    saveLayoutPreference(layoutName) {
        try {
            localStorage.setItem('football-dashboard-layout', layoutName);
            Utils.log(`Saved layout preference: ${layoutName}`, 'LAYOUT_MANAGER');
        } catch (error) {
            Utils.log(`Failed to save layout preference: ${error.message}`, 'LAYOUT_MANAGER', 'error');
        }
    }

    /**
     * Load layout preference from localStorage
     */
    loadLayoutPreference() {
        try {
            const saved = localStorage.getItem('football-dashboard-layout');
            if (saved && this.getAvailableLayouts().some(layout => layout.id === saved)) {
                this.switchLayout(saved);
                Utils.log(`Loaded layout preference: ${saved}`, 'LAYOUT_MANAGER');
                return saved;
            }
        } catch (error) {
            Utils.log(`Failed to load layout preference: ${error.message}`, 'LAYOUT_MANAGER', 'error');
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
            Utils.log('Auto-switched to vertical layout for mobile', 'LAYOUT_MANAGER');
        }
        
        // Trigger plot resize
        setTimeout(() => {
            if (window.app && window.app.getComponent('plotManager')) {
                window.app.getComponent('plotManager').resizeAllPlots();
            }
        }, 100);
    }

    /**
     * Destroy layout manager
     */
    destroy() {
        this.layoutButtons.forEach(button => {
            button.removeEventListener('click', this.switchLayout);
        });
        
        this.gridContainer = null;
        this.layoutButtons = [];
        this.currentLayout = 'classic';
        
        Utils.log('Layout manager destroyed', 'LAYOUT_MANAGER');
    }
}

window.LayoutManager = LayoutManager;
