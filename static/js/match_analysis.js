// match_analysis.js — Refactored with flat plot cache and simplified logic

const cachedPlots = {};

function renderPlot(containerId, plot) {
    const el = document.getElementById(containerId);

    console.log(`[PLOT] Preparing to render in: ${containerId}`);
    if (!el || el.offsetWidth === 0 || el.offsetHeight === 0 || el.classList.contains('hidden')) {
        console.warn(`[PLOT] Skipped rendering: ${containerId} (container not visible or missing)`);
        return;
    }

    if (plot?.data && plot?.layout) {
        try {
            console.log(`[PLOT] Rendering plot:`, {
                containerId,
                dataLength: plot.data.length,
                layoutKeys: Object.keys(plot.layout)
            });
            Plotly.newPlot(containerId, plot.data, plot.layout);
            console.log(`[PLOT] Successfully rendered: ${containerId}`);
        } catch (err) {
            console.error(`[PLOT] ❌ Failed to render in: ${containerId}`, err);
            console.log('[PLOT] Plot data preview:', plot.data);
            console.log('[PLOT] Plot layout preview:', plot.layout);
        }
    } else {
        console.warn(`[PLOT] Missing data/layout for: ${containerId}`);
    }
}


function togglePlotView(viewKey, containerId) {
    const plot = cachedPlots[viewKey];
    renderPlot(containerId, plot);
}

document.querySelectorAll('.tab-btn').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.analysis-content').forEach(content => content.classList.add('hidden'));

        button.classList.add('active');
        const tabId = button.getAttribute('data-tab');
        const targetTab = document.getElementById(tabId);
        targetTab.classList.remove('hidden');

        if (tabId === 'home') {
            document.getElementById('graph-container-home-team-4')?.classList.remove('hidden');
        } else if (tabId === 'away') {
            document.getElementById('graph-container-away-team-4')?.classList.remove('hidden');
        }

        setTimeout(() => {
            const containerId = tabId === 'home' ? 'heatmap-home-plot-container' : 'heatmap-away-plot-container';
            const viewKey = tabId === 'home' ? 'home_team_heatmap' : 'away_team_heatmap';

            const el = document.getElementById(containerId);
            if (el.offsetWidth > 0 && el.offsetHeight > 0) {
                togglePlotView(viewKey, containerId);
            } else {
                setTimeout(() => togglePlotView(viewKey, containerId), 100);
            }
        }, 150);
    });
});

document.querySelectorAll('.toggle-btn').forEach(button => {
    button.addEventListener('click', () => {
        const allButtons = button.closest('.heatmap-toggle-buttons, .dominance-toggle-buttons');
        if (allButtons) {
            allButtons.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
        }
        button.classList.add('active');

        const viewKey = button.getAttribute('data-view');
        const containerId = button.closest('.graph-container').querySelector('.plotly-wrapper').id;

        togglePlotView(viewKey, containerId);
    });
});

$('#match-select').on('change', async function () {
    const matchId = $(this).val();
    console.log("Match selected, ID:", matchId);

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

        [1, 2, 3, 4].forEach(i => {
            const el = document.getElementById(`graph-container-${i}`);
            if (el) el.classList.remove('hidden');
        });

        if (result.xg_graph?.data && result.xg_graph?.layout) {
            Plotly.newPlot('graph-container-1', result.xg_graph.data, result.xg_graph.layout);
        }

        if (result.momentum_graph?.data && result.momentum_graph?.layout) {
            Plotly.newPlot('graph-container-3', result.momentum_graph.data, result.momentum_graph.layout);
        }

        togglePlotView('dominance_heatmap', 'dominance-plot-container');
        togglePlotView('home_team_heatmap', 'heatmap-home-plot-container');
        togglePlotView('away_team_heatmap', 'heatmap-away-plot-container');

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
