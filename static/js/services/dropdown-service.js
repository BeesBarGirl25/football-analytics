// Dropdown service for managing competition, season, and match dropdowns
class DropdownService {
    constructor() {
        this.cache = {
            competitions: null,
            seasons: {},
            matches: {}
        };
        this.isInitialized = false;
    }

    /**
     * Initialize the dropdown service
     */
    async initialize() {
        if (this.isInitialized) return;

        try {
            // Initialize Select2 for better UX
            this.initializeSelect2();
            
            // Load initial data
            await this.loadCompetitions();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Auto-select first options for better UX (if enabled)
            if (AppConfig.DROPDOWNS.AUTO_SELECT_DEFAULTS) {
                await this.autoSelectDefaults();
            }
            
            this.isInitialized = true;
            Utils.log('Dropdown service initialized with default selections', 'DROPDOWN_SERVICE');
            
        } catch (error) {
            Utils.log(`Failed to initialize dropdown service: ${error.message}`, 'DROPDOWN_SERVICE', 'error');
        }
    }

    /**
     * Initialize Select2 dropdowns
     */
    initializeSelect2() {
        $('.searchable-dropdown').select2({
            dropdownParent: $('.content'),
            placeholder: function() {
                return $(this).data('placeholder') || 'Select option';
            },
            allowClear: true
        });
        
        Utils.log('Select2 initialized', 'DROPDOWN_SERVICE');
    }

    /**
     * Load competitions from API
     */
    async loadCompetitions() {
        if (this.cache.competitions) {
            this.populateCompetitionDropdown(this.cache.competitions);
            return;
        }

        try {
            Utils.log('Loading competitions...', 'DROPDOWN_SERVICE');
            
            const response = await fetch('/api/competitions');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Get unique competitions
            const uniqueCompetitions = [...new Set(data.map(d => d.competition_name))];
            
            // Cache the full data for later use
            this.cache.competitions = data;
            
            // Populate dropdown
            this.populateCompetitionDropdown(uniqueCompetitions);
            
            Utils.log(`✅ Loaded ${uniqueCompetitions.length} competitions`, 'DROPDOWN_SERVICE');
            
        } catch (error) {
            Utils.log(`❌ Error fetching competitions: ${error.message}`, 'DROPDOWN_SERVICE', 'error');
            this.showDropdownError('competition-select', 'Failed to load competitions');
        }
    }

    /**
     * Populate competition dropdown
     */
    populateCompetitionDropdown(competitions) {
        const dropdown = $('#competition-select');
        dropdown.empty().append('<option value="">Select competition</option>');
        
        competitions.forEach(name => {
            dropdown.append(`<option value="${name}">${name}</option>`);
        });
        
        // Trigger Select2 update
        dropdown.trigger('change.select2');
    }

    /**
     * Load seasons for selected competition
     */
    async loadSeasons(competitionName) {
        if (!competitionName) {
            this.clearDropdown('season-select', 'Select season');
            this.clearDropdown('match-select', 'Select match');
            return;
        }

        // Check cache first
        if (this.cache.seasons[competitionName]) {
            this.populateSeasonDropdown(this.cache.seasons[competitionName]);
            return;
        }

        try {
            Utils.log(`Loading seasons for ${competitionName}...`, 'DROPDOWN_SERVICE');
            
            // Use cached competition data if available
            if (this.cache.competitions) {
                const filtered = this.cache.competitions.filter(d => d.competition_name === competitionName);
                this.cache.seasons[competitionName] = filtered;
                this.populateSeasonDropdown(filtered);
                Utils.log(`✅ Loaded ${filtered.length} seasons for ${competitionName}`, 'DROPDOWN_SERVICE');
            } else {
                // Fallback to API call
                const response = await fetch('/api/competitions');
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                const filtered = data.filter(d => d.competition_name === competitionName);
                
                this.cache.seasons[competitionName] = filtered;
                this.populateSeasonDropdown(filtered);
                Utils.log(`✅ Loaded ${filtered.length} seasons for ${competitionName}`, 'DROPDOWN_SERVICE');
            }
            
        } catch (error) {
            Utils.log(`❌ Error fetching seasons: ${error.message}`, 'DROPDOWN_SERVICE', 'error');
            this.showDropdownError('season-select', 'Failed to load seasons');
        }
    }

    /**
     * Populate season dropdown
     */
    populateSeasonDropdown(seasons) {
        const dropdown = $('#season-select');
        dropdown.empty().append('<option value="">Select season</option>');
        
        seasons.forEach(entry => {
            dropdown.append(`<option value="${entry.season_id}">${entry.season_name}</option>`);
        });
        
        // Clear matches dropdown
        this.clearDropdown('match-select', 'Select match');
        
        // Trigger Select2 update
        dropdown.trigger('change.select2');
    }

