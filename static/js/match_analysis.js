// Backward compatibility layer for match_analysis.js
// This file maintains the original global variables and functions
// while delegating to the new modular system

console.warn('Using compatibility layer for match_analysis.js - consider updating to use the new modular system');

// Global variables for backward compatibility
let cachedPlots = {};
let renderedPlots = new Set();
let teamHeatmapState = {
  home_team: { phase: 'possession', half: 'full' },
  away_team: { phase: 'possession', half: 'full' }
};

// Wait for the new app to be ready
function waitForApp(callback) {
  if (window.app && window.app.isReady()) {
    callback();
  } else {
    setTimeout(() => waitForApp(callback), 100);
  }
}

// Legacy function implementations that delegate to new system
function lazyRenderPlot(containerId, plotKey, force = false) {
  waitForApp(() => {
    const plotManager = window.app.getComponent('plotManager');
    if (plotManager) {
      plotManager.lazyRenderPlot(containerId, plotKey, force);
    }
  });
}

function showTabAndRenderPlot(tabId, viewKey, containerId, graphContainerId) {
  waitForApp(() => {
    const navigation = window.app.getComponent('navigation');
    if (navigation) {
      navigation.switchTab(tabId);
    }
  });
}

function renderCurrentTeamHeatmap(teamPrefix) {
  waitForApp(() => {
    const plotManager = window.app.getComponent('plotManager');
    if (plotManager) {
      plotManager.renderCurrentTeamHeatmap(teamPrefix);
    }
  });
}

function populateTable(tableId, players) {
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
}

// Keep global variables in sync with the new system
document.addEventListener('DOMContentLoaded', () => {
  // Update global variables when app is ready
  const updateGlobals = () => {
    if (window.app && window.app.isReady()) {
      const plotManager = window.app.getComponent('plotManager');
      if (plotManager) {
        // Keep cachedPlots in sync
        cachedPlots = plotManager.cachedPlots || {};
        window.cachedPlots = cachedPlots;
        
        // Keep teamHeatmapState in sync
        teamHeatmapState = plotManager.teamHeatmapState || teamHeatmapState;
        window.teamHeatmapState = teamHeatmapState;
        
        // Keep renderedPlots in sync
        renderedPlots = plotManager.renderedPlots || new Set();
        window.renderedPlots = renderedPlots;
      }
    }
    
    // Check again in 1 second
    setTimeout(updateGlobals, 1000);
  };
  
  updateGlobals();
});

// Export for backward compatibility
window.cachedPlots = cachedPlots;
window.renderedPlots = renderedPlots;
window.teamHeatmapState = teamHeatmapState;
window.lazyRenderPlot = lazyRenderPlot;
window.showTabAndRenderPlot = showTabAndRenderPlot;
window.renderCurrentTeamHeatmap = renderCurrentTeamHeatmap;
window.populateTable = populateTable;
