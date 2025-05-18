$('#match-select').on('change', async function () {
    const matchId = $(this).val();
    console.log("Match selected, ID:", matchId);

    try {
        const response = await fetch(`/api/plots/${matchId}`);
        if (!response.ok) throw new Error("Failed to fetch plot data");

        const result = await response.json();

        // Use fields directly (they're already JSON)
        const xg = result.xg_graph;
        const momentum = result.momentum_graph;
        const summary = result.match_summary;

        // Show containers
        document.getElementById('graph-container-1').classList.remove('hidden');
        document.getElementById('graph-container-2').classList.remove('hidden');
        document.getElementById('graph-container-3').classList.remove('hidden');

        // Render xG graph
        if (xg?.data && xg?.layout) {
            Plotly.newPlot('graph-container-1', xg.data, xg.layout);
            console.log("[Debug]: xG graph rendered");
        } else {
            console.warn("[Warning]: xG graph data missing");
        }

        // Render momentum graph
        if (momentum?.data && momentum?.layout) {
            Plotly.newPlot('graph-container-3', momentum.data, momentum.layout);
            console.log("[Debug]: Momentum graph rendered");
        } else {
            console.warn("[Warning]: Momentum graph data missing");
        }

        // Populate match summary
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