    /**
     * Load matches for selected season
     */
    async loadMatches(seasonId) {
        if (!seasonId) {
            this.clearDropdown('match-select', 'Select match');
            return;
        }

        // Check cache first
        if (this.cache.matches[seasonId]) {
            this.populateMatchDropdown(this.cache.matches[seasonId]);
            return;
        }

        try {
            Utils.log(`Loading matches for season ${seasonId}...`, 'DROPDOWN_SERVICE');
            
            const response = await fetch(`/api/matches/${seasonId}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const matches = await response.json();
            
            // Cache matches
            this.cache.matches[seasonId] = matches;
            
            // Populate dropdown
            this.populateMatchDropdown(matches);
            
            Utils.log(`✅ Loaded ${matches.length} matches for season ${seasonId}`, 'DROPDOWN_SERVICE');
            
        } catch (error) {
            Utils.log(`❌ Error fetching matches: ${error.message}`, 'DROPDOWN_SERVICE', 'error');
            this.showDropdownError('match-select', 'Failed to load matches');
        }
    }

    /**
     * Populate match dropdown
     */
    populateMatchDropdown(matches) {
        const dropdown = $('#match-select');
        dropdown.empty().append('<option value="">Select match</option>');
        
        matches.forEach(match => {
            const displayText = `${match.home_team} vs ${match.away_team}`;
            dropdown.append(`<option value="${match.match_id}">${displayText}</option>`);
        });
        
        // Trigger Select2 update
        dropdown.trigger('change.select2');
    }

    /**
     * Clear dropdown and set placeholder
     */
    clearDropdown(dropdownId, placeholder) {
        const dropdown = $(`#${dropdownId}`);
        dropdown.empty().append(`<option value="">${placeholder}</option>`);
        dropdown.trigger('change.select2');
    }

    /**
     * Show error in dropdown
     */
    showDropdownError(dropdownId, errorMessage) {
        const dropdown = $(`#${dropdownId}`);
        dropdown.empty().append(`<option value="">${errorMessage}</option>`);
        dropdown.trigger('change.select2');
    }

    /**
     * Set up event listeners for dropdowns
     */
    setupEventListeners() {
        // Competition selection
        $('#competition-select').on('change', async (event) => {
            const selectedCompetition = $(event.target).val();
            await this.loadSeasons(selectedCompetition);
        });

        // Season selection
        $('#season-select').on('change', async (event) => {
            const seasonId = $(event.target).val();
            await this.loadMatches(seasonId);
        });

        Utils.log('Event listeners set up', 'DROPDOWN_SERVICE');
    }

    /**
     * Get selected values
     */
    getSelectedValues() {
        return {
            competition: $('#competition-select').val(),
            season: $('#season-select').val(),
            match: $('#match-select').val()
        };
    }

    /**
     * Set selected values programmatically
     */
    async setSelectedValues(values) {
        if (values.competition) {
            $('#competition-select').val(values.competition).trigger('change');
            await this.loadSeasons(values.competition);
        }
        
        if (values.season) {
            $('#season-select').val(values.season).trigger('change');
            await this.loadMatches(values.season);
        }
        
        if (values.match) {
            $('#match-select').val(values.match).trigger('change');
        }
    }

    /**
     * Clear all selections
     */
    clearAllSelections() {
        $('#competition-select').val('').trigger('change');
        this.clearDropdown('season-select', 'Select season');
        this.clearDropdown('match-select', 'Select match');
        Utils.log('All selections cleared', 'DROPDOWN_SERVICE');
    }

    /**
     * Refresh all dropdowns
     */
    async refresh() {
        // Clear cache
        this.cache = {
            competitions: null,
            seasons: {},
            matches: {}
        };
        
        // Reload competitions
        await this.loadCompetitions();
        
        Utils.log('Dropdowns refreshed', 'DROPDOWN_SERVICE');
    }

    /**
     * Auto-select default values (first available option in each dropdown)
     */
    async autoSelectDefaults() {
        try {
            Utils.log('Auto-selecting default dropdown values...', 'DROPDOWN_SERVICE');
            
            // Auto-select first competition
            const competitionDropdown = $('#competition-select');
            const firstCompetition = competitionDropdown.find('option:not([value=""])').first().val();
            
            if (firstCompetition) {
                competitionDropdown.val(firstCompetition).trigger('change.select2');
                Utils.log(`Auto-selected competition: ${firstCompetition}`, 'DROPDOWN_SERVICE');
                
                // Load seasons for the selected competition
                await this.loadSeasons(firstCompetition);
                
                // Small delay to ensure seasons are loaded
                await new Promise(resolve => setTimeout(resolve, AppConfig.DROPDOWNS.SELECTION_DELAY));
                
                // Auto-select first season
                const seasonDropdown = $('#season-select');
                const firstSeason = seasonDropdown.find('option:not([value=""])').first().val();
                
                if (firstSeason) {
                    seasonDropdown.val(firstSeason).trigger('change.select2');
                    Utils.log(`Auto-selected season: ${firstSeason}`, 'DROPDOWN_SERVICE');
                    
                    // Load matches for the selected season
                    await this.loadMatches(firstSeason);
                    
                    // Small delay to ensure matches are loaded
                    await new Promise(resolve => setTimeout(resolve, AppConfig.DROPDOWNS.SELECTION_DELAY));
                    
                    // Auto-select first match
                    const matchDropdown = $('#match-select');
                    const firstMatch = matchDropdown.find('option:not([value=""])').first().val();
                    
                    if (firstMatch) {
                        matchDropdown.val(firstMatch).trigger('change.select2');
                        Utils.log(`Auto-selected match: ${firstMatch}`, 'DROPDOWN_SERVICE');
                        
                        // Trigger the match selection event for any page-specific handlers
                        matchDropdown.trigger('change');
                    }
                }
            }
            
            Utils.log('✅ Default selections completed', 'DROPDOWN_SERVICE');
            
        } catch (error) {
            Utils.log(`❌ Error auto-selecting defaults: ${error.message}`, 'DROPDOWN_SERVICE', 'error');
        }
    }

    /**
     * Get cached data
     */
    getCachedData() {
        return {
            competitions: this.cache.competitions,
            seasons: Object.keys(this.cache.seasons).length,
            matches: Object.keys(this.cache.matches).length
        };
    }
}

window.DropdownService = DropdownService;
