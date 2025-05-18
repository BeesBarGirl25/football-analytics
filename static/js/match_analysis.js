// Event listener - Match dropdown
$('#match-select').on('change', async function () {
    const matchId = $(this).val();
    console.log("Match selected, ID:", matchId);

    try {
        // Fetch pre-generated plot data from new endpoint
        const response = await fetch(`/api/plots/${matchId}`);
        if (!response.ok) throw new Error("Failed to fetch plot data");

        const result = await response.json();

        const xg = JSON.parse(result.xg_graph_json);
        const momentum = JSON.parse(result.momentum_graph_json);
        const summary = JSON.parse(result.match_summary_json);

        // Show containers
        document.getElementById('graph-container-1').classList.remove('hidden');
        document.getElementById('graph-container-2').classList.remove('hidden');
        document.getElementById('graph-container-3').classList.remove('hidden');

        // Render xG graph
        Plotly.newPlot('graph-container-1', xg.data, xg.layout);
        console.log("[Debug]: xG graph rendered");

        // Render momentum graph
        Plotly.newPlot('graph-container-3', momentum.data, momentum.layout);
        console.log("[Debug]: Momentum graph rendered");

        // Populate match summary
        document.getElementById('home-team-name').textContent = summary.homeTeam;
        document.getElementById('away-team-name').textContent = summary.awayTeam;
        document.getElementById('home-team-score').textContent = summary.homeTeamNormalTime;
        document.getElementById('away-team-score').textContent = summary.awayTeamNormalTime;
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
        contribCell.textContent = player.contributions.join('');
        row.appendChild(playerCell);
        row.appendChild(contribCell);
        tableBody.appendChild(row);
    });
}
