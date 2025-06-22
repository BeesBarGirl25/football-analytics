// match_analysis.js — Render plots only when tabs are clicked

const cachedPlots = {};

function renderPlot(containerId, plot, attempts = 0) {
    const el = document.getElementById(containerId);
    console.log(`[RENDER ATTEMPT] ${containerId}, attempt ${attempts}`);
    if (!el) {
        console.warn(`[PLOT] Skipped rendering: ${containerId} (element not found)`);
        return;
    }

    const isVisible = el.offsetWidth > 0 && el.offsetHeight > 0 && !el.classList.contains('hidden');
    if (!isVisible) {
        if (attempts < 10) {
            console.log(`[WAIT] ${containerId} not yet visible, retrying... (${attempts})`);
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

function togglePlotView(viewKey, containerId) {
    // Diagnostic trace
    if (viewKey === 'home_team_heatmap') {
        console.trace(`[TRACE] togglePlotView called for ${viewKey}`);
    }

    const plot = cachedPlots[viewKey];
    const el = document.getElementById(containerId);

    const isVisible = el?.offsetHeight > 0 && el?.offsetWidth > 0 && !el.classList.contains('hidden');
    if (!isVisible) {
        console.log(`[SKIP] togglePlotView skipped for ${containerId} — not visible`);
        return;
    }

    renderPlot(containerId, plot);
}

function showTabAndRenderPlot(tabId, viewKey, containerId, graphContainerId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.analysis-content').forEach(content => content.classList.add('hidden'));

    const selectedTab = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    const tabEl = document.getElementById(tabId);
    const graphEl = document.getElementById(graphContainerId);

    selectedTab?.classList.add('active');
    tabEl?.classList.remove('hidden');

    requestAnimationFrame(() => {
        graphEl?.classList.remove('hidden');
        setTimeout(() => {
            togglePlotView(viewKey, containerId);
            const el = document.getElementById(containerId);
            if (el) Plotly.Plots.resize(el);
        }, 0);
    });
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

        if (container?.offsetHeight > 0 && container?.offsetWidth > 0 && !container.classList.contains('hidden')) {
            requestAnimationFrame(() => {
                togglePlotView(viewKey, containerId);
            });
        } else {
            console.log(`[SKIP] Toggle for ${viewKey} skipped — container not visible`);
        }
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

        document.getElementById('graph-container-xg')?.classList.remove('hidden');
        document.getElementById('graph-container-momentum')?.classList.remove('hidden');
        document.getElementById('graph-container-summary')?.classList.remove('hidden');
        document.getElementById('graph-container-heatmap')?.classList.remove('hidden');

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
