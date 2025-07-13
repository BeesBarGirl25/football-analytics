// Match analysis page component
class MatchAnalysisPage {
    constructor() {
        this.plotManager = null;
        this.navigation = null;
        this.heatmapControls = null;
        this.statsTable = null;
        this.layoutManager = null;
        this.homeTeamLayoutManager = null;
        this.awayTeamLayoutManager = null;
        this.currentMatchId = null;
    }

    /**
     * Initialize the match analysis page
     */
    initialize() {
        // Initialize services
        this.plotManager = new PlotManager();
        
        // Initialize components
        this.navigation = new Navigation(this.plotManager);
        this.heatmapControls = new HeatmapControls(this.plotManager);
        this.statsTable = new StatsTable();
        this.layoutManager = new LayoutManager();
        this.homeTeamLayoutManager = new TeamLayoutManager('home_team');
        this.awayTeamLayoutManager = new TeamLayoutManager('away_team');
        
        // Set up match selection
        this.setupMatchSelection();
        
        // Also listen for dropdown service completion
        this.listenForDropdownServiceCompletion();
        
        // Initialize components
        this.navigation.initialize();
        this.heatmapControls.initialize();
        this.statsTable.initialize();
        this.layoutManager.initialize();
        this.homeTeamLayoutManager.initialize();
        this.awayTeamLayoutManager.initialize();
        
        // Load saved layout preferences
        this.layoutManager.loadLayoutPreference();
        this.homeTeamLayoutManager.loadLayoutPreference();
        this.awayTeamLayoutManager.loadLayoutPreference();
        
        // Check for default match selection and load plots immediately
        this.checkAndLoadDefaultMatch();
        
        Utils.log('Match analysis page initialized', 'MATCH_ANALYSIS');
    }

    /**
     * Set up match selection dropdown
     */
    setupMatchSelection() {
        const matchSelect = $('#match-select');
        if (matchSelect.length) {
            matchSelect.on('change', async (event) => {
                await this.handleMatchSelection(event.target.value);
            });
            
            // Check if there's already a selected match (from auto-selection)
            // Use multiple checks with increasing delays to ensure dropdown service has completed auto-selection
            const checkForPreselectedMatch = (attempt = 1, maxAttempts = 10) => {
                const currentValue = matchSelect.val();
                Utils.log(`Attempt ${attempt}: Checking for pre-selected match, current value: "${currentValue}"`, 'MATCH_ANALYSIS');
                
                if (currentValue && currentValue !== "" && currentValue !== "Select match") {
                    Utils.log(`Found pre-selected match: ${currentValue}, loading plots...`, 'MATCH_ANALYSIS');
                    this.handleMatchSelection(currentValue);
                    return;
                }
                
                if (attempt < maxAttempts) {
                    setTimeout(() => checkForPreselectedMatch(attempt + 1, maxAttempts), 200);
                } else {
                    Utils.log('No pre-selected match found after all attempts', 'MATCH_ANALYSIS', 'warn');
                }
            };
            
            // Start checking after a short delay
            setTimeout(() => checkForPreselectedMatch(), 300);
        }
    }

    /**
     * Handle match selection
     */
    async handleMatchSelection(matchId) {
        if (!matchId || matchId === "Select match") {
            Utils.log("Skipping fetch: no valid match selected", 'MATCH_ANALYSIS', 'warn');
            return;
        }

        this.currentMatchId = matchId;
        Utils.log(`Loading match data for ID: ${matchId}`, 'MATCH_ANALYSIS');

        try {
            // Show loading states
            this.showLoadingStates();
            
            // Fetch plot data
            const response = await fetch(`${AppConfig.API.MATCH_PLOTS}/${matchId}`);
            if (!response.ok) {
                throw new Error(`Failed to fetch plot data: ${response.status}`);
            }

            const result = await response.json();
            Utils.log("Plot data received", 'MATCH_ANALYSIS');

            // Cache plot data
            this.plotManager.cachePlots(result);
            
            // Clear previous renders
            this.plotManager.clearCache();
            this.plotManager.cachePlots(result);

            // Show main containers
            this.plotManager.showOverviewContainers();

            // Render main plots
            this.plotManager.renderMainPlots();

            // Render default dominance heatmap
            this.renderDefaultHeatmap();

            // Update match summary
            this.updateMatchSummary(result.match_summary);

            // Update team tables
            this.updateTeamTables(result.match_summary);

            // Load team stats
            this.statsTable.loadAllTeamStats();

            // Reset controls and switch to overview
            this.heatmapControls.resetToDefaults();
            this.navigation.switchTab('overview');

            Utils.log('Match data loaded successfully', 'MATCH_ANALYSIS');

        } catch (error) {
            Utils.log(`Failed to load match data: ${error.message}`, 'MATCH_ANALYSIS', 'error');
            this.showErrorStates();
        }
    }

