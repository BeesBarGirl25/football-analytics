const cachedPlots = {};
const renderedPlots = new Set();

// Track current selections for team heatmaps
const teamHeatmapState = {
  home_team: { phase: 'possession', half: 'full' },
  away_team: { phase: 'possession', half: 'full' }
};

function lazyRenderPlot(containerId, plotKey, force = false) {
  const el = document.getElementById(containerId);
  const plot = cachedPlots[plotKey];

  if (!el || (!force && renderedPlots.has(containerId))) return;

  setTimeout(() => {
    if (el.offsetWidth === 0 || el.offsetHeight === 0) {
      console.warn(`[DELAY] ${containerId} not visible yet. Skipping render.`);
      return;
    }
    try {
      Plotly.newPlot(containerId, plot.data, plot.layout);
      renderedPlots.add(containerId);
      console.log(`[LAZY PLOT] ✅ ${containerId} (${plotKey})`);
    } catch (err) {
      console.error(`[LAZY PLOT] ❌ Failed for ${containerId}`, err);
    }
  }, 100);
}


function showTabAndRenderPlot(tabId, viewKey, containerId, graphContainerId) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.analysis-content').forEach(content => content.classList.add('hidden'));

  const selectedTab = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
  const tabEl = document.getElementById(tabId);
  selectedTab?.classList.add('active');
  tabEl?.classList.remove('hidden');

  const graphEl = document.getElementById(graphContainerId);
  if (graphEl) {
    graphEl.classList.remove('hidden');
    console.log(`[SHOW] Unhiding graph container: ${graphContainerId}`);
  }

  const plotWrapper = document.getElementById(containerId);
  if (plotWrapper) {
    plotWrapper.classList.remove('hidden');
    console.log(`[SHOW] Unhiding plot wrapper: ${containerId}`);
  }

  // Unhide all containers with the matching data-plot-group
  const plotGroupElements = document.querySelectorAll(`[data-plot-group="${viewKey}"]`);
  plotGroupElements.forEach(el => {
    el.classList.remove('hidden');
    console.log(`[SHOW] Unhiding plot group element for: ${viewKey}`);
  });

  // Also ensure any nested elements are visible
  if (graphEl) {
    const nestedElements = graphEl.querySelectorAll('.hidden');
    nestedElements.forEach(el => {
      el.classList.remove('hidden');
      console.log(`[SHOW] Unhiding nested element`);
    });
  }

  requestAnimationFrame(() => {
    setTimeout(() => {
      console.log(`[SHOW] Rendering plot for ${containerId}`);
      lazyRenderPlot(containerId, viewKey);
    }, 20);
  });
}


// Tabs

document.querySelectorAll('.tab-btn').forEach(button => {
  button.addEventListener('click', () => {
    const tabId = button.getAttribute('data-tab');
    
    // Always update tab states first
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.analysis-content').forEach(content => content.classList.add('hidden'));
    button.classList.add('active');
    document.getElementById(tabId)?.classList.remove('hidden');
    
    if (tabId === 'home') {
      // Show home team container and render current heatmap
      const homeContainer = document.getElementById('graph-container-home-team-4');
      if (homeContainer) {
        homeContainer.classList.remove('hidden');
        console.log('[HOME TAB] Container shown, rendering heatmap');
      }
      
      // Render with current state
      setTimeout(() => renderCurrentTeamHeatmap('home_team'), 100);
      
    } else if (tabId === 'away') {
      // Show away team container and render current heatmap
      const awayContainer = document.getElementById('graph-container-away-team-4');
      if (awayContainer) {
        awayContainer.classList.remove('hidden');
        console.log('[AWAY TAB] Container shown, rendering heatmap');
      }
      
      // Render with current state
      setTimeout(() => renderCurrentTeamHeatmap('away_team'), 100);
      
    } else if (tabId === 'overview') {
      showTabAndRenderPlot(tabId, 'dominance_heatmap', 'dominance-plot-container', 'graph-container-heatmap');
    }
  });
});

// Helper function to render current team heatmap based on state
function renderCurrentTeamHeatmap(teamPrefix) {
  const state = teamHeatmapState[teamPrefix];
  const plotKey = `${teamPrefix}_${state.phase}_${state.half}`;
  
  // Determine container ID based on team
  const containerId = teamPrefix === 'home_team' ? 'heatmap-home-plot-container' : 'heatmap-away-plot-container';
  
  // Debug: Check if plot data exists
  if (!cachedPlots[plotKey]) {
    console.error(`[TEAM HEATMAP] Plot data missing for ${plotKey}`);
    console.log('[TEAM HEATMAP] Available plots:', Object.keys(cachedPlots));
    return;
  }
  
  // Debug: Check if container exists and is visible
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`[TEAM HEATMAP] Container ${containerId} not found`);
    return;
  }
  
  console.log(`[TEAM HEATMAP] Rendering ${plotKey} in ${containerId}`);
  console.log(`[TEAM HEATMAP] Container dimensions: ${container.offsetWidth}x${container.offsetHeight}`);
  
  setTimeout(() => lazyRenderPlot(containerId, plotKey, true), 50);
}

