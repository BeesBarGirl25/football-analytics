const cachedPlots = {};

function printVisibility(el, label) {
  console.log(`[VISIBILITY] ${label} — exists: ${!!el}, width: ${el?.offsetWidth}, height: ${el?.offsetHeight}, hiddenClass: ${el?.classList.contains('hidden')}`);
}

function renderPlot(containerId, plot, attempts = 0) {
  const el = document.getElementById(containerId);
  console.log(`[RENDER ATTEMPT] ${containerId}, attempt ${attempts}`);
  printVisibility(el, containerId);

  if (!el || el.offsetWidth === 0 || el.offsetHeight === 0 || el.classList.contains('hidden')) {
    if (attempts < 10) {
      console.log(`[WAIT] renderPlot retry (${attempts + 1})…`);
      setTimeout(() => renderPlot(containerId, plot, attempts + 1), 100);
    } else {
      console.warn(`[PLOT] Skipped rendering: ${containerId} after ${attempts} attempts`);
    }
    return;
  }

  if (plot?.data && plot?.layout) {
    try {
      Plotly.newPlot(containerId, plot.data, plot.layout);
      console.log(`[PLOT] ✅ Rendered successfully: ${containerId}`);
    } catch (err) {
      console.error(`[PLOT] ❌ Failed to render in: ${containerId}`, err);
    }
  } else {
    console.warn(`[PLOT] Missing data/layout for: ${containerId}`);
  }
}

function togglePlotView(viewKey, containerId, attempts = 0) {
  const plot = cachedPlots[viewKey];
  const el = document.getElementById(containerId);
  printVisibility(el, containerId);

  if (!el || el.offsetWidth === 0 || el.offsetHeight === 0 || el.classList.contains('hidden')) {
    if (attempts < 10) {
      console.log(`[WAIT] togglePlotView retry (${attempts + 1})…`);
      setTimeout(() => togglePlotView(viewKey, containerId, attempts + 1), 100);
    } else {
      console.warn(`[SKIP] togglePlotView aborted after ${attempts} attempts`);
    }
    return;
  }

  renderPlot(containerId, plot);
}

function showTabAndRenderPlot(tabId, viewKey, containerId, graphContainerId) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.analysis-content').forEach(content => content.classList.add('hidden'));

  const selectedTab = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
  const tabEl = document.getElementById(tabId);

  selectedTab?.classList.add('active');
  tabEl?.classList.remove('hidden'); // Must be unhidden *first* so children can become visible

  // Now access elements *within* tabEl
  const graphEl = tabEl?.querySelector(`#${graphContainerId}`);
  const plotWrapper = tabEl?.querySelector(`#${containerId}`);

  graphEl?.classList.remove('hidden');
  plotWrapper?.classList.remove('hidden');

  setTimeout(() => {
    requestAnimationFrame(() => {
      console.log(`[SHOW] Rendering plot for ${containerId}`);
      togglePlotView(viewKey, containerId);
      const el = document.getElementById(containerId);
      if (el) Plotly.Plots.resize(el);
    });
  }, 100);
}



// Tabs
document.querySelectorAll('.tab-btn').forEach(button => {
  button.addEventListener('click', () => {
    const tabId = button.getAttribute('data-tab');
    if (tabId === 'home') {
      showTabAndRenderPlot(tabId, 'home_team_heatmap', 'heatmap-home-plot-container', 'graph-container-home-team-4');
    } else if (tabId === 'away') {
      showTabAndRenderPlot(tabId, 'away_team_heatmap', 'heatmap-away-plot-container', 'graph-container-away-team-4');
    } else if (tabId === 'overview') {
      showTabAndRenderPlot(tabId, 'dominance_heatmap', 'dominance-plot-container', 'graph-container-4');
    } else {
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('.analysis-content').forEach(content => content.classList.add('hidden'));
      button.classList.add('active');
      document.getElementById(tabId)?.classList.remove('hidden');
    }
  });
});

// Toggle buttons
document.querySelectorAll('.toggle-btn').forEach(button => {
  button.addEventListener('click', () => {
    const allButtons = button.closest('.heatmap-toggle-buttons, .dominance-toggle-buttons');
    if (allButtons) {
      allButtons.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
    }
    button.classList.add('active');

    const viewKey = button.getAttribute('data-view');
    const container = button.closest('.graph-container');
    const containerId = container?.querySelector('.plotly-wrapper')?.id;

    if (!container || container.offsetParent === null) {
      console.log(`[SKIP] Toggle for ${viewKey} — container not visible`);
      return;
    }

    setTimeout(() => togglePlotView(viewKey, containerId), 50);
  });
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

    ['graph-container-xg', 'graph-container-momentum', 'graph-container-summary', 'graph-container-heatmap']
      .forEach(id => document.getElementById(id)?.classList.remove('hidden'));

    if (result.xg_graph?.data && result.xg_graph?.layout) {
      Plotly.newPlot('xg-plot-container', result.xg_graph.data, result.xg_graph.layout);
    }

    if (result.momentum_graph?.data && result.momentum_graph?.layout) {
      Plotly.newPlot('momentum-plot-container', result.momentum_graph.data, result.momentum_graph.layout);
    }

    showTabAndRenderPlot('overview', 'dominance_heatmap', 'dominance-plot-container', 'graph-container-4');

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