    /**
     * Show loading states across the UI
     */
    showLoadingStates() {
        // Show loading for stats tables
        this.statsTable.showLoading(AppConfig.TEAMS.HOME, 'Loading...');
        this.statsTable.showLoading(AppConfig.TEAMS.AWAY, 'Loading...');
        
        // Show loading for summary
        const summaryElements = [
            'home-team-name',
            'away-team-name',
            'home-team-score',
            'away-team-score'
        ];
        
        summaryElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.textContent = '...';
        });
    }

    /**
     * Show error states across the UI
     */
    showErrorStates() {
        this.statsTable.showError(AppConfig.TEAMS.HOME, 'Failed to load');
        this.statsTable.showError(AppConfig.TEAMS.AWAY, 'Failed to load');
        
        const summaryElements = [
            'home-team-name',
            'away-team-name',
            'home-team-score',
            'away-team-score'
        ];
        
        summaryElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.textContent = 'Error';
        });
    }

    /**
     * Update match summary display
     */
    updateMatchSummary(summary) {
        if (!summary) return;

        // Debug logging for scoreline issues
        Utils.log('=== MATCH SUMMARY DEBUG ===', 'MATCH_ANALYSIS');
        Utils.log(`Home Team: ${summary.homeTeam}`, 'MATCH_ANALYSIS');
        Utils.log(`Away Team: ${summary.awayTeam}`, 'MATCH_ANALYSIS');
        Utils.log(`Home Score (Normal): ${summary.homeTeamNormalTime}`, 'MATCH_ANALYSIS');
        Utils.log(`Away Score (Normal): ${summary.awayTeamNormalTime}`, 'MATCH_ANALYSIS');
        Utils.log(`Home Score Type: ${typeof summary.homeTeamNormalTime}`, 'MATCH_ANALYSIS');
        Utils.log(`Away Score Type: ${typeof summary.awayTeamNormalTime}`, 'MATCH_ANALYSIS');
        Utils.log(`Away Score === 0: ${summary.awayTeamNormalTime === 0}`, 'MATCH_ANALYSIS');
        Utils.log(`Away Score == 0: ${summary.awayTeamNormalTime == 0}`, 'MATCH_ANALYSIS');
        Utils.log(`Away Score === "0": ${summary.awayTeamNormalTime === "0"}`, 'MATCH_ANALYSIS');
        Utils.log(`Scoreline: ${summary.scoreline}`, 'MATCH_ANALYSIS');
        Utils.log(`Full Summary Object:`, 'MATCH_ANALYSIS');
        Utils.log(summary, 'MATCH_ANALYSIS');

        // Update team names and scores
        const updates = [
            { id: 'home-team-name', value: summary.homeTeam ?? '–' },
            { id: 'away-team-name', value: summary.awayTeam ?? '–' },
            { id: 'home-team-score', value: (summary.homeTeamNormalTime !== null && summary.homeTeamNormalTime !== undefined) ? summary.homeTeamNormalTime : '–' },
            { id: 'away-team-score', value: (summary.awayTeamNormalTime !== null && summary.awayTeamNormalTime !== undefined) ? summary.awayTeamNormalTime : '–' }
        ];

        updates.forEach(({ id, value }) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
            Utils.log(`Updated ${id} to: ${value}`, 'MATCH_ANALYSIS');
        });

        // Update score separator
        const separator = document.getElementById('score-seperator');
        if (separator) separator.textContent = '-';

        // Update tab button texts with actual team names
        if (summary.homeTeam) {
            this.navigation.updateTabButtonText('home', summary.homeTeam);
            this.homeTeamLayoutManager.updateTeamName(summary.homeTeam);
        }
        if (summary.awayTeam) {
            this.navigation.updateTabButtonText('away', summary.awayTeam);
            this.awayTeamLayoutManager.updateTeamName(summary.awayTeam);
        }

        // Handle extra time details
        const extraDetails = document.getElementById('extra-details');
        if (extraDetails) {
            if (summary.extraTimeDetails) {
                extraDetails.textContent = summary.extraTimeDetails;
                extraDetails.style.display = 'block';
            } else {
                extraDetails.style.display = 'none';
            }
        }

        Utils.log(`Match summary updated: ${summary.homeTeam} vs ${summary.awayTeam}`, 'MATCH_ANALYSIS');
    }

    /**
     * Update team tables with player data
     */
    updateTeamTables(summary) {
        if (!summary) return;

        if (summary.home) {
            this.populateTable('home-team-table', summary.home);
        }
        if (summary.away) {
            this.populateTable('away-team-table', summary.away);
        }
    }

    /**
     * Populate a team table with player data
     */
    populateTable(tableId, players) {
        const tableBody = document.querySelector(`#${tableId} tbody`);
        if (!tableBody) return;

        tableBody.innerHTML = '';

        players.forEach(player => {
            const row = document.createElement('tr');
            const playerCell = document.createElement('td');
            const contribCell = document.createElement('td');

            playerCell.textContent = player.player;
            contribCell.textContent = player.contributions?.join('') ?? '';

            row.appendChild(playerCell);
            row.appendChild(contribCell);
            tableBody.appendChild(row);
        });

        Utils.log(`Table ${tableId} populated with ${players.length} players`, 'MATCH_ANALYSIS');
    }

    /**
     * Get current match ID
     */
    getCurrentMatchId() {
        return this.currentMatchId;
    }

    /**
     * Refresh current match data
     */
    async refreshCurrentMatch() {
        if (this.currentMatchId) {
            await this.handleMatchSelection(this.currentMatchId);
        }
    }

    /**
     * Clear all match data
     */
    clearMatchData() {
        this.currentMatchId = null;
        this.plotManager.clearCache();
        this.statsTable.clear();
        this.heatmapControls.resetToDefaults();
        
        // Clear summary
        const summaryElements = [
            'home-team-name',
            'away-team-name', 
            'home-team-score',
            'away-team-score'
        ];
        
        summaryElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.textContent = '–';
        });

        // Reset tab button texts
        this.navigation.updateTabButtonText('home', 'Home');
        this.navigation.updateTabButtonText('away', 'Away');

        Utils.log('Match data cleared', 'MATCH_ANALYSIS');
    }

    /**
     * Handle window resize
     */
    handleResize() {
        if (this.plotManager) {
            this.plotManager.resizeAllPlots();
        }
    }

    /**
     * Listen for dropdown service completion and auto-load first match
     */
    listenForDropdownServiceCompletion() {
        // Listen for the match dropdown to be populated
        const matchSelect = $('#match-select');
        
        // Use MutationObserver to watch for options being added to the dropdown
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Check if options were added (excluding the default "Select match" option)
                    const options = matchSelect.find('option:not([value=""]):not([value="Select match"])');
                    if (options.length > 0 && !this.currentMatchId) {
                        Utils.log(`Dropdown populated with ${options.length} matches, auto-selecting first match`, 'MATCH_ANALYSIS');
                        
                        // Auto-select the first match
                        const firstMatchId = options.first().val();
                        if (firstMatchId) {
                            matchSelect.val(firstMatchId).trigger('change.select2');
                            this.handleMatchSelection(firstMatchId);
                            
                            // Stop observing once we've auto-selected
                            observer.disconnect();
                        }
                    }
                }
            });
        });
        
        // Start observing the match dropdown for changes
        if (matchSelect.length > 0) {
            observer.observe(matchSelect[0], {
                childList: true,
                subtree: true
            });
            
            Utils.log('Started observing match dropdown for auto-selection', 'MATCH_ANALYSIS');
        }
    }

    /**
     * Render default dominance heatmap on load
     */
    renderDefaultHeatmap() {
        // Render the default dominance heatmap (full match view)
        const defaultHeatmapKey = 'dominance_heatmap';
        const containerId = 'dominance-plot-container';
        
        // Small delay to ensure container is ready
        setTimeout(() => {
            if (this.plotManager && this.plotManager.hasPlot(defaultHeatmapKey)) {
                this.plotManager.lazyRenderPlot(containerId, defaultHeatmapKey, true);
                Utils.log('Default dominance heatmap rendered on load', 'MATCH_ANALYSIS');
            } else {
                Utils.log(`Default heatmap data not available: ${defaultHeatmapKey}`, 'MATCH_ANALYSIS', 'warn');
            }
        }, AppConfig.UI.PLOT_RENDER_DELAY);
    }

    /**
     * Check for default match selection and load plots immediately
     * This runs after page initialization to handle cases where a match is already selected
     */
    checkAndLoadDefaultMatch() {
        // Use multiple attempts with increasing delays to ensure dropdowns are ready
        const checkForDefaultMatch = (attempt = 1, maxAttempts = 15) => {
            const matchSelect = $('#match-select');
            const currentValue = matchSelect.val();
            
            Utils.log(`Default match check attempt ${attempt}: current value = "${currentValue}"`, 'MATCH_ANALYSIS');
            
            // Check if we have a valid match selected and haven't already loaded it
            if (currentValue && 
                currentValue !== "" && 
                currentValue !== "Select match" && 
                !this.currentMatchId) {
                
                Utils.log(`Found default selected match: ${currentValue}, loading plots immediately...`, 'MATCH_ANALYSIS');
                this.handleMatchSelection(currentValue);
                return;
            }
            
            // If no match found yet and we haven't reached max attempts, try again
            if (attempt < maxAttempts) {
                setTimeout(() => checkForDefaultMatch(attempt + 1, maxAttempts), 500);
            } else {
                Utils.log('No default match found after all attempts - waiting for dropdown service to complete', 'MATCH_ANALYSIS', 'warn');
            }
        };
        
        // Start checking immediately, then with delays
        checkForDefaultMatch();
        
        Utils.log('Started checking for default match selection', 'MATCH_ANALYSIS');
    }

    /**
     * Get component instances
     */
    getComponents() {
        return {
            plotManager: this.plotManager,
            navigation: this.navigation,
            heatmapControls: this.heatmapControls,
            statsTable: this.statsTable
        };
    }
}

window.MatchAnalysisPage = MatchAnalysisPage;
