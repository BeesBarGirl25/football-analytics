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
            Utils.log(`Stats container not found for ${teamPrefix}`, 'STATS_TABLE', 'error');
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
        
        Utils.log(`Stats table populated for ${teamPrefix} (${teamName})`, 'STATS_TABLE');
    }

    /**
     * Load stats for a specific team
     */
    loadTeamStats(teamType) {
        if (!window.cachedPlots) {
            Utils.log('No cached plots available for team stats', 'STATS_TABLE', 'warn');
            return;
        }
        
        const statsKey = `${teamType}_stats`;
        if (window.cachedPlots[statsKey]) {
            this.populateTeamStatsTable(teamType, window.cachedPlots[statsKey]);
        } else {
            Utils.log(`${teamType} stats not available`, 'STATS_TABLE', 'warn');
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
        this.loadTeamStats(AppConfig.TEAMS.HOME);
        this.loadTeamStats(AppConfig.TEAMS.AWAY);
        Utils.log('All team stats loaded', 'STATS_TABLE');
    }

    /**
     * Refresh stats tables
     */
    refresh() {
        this.loadAllTeamStats();
    }

    /**
     * Show loading state for a team
     */
    showLoading(teamType, message = 'Loading stats...') {
        const container = document.getElementById(`${teamType}-stats-container`);
        if (container) {
            container.innerHTML = `<div class="stats-loading">${message}</div>`;
        }
    }

    /**
     * Show error state for a team
     */
    showError(teamType, message = 'Failed to load stats') {
        const container = document.getElementById(`${teamType}-stats-container`);
        if (container) {
            container.innerHTML = `<div class="stats-loading" style="color: #f44336;">${message}</div>`;
        }
    }

    /**
     * Clear all stats tables
     */
    clear() {
        [AppConfig.TEAMS.HOME, AppConfig.TEAMS.AWAY].forEach(teamType => {
            const container = document.getElementById(`${teamType}-stats-container`);
            if (container) {
                container.innerHTML = '<div class="stats-loading">Select a match to view stats</div>';
            }
        });
        Utils.log('Stats tables cleared', 'STATS_TABLE');
    }

    /**
     * Update highlight stats list
     */
    setHighlightStats(statNames) {
        this.highlightStats = statNames;
        Utils.log(`Highlight stats updated: ${statNames.join(', ')}`, 'STATS_TABLE');
    }

    /**
     * Get current highlight stats
     */
    getHighlightStats() {
        return [...this.highlightStats];
    }

    /**
     * Check if stats are available for a team
     */
    hasStatsForTeam(teamType) {
        if (!window.cachedPlots) return false;
        const statsKey = `${teamType}_stats`;
        return !!(window.cachedPlots[statsKey] && 
                 window.cachedPlots[statsKey].team_stats && 
                 window.cachedPlots[statsKey].team_stats.stats);
    }

    /**
     * Get stats data for a team
     */
    getTeamStatsData(teamType) {
        if (!window.cachedPlots) return null;
        const statsKey = `${teamType}_stats`;
        return window.cachedPlots[statsKey] || null;
    }

    /**
     * Initialize stats tables with default state
     */
    initialize() {
        this.clear();
        Utils.log('Stats table component initialized', 'STATS_TABLE');
    }
}

window.StatsTable = StatsTable;
