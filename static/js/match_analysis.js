const cachedPlots = {
    dominance: {},
    heatmap_home: {},
    heatmap_away: {}
};

function renderPlot(containerId, plot) {
    if (plot?.data && plot?.layout) {
        Plotly.newPlot(containerId, plot.data, plot.layout);
        console.log(`[PLOT] Rendered in: ${containerId}`);
    } else {
        console.warn(`[PLOT] Missing data for: ${containerId}`);
    }
}

function togglePlotView(viewKey, plotGroup, containerId) {
    const plot = cachedPlots[plotGroup][viewKey];
    renderPlot(containerId, plot);
}

// ✅ Toggle tab visibility and re-render if needed
document.querySelectorAll('.tab-btn').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.analysis-content').forEach(content => content.classList.add('hidden'));

        button.classList.add('active');
        const tabId = button.getAttribute('data-tab');
        const targetTab = document.getElementById(tabId);
        targetTab.classList.remove('hidden');

        // ✅ Remove hidden class from container inside tab
        if (tabId === 'home') {
            document.getElementById('graph-container-home-team-4')?.classList.remove('hidden');
        } else if (tabId === 'away') {
            document.getElementById('graph-container-away-team-4')?.classList.remove('hidden');
        }

        // ✅ Re-render plot now that container is visible
        setTimeout(() => {
            if (tabId === 'home') {
                togglePlotView('heatmap_heatmap_full', 'heatmap_home', 'heatmap-home-plot-container');
            } else if (tabId === 'away') {
                togglePlotView('heatmap_heatmap_full', 'heatmap_away', 'heatmap-away-plot-container');
            }
        }, 100);
    });
});


// Generic toggle buttons for plot sections
document.querySelectorAll('.toggle-btn').forEach(button => {
    button.addEventListener('click', () => {
        const allButtons = button.closest('.heatmap-toggle-buttons, .dominance-toggle-buttons');
        if (allButtons) {
            allButtons.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
        }
        button.classList.add('active');

        const viewKey = button.getAttribute('data-view');
        const plotGroup = button.closest('.graph-container').dataset.plotGroup;
        const containerId = button.closest('.graph-container').querySelector('.plotly-wrapper').id;

        togglePlotView(viewKey, plotGroup, containerId);
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

        const { xg_graph, momentum_graph, match_summary } = result;

        cachedPlots.dominance = {
            dominance_heatmap_full: result.dominance_heatmap,
            dominance_heatmap_first: result.dominance_heatmap_first,
            dominance_heatmap_second: result.dominance_heatmap_second
        };

        cachedPlots.heatmap_home = {
            heatmap_heatmap_full: result.home_team_heatmap,
            heatmap_heatmap_first: result.home_team_heatmap_first,
            heatmap_heatmap_second: result.home_team_heatmap_second
        };

        cachedPlots.heatmap_away = {
            heatmap_heatmap_full: result.away_team_heatmap,
            heatmap_heatmap_first: result.away_team_heatmap_first,
            heatmap_heatmap_second: result.away_team_heatmap_second
        };

        [1, 2, 3, 4].forEach(i => {
            const el = document.getElementById(`graph-container-${i}`);
            if (el) el.classList.remove('hidden');
        });

        if (xg_graph?.data && xg_graph?.layout) {
            Plotly.newPlot('graph-container-1', xg_graph.data, xg_graph.layout);
        }

        if (momentum_graph?.data && momentum_graph?.layout) {
            Plotly.newPlot('graph-container-3', momentum_graph.data, momentum_graph.layout);
        }

        togglePlotView('dominance_heatmap_full', 'dominance', 'dominance-plot-container');
        togglePlotView('heatmap_heatmap_full', 'heatmap_home', 'heatmap-home-plot-container');
        togglePlotView('heatmap_heatmap_full', 'heatmap_away', 'heatmap-away-plot-container');

        const summary = match_summary;
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
