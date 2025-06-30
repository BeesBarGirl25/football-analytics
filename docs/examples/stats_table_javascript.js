// Add these functions to static/js/match_analysis.js

/**
 * Populate team stats table
 * @param {string} teamPrefix - 'home_team' or 'away_team'
 * @param {Object} statsData - Team stats data from backend
 */
function populateTeamStatsTable(teamPrefix, statsData) {
    const container = document.getElementById(`${teamPrefix}-stats-container`);
    
    if (!container) {
        console.error(`Stats container not found for ${teamPrefix}`);
        return;
    }
    
    if (!statsData || !statsData.team_stats || !statsData.team_stats.stats) {
        container.innerHTML = '<div class="stats-loading">No stats available</div>';
        return;
    }
    
    const stats = statsData.team_stats.stats;
    const teamName = statsData.team_stats.team_name;
    
    // Create table HTML
    let tableHTML = `
        <table class="team-stats-table">
            <tbody>
    `;
    
    // Define which stats should be highlighted (key performance indicators)
    const highlightStats = ['Goals', 'Shots on Target', 'Passes', 'xG'];
    
    stats.forEach(stat => {
        const isHighlight = highlightStats.includes(stat.stat_name);
        const rowClass = isHighlight ? 'highlight-stat' : '';
        
        tableHTML += `
            <tr class="${rowClass}">
                <td class="stat-name">${stat.stat_name}</td>
                <td class="stat-value">${stat.value}</td>
            </tr>
        `;
    });
    
    tableHTML += `
            </tbody>
        </table>
    `;
    
    container.innerHTML = tableHTML;
}

/**
 * Load and display team stats for both teams
 */
function loadTeamStats() {
    if (!cachedPlots) {
        console.log('No cached plots available for team stats');
        return;
    }
    
    // Load home team stats
    if (cachedPlots['home_team_stats']) {
        populateTeamStatsTable('home_team', cachedPlots['home_team_stats']);
    } else {
        console.log('Home team stats not available');
        const homeContainer = document.getElementById('home_team-stats-container');
        if (homeContainer) {
            homeContainer.innerHTML = '<div class="stats-loading">Stats not available</div>';
        }
    }
    
    // Load away team stats
    if (cachedPlots['away_team_stats']) {
        populateTeamStatsTable('away_team', cachedPlots['away_team_stats']);
    } else {
        console.log('Away team stats not available');
        const awayContainer = document.getElementById('away_team-stats-container');
        if (awayContainer) {
            awayContainer.innerHTML = '<div class="stats-loading">Stats not available</div>';
        }
    }
}

// Update the existing loadPlots function to include team stats
function loadPlots() {
    // ... existing plot loading code ...
    
    // Load team stats after other plots are loaded
    loadTeamStats();
    
    // ... rest of existing code ...
}

// Alternative: Add to the existing plot loading logic
// If you have a specific function that handles team tab activation, add this there:
function onTeamTabActivated(teamType) {
    // ... existing team tab logic ...
    
    // Load stats for the activated team
    const statsKey = `${teamType}_stats`;
    if (cachedPlots && cachedPlots[statsKey]) {
        populateTeamStatsTable(teamType, cachedPlots[statsKey]);
    }
}

// Example usage in your existing tab switching logic:
// When home tab is clicked:
// onTeamTabActivated('home_team');
// When away tab is clicked:
// onTeamTabActivated('away_team');
