// Heatmap controls component for phase and half switching
class HeatmapControls {
    constructor(plotManager) {
        this.plotManager = plotManager;
        this.setupEventListeners();
    }

    /**
     * Set up event listeners for heatmap controls
     */
    setupEventListeners() {
        // Dropdown change handlers
        document.addEventListener('change', (event) => {
            if (event.target.classList.contains('half-dropdown')) {
                this.handleHalfDropdownChange(event);
            } else if (event.target.classList.contains('phase-dropdown')) {
                this.handlePhaseDropdownChange(event);
            }
        });

        // Quick action button handlers
        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('quick-btn')) {
                this.handleQuickAction(event);
            }
        });

        // Legacy button handlers (for backward compatibility)
        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('phase-btn')) {
                this.handlePhaseChange(event);
            } else if (event.target.classList.contains('toggle-btn')) {
                this.handleToggleChange(event);
            }
        });
    }

    /**
     * Handle phase button changes
     */
    handlePhaseChange(event) {
        const button = event.target;
        const controlsBar = button.closest('.heatmap-controls-bar');
        
        if (!controlsBar) return;
        
        const teamPrefix = controlsBar.getAttribute('data-team');
        
        // Update active states within the phase control group
        const phaseGroup = button.closest('.control-group.phase-controls');
        if (phaseGroup) {
            phaseGroup.querySelectorAll('.phase-btn').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
        }
        
        // Update state
        const newPhase = button.getAttribute('data-phase');
        if (this.plotManager) {
            this.plotManager.updateTeamHeatmapState(teamPrefix, 'phase', newPhase);
        }
        
        // Check if container is visible before rendering
        const container = button.closest('.graph-container');
        if (!container || !Utils.isElementVisible(container)) {
            Utils.log(`Phase change for ${teamPrefix} — container not visible`, 'HEATMAP_CONTROLS');
            return;
        }
        
        // Re-render with new combination
        if (this.plotManager) {
            this.plotManager.renderCurrentTeamHeatmap(teamPrefix);
        }
        
        Utils.log(`Phase changed to ${newPhase} for ${teamPrefix}`, 'HEATMAP_CONTROLS');
    }

    /**
     * Handle toggle button changes (half switching and dominance)
     */
    handleToggleChange(event) {
        const button = event.target;
        const controlsBar = button.closest('.heatmap-controls-bar');
        const dominanceButtons = button.closest('.dominance-toggle-buttons');
        
        if (controlsBar) {
            // Team heatmap half switching
            this.handleTeamHalfChange(button, controlsBar);
        } else if (dominanceButtons) {
            // Dominance heatmap switching
            this.handleDominanceChange(button, dominanceButtons);
        }
    }

    /**
     * Handle team heatmap half changes
     */
    handleTeamHalfChange(button, controlsBar) {
        const teamPrefix = controlsBar.getAttribute('data-team');
        
        // Update active states within the half control group
        const halfGroup = button.closest('.control-group.half-controls');
        if (halfGroup) {
            halfGroup.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
        }
        
        // Update state
        const newHalf = button.getAttribute('data-half');
        if (this.plotManager) {
            this.plotManager.updateTeamHeatmapState(teamPrefix, 'half', newHalf);
        }
        
        // Check if container is visible before rendering
        const container = button.closest('.graph-container');
        if (!container || !Utils.isElementVisible(container)) {
            Utils.log(`Half change for ${teamPrefix} — container not visible`, 'HEATMAP_CONTROLS');
            return;
        }
        
        // Re-render with new combination
        if (this.plotManager) {
            this.plotManager.renderCurrentTeamHeatmap(teamPrefix);
        }
        
        Utils.log(`Half changed to ${newHalf} for ${teamPrefix}`, 'HEATMAP_CONTROLS');
    }

    /**
     * Handle half dropdown changes
     */
    handleHalfDropdownChange(event) {
        const dropdown = event.target;
        const controlsContainer = dropdown.closest('.heatmap-controls-option3');
        
        if (!controlsContainer) return;
        
        const teamPrefix = controlsContainer.getAttribute('data-team');
        const newHalf = dropdown.value;
        
        // Update state
        if (this.plotManager) {
            this.plotManager.updateTeamHeatmapState(teamPrefix, 'half', newHalf);
        }
        
        // Check if container is visible before rendering
        const container = dropdown.closest('.graph-container');
        if (!container || !Utils.isElementVisible(container)) {
            Utils.log(`Half dropdown change for ${teamPrefix} — container not visible`, 'HEATMAP_CONTROLS');
            return;
        }
        
        // Re-render with new combination
        if (this.plotManager) {
            this.plotManager.renderCurrentTeamHeatmap(teamPrefix);
        }
        
        Utils.log(`Half changed to ${newHalf} for ${teamPrefix} via dropdown`, 'HEATMAP_CONTROLS');
    }

    /**
     * Handle phase dropdown changes
     */
    handlePhaseDropdownChange(event) {
        const dropdown = event.target;
        const controlsContainer = dropdown.closest('.heatmap-controls-option3');
        
        if (!controlsContainer) return;
        
        const teamPrefix = controlsContainer.getAttribute('data-team');
        const newPhase = dropdown.value;
        
        // Update state
        if (this.plotManager) {
            this.plotManager.updateTeamHeatmapState(teamPrefix, 'phase', newPhase);
        }
        
        // Check if container is visible before rendering
        const container = dropdown.closest('.graph-container');
        if (!container || !Utils.isElementVisible(container)) {
            Utils.log(`Phase dropdown change for ${teamPrefix} — container not visible`, 'HEATMAP_CONTROLS');
            return;
        }
        
        // Re-render with new combination
        if (this.plotManager) {
            this.plotManager.renderCurrentTeamHeatmap(teamPrefix);
        }
        
        Utils.log(`Phase changed to ${newPhase} for ${teamPrefix} via dropdown`, 'HEATMAP_CONTROLS');
    }

    /**
     * Handle quick action button clicks
     */
    handleQuickAction(event) {
        const button = event.target;
        const controlsContainer = button.closest('.heatmap-controls-option3');
        
        if (!controlsContainer) return;
        
        const teamPrefix = controlsContainer.getAttribute('data-team');
        const preset = button.getAttribute('data-preset');
        
        // Parse preset (e.g., "full-possession" -> half: "full", phase: "possession")
        const [half, phase] = preset.split('-');
        
        // Update dropdowns
        const halfDropdown = controlsContainer.querySelector('.half-dropdown');
        const phaseDropdown = controlsContainer.querySelector('.phase-dropdown');
        
        if (halfDropdown) halfDropdown.value = half;
        if (phaseDropdown) phaseDropdown.value = phase;
        
        // Update state
        if (this.plotManager) {
            this.plotManager.updateTeamHeatmapState(teamPrefix, 'half', half);
            this.plotManager.updateTeamHeatmapState(teamPrefix, 'phase', phase);
        }
        
        // Check if container is visible before rendering
        const container = button.closest('.graph-container');
        if (!container || !Utils.isElementVisible(container)) {
            Utils.log(`Quick action for ${teamPrefix} — container not visible`, 'HEATMAP_CONTROLS');
            return;
        }
        
        // Re-render with new combination
        if (this.plotManager) {
            this.plotManager.renderCurrentTeamHeatmap(teamPrefix);
        }
        
        Utils.log(`Quick action applied: ${preset} for ${teamPrefix}`, 'HEATMAP_CONTROLS');
    }

    /**
     * Handle dominance heatmap changes
     */
    handleDominanceChange(button, dominanceButtons) {
        // Update active states
        dominanceButtons.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        const viewKey = button.getAttribute('data-view');
        const container = button.closest('.graph-container');
        const containerId = container?.querySelector('.plotly-wrapper')?.id;

        if (!container || !Utils.isElementVisible(container)) {
            Utils.log(`Dominance toggle for ${viewKey} — container not visible`, 'HEATMAP_CONTROLS');
            return;
        }

        if (containerId && this.plotManager) {
            setTimeout(() => {
                this.plotManager.lazyRenderPlot(containerId, viewKey, true);
            }, 50);
        }
        
        Utils.log(`Dominance view changed to ${viewKey}`, 'HEATMAP_CONTROLS');
    }

    /**
     * Initialize controls with default states
     */
    initialize() {
        // Set default active states for phase buttons
        document.querySelectorAll('.phase-btn[data-phase="possession"]').forEach(btn => {
            btn.classList.add('active');
        });
        
        // Set default active states for half buttons
        document.querySelectorAll('.toggle-btn[data-half="full"]').forEach(btn => {
            btn.classList.add('active');
        });
        
        // Set default active state for dominance view
        const defaultDominanceBtn = document.querySelector('.toggle-btn[data-view="dominance_heatmap"]');
        if (defaultDominanceBtn) {
            defaultDominanceBtn.classList.add('active');
        }
        
        Utils.log('Heatmap controls initialized', 'HEATMAP_CONTROLS');
    }

    /**
     * Reset controls to default state
     */
    resetToDefaults() {
        // Reset team heatmap states
        if (this.plotManager) {
            this.plotManager.updateTeamHeatmapState(AppConfig.TEAMS.HOME, 'phase', AppConfig.HEATMAP.DEFAULT_PHASE);
            this.plotManager.updateTeamHeatmapState(AppConfig.TEAMS.HOME, 'half', AppConfig.HEATMAP.DEFAULT_HALF);
            this.plotManager.updateTeamHeatmapState(AppConfig.TEAMS.AWAY, 'phase', AppConfig.HEATMAP.DEFAULT_PHASE);
            this.plotManager.updateTeamHeatmapState(AppConfig.TEAMS.AWAY, 'half', AppConfig.HEATMAP.DEFAULT_HALF);
        }
        
        // Reset UI states
        this.initialize();
        
        Utils.log('Heatmap controls reset to defaults', 'HEATMAP_CONTROLS');
    }

    /**
     * Get current state for a team
     */
    getTeamState(teamPrefix) {
        if (this.plotManager) {
            return this.plotManager.getTeamHeatmapState(teamPrefix);
        }
        return { phase: AppConfig.HEATMAP.DEFAULT_PHASE, half: AppConfig.HEATMAP.DEFAULT_HALF };
    }

    /**
     * Set team state programmatically
     */
    setTeamState(teamPrefix, phase, half) {
        if (this.plotManager) {
            this.plotManager.updateTeamHeatmapState(teamPrefix, 'phase', phase);
            this.plotManager.updateTeamHeatmapState(teamPrefix, 'half', half);
        }
        
        // Update UI to reflect the state
        this.updateUIState(teamPrefix, phase, half);
        
        Utils.log(`Set ${teamPrefix} state to ${phase}/${half}`, 'HEATMAP_CONTROLS');
    }

    /**
     * Update UI to reflect current state
     */
    updateUIState(teamPrefix, phase, half) {
        // Try new dropdown controls first
        const dropdownControls = document.querySelector(`.heatmap-controls-option3[data-team="${teamPrefix}"]`);
        if (dropdownControls) {
            const halfDropdown = dropdownControls.querySelector('.half-dropdown');
            const phaseDropdown = dropdownControls.querySelector('.phase-dropdown');
            
            if (halfDropdown) halfDropdown.value = half;
            if (phaseDropdown) phaseDropdown.value = phase;
            return;
        }
        
        // Fallback to legacy button controls
        const controlsBar = document.querySelector(`.heatmap-controls-bar[data-team="${teamPrefix}"]`);
        if (!controlsBar) return;
        
        // Update phase buttons
        const phaseButtons = controlsBar.querySelectorAll('.phase-btn');
        phaseButtons.forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-phase') === phase);
        });
        
        // Update half buttons
        const halfButtons = controlsBar.querySelectorAll('.toggle-btn[data-half]');
        halfButtons.forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-half') === half);
        });
    }
}

window.HeatmapControls = HeatmapControls;