// Phase button handlers
document.addEventListener('click', (event) => {
  if (event.target.classList.contains('phase-btn')) {
    const button = event.target;
    const phaseButtons = button.closest('.phase-toggle-buttons');
    const teamPrefix = phaseButtons.getAttribute('data-team');
    
    // Update active states
    phaseButtons.querySelectorAll('.phase-btn').forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
    
    // Update state
    const newPhase = button.getAttribute('data-phase');
    teamHeatmapState[teamPrefix].phase = newPhase;
    
    // Check if container is visible before rendering
    const container = button.closest('.graph-container');
    if (!container || container.offsetParent === null) {
      console.log(`[SKIP] Phase change for ${teamPrefix} — container not visible`);
      return;
    }
    
    // Re-render with new combination
    renderCurrentTeamHeatmap(teamPrefix);
  }
});

// Half button handlers (updated to work with team heatmaps)
document.addEventListener('click', (event) => {
  if (event.target.classList.contains('toggle-btn')) {
    const button = event.target;
    const toggleButtons = button.closest('.heatmap-toggle-buttons, .dominance-toggle-buttons');
    
    // Update active states
    toggleButtons.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
    
    // Check if this is a team heatmap or dominance heatmap
    const teamPrefix = toggleButtons.getAttribute('data-team');
    
    if (teamPrefix) {
      // Team heatmap logic
      const newHalf = button.getAttribute('data-half');
      teamHeatmapState[teamPrefix].half = newHalf;
      
      // Check if container is visible before rendering
      const container = button.closest('.graph-container');
      if (!container || container.offsetParent === null) {
        console.log(`[SKIP] Half change for ${teamPrefix} — container not visible`);
        return;
      }
      
      renderCurrentTeamHeatmap(teamPrefix);
    } else {
      // Original dominance heatmap logic
      const viewKey = button.getAttribute('data-view');
      const container = button.closest('.graph-container');
      const containerId = container?.querySelector('.plotly-wrapper')?.id;

      if (!container || container.offsetParent === null) {
        console.log(`[SKIP] Toggle for ${viewKey} — container not visible`);
        return;
      }

      setTimeout(() => lazyRenderPlot(containerId, viewKey, true), 50);
    }
  }
});

// Match select

$('#match-select').on('change', async function () {
  const matchId = $(this).val();
  if (!matchId || matchId === "Select match") {
    console.warn("Skipping fetch: no valid match selected.");
    return;
  }

  try {
    const response = await fetch(`/api/plots/${matchId}`);
    if (!response.ok) throw new Error("Failed to fetch plot data");

    const result = await response.json();
    console.log("[DEBUG] Results: ", result);

    // Cache all plot data including new phase combinations
    Object.assign(cachedPlots, result);
    
    // Ensure backward compatibility keys are available
    Object.assign(cachedPlots, {
      dominance_heatmap: result.dominance_heatmap,
      dominance_heatmap_first: result.dominance_heatmap_first,
      dominance_heatmap_second: result.dominance_heatmap_second,
      home_team_heatmap: result.home_team_heatmap,
      home_team_heatmap_first: result.home_team_heatmap_first,
      home_team_heatmap_second: result.home_team_heatmap_second,
      away_team_heatmap: result.away_team_heatmap,
      away_team_heatmap_first: result.away_team_heatmap_first,
      away_team_heatmap_second: result.away_team_heatmap_second
    });

    renderedPlots.clear();

    ['graph-container-xg', 'graph-container-momentum', 'graph-container-summary', 'graph-container-heatmap']
      .forEach(id => document.getElementById(id)?.classList.remove('hidden'));

    if (result.xg_graph?.data && result.xg_graph?.layout) {
      Plotly.newPlot('xg-plot-container', result.xg_graph.data, result.xg_graph.layout);
    }

    if (result.momentum_graph?.data && result.momentum_graph?.layout) {
      Plotly.newPlot('momentum-plot-container', result.momentum_graph.data, result.momentum_graph.layout);
    }

    showTabAndRenderPlot('overview', 'dominance_heatmap', 'dominance-plot-container', 'graph-container-heatmap');

    const summary = result.match_summary;
    document.getElementById('home-team-name').textContent = summary.homeTeam ?? '–';
    document.getElementById('away-team-name').textContent = summary.awayTeam ?? '–';
    document.getElementById('home-team-score').textContent = summary.homeTeamNormalTime ?? '–';
    document.getElementById('away-team-score').textContent = summary.awayTeamNormalTime ?? '–';
    document.getElementById('score-seperator').textContent = '-';

    const extraDetails = document.getElementById('extra-details');
    if (summary.extraTimeDetails) {
      extraDetails.textContent = summary.extraTimeDetails;
      extraDetails.style.display = 'block';
    } else {
      extraDetails.style.display = 'none';
    }

    populateTable('home-team-table', summary.home);
    populateTable('away-team-table', summary.away);
  } catch (error) {
    console.error("[Error]: Failed to load plots or summary", error);
  }
});

function populateTable(tableId, players) {
  const tableBody = document.querySelector(`#${tableId} tbody`);
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
