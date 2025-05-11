// Global cache for match data
const matchDataCache = {};

// Helper functions for caching with localStorage
function cacheMatchDataLocally(matchId, data) {
    localStorage.setItem(`match_${matchId}`, JSON.stringify(data));
}

function getCachedMatchDataLocally(matchId) {
    const data = localStorage.getItem(`match_${matchId}`);
    return data ? JSON.parse(data) : null;
}

// Fetch match data from API or cache
async function fetchMatchData(matchId) {
    // Step 1: Check if the match data is already cached in the browser
    if (matchDataCache[matchId]) {
        console.log(`[Cache Hit]: Using cached data for matchId: ${matchId}`);
        return matchDataCache[matchId]; // Return the cached data
    }

    // Step 2: If data is not cached, fetch it from the backend API
    console.log(`[Cache Miss]: Fetching data for matchId: ${matchId} from API...`);
    try {
        const response = await fetch(`/api/events/${matchId}`); // Backend route

        // Handle errors in API call
        if (!response.ok) {
            throw new Error(`Failed to fetch match data for matchId: ${matchId}`);
        }

        // Parse and store the response data
        const matchData = await response.json();

        // Step 3: Cache the fetched data for future use in this session
        matchDataCache[matchId] = matchData;

        return matchData;
    } catch (error) {
        console.error(`[Error]: Unable to fetch match data for matchId: ${matchId}`, error);
        throw error;
    }
}

async function renderGraph(matchData) {
    try {
        // Fetch the graph data from the backend
        const response = await fetch('/api/generate_match_graph', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ matchData }), // Post matchData (if applicable)
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch graph: ${response.status}`);
        }

        // Parse the JSON response from the backend
        const result = await response.json();
        // Deserialize the graph JSON
        const graph = JSON.parse(result); // Parse the graph string into JSON objects
        // Verify that data and layout exist
        if (!graph.data || !graph.layout) {
            throw new Error("Graph data or layout is missing!");
        }

        // Render the graph using Plotly
        Plotly.newPlot('graph-container-1', graph.data, graph.layout);
        console.log("[Debug]: Graph rendered successfully.");
    } catch (error) {
        console.error("[Error]: Failed to render graph:", error);
    }
}

async function renderMomentumGraph(matchData) {
    try {
        const response = await fetch('/api/generate_momentum_graph', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ matchData }),
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch graph: {response.status}`);
        }

        const result = await response.json();
        const graph = JSON.parse(result);

        console.log("Graph data: ", graph.data);
        console.log("Layout Data: ", graph.data);

        if (!graph.data | !graph.layout) {
            throw new Error("Graph data or layout is missing!");
        }

        Plotly.newPlot('graph-container-3', graph.data, graph.layout);
        console.log("[Debug]: Graph rendered succesfully.");
    } catch (error) {
        console.error("[Error]: Failed to render graph:", error)
    }
}


async function renderMatchSummary(matchData) {
    try {
        const response = await fetch('/api/generate_match_summary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ matchData }),
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch match summary: ${response.status}`);
        }

        const result = await response.json();
        console.log("[Debug] Match Summary Result:", result);
        const extraTimeDetails = result.extraTimeDetails; // Extra info: e.g., "(ET: 1 - 0, Pen: 5 - 4)"

        // Populate the score header dynamically
        document.getElementById('home-team-name').textContent = result.homeTeam
        document.getElementById('away-team-name').textContent = result.awayTeam
        document.getElementById('home-team-score').textContent = result.homeTeamNormalTime
        document.getElementById('away-team-score').textContent = result.awayTeamNormalTime
        document.getElementById('score-seperator').textContent = '-'

        // Update the extra details (or hide if not applicable)
        const extraDetails = document.getElementById('extra-details');
        if (extraTimeDetails) {
            extraDetails.textContent = extraTimeDetails;
            extraDetails.style.display = 'block';
        } else {
            extraDetails.style.display = 'none';
        }


        // Populate contribution tables
        populateTable('home-team-table', result.home);
        populateTable('away-team-table', result.away);
    } catch (error) {
        console.error('Error rendering match summary:', error);
    }
}

function populateTable(tableId, players) {
    const tableBody = document.querySelector(`#${tableId} tbody`);
    tableBody.innerHTML = '';  // Clear existing content

    players.forEach(player => {
        const row = document.createElement('tr');

        const playerCell = document.createElement('td');
        playerCell.textContent = player.player;

        const contributionsCell = document.createElement('td');
        contributionsCell.textContent = player.contributions.join('');

        row.appendChild(playerCell);
        row.appendChild(contributionsCell);
        tableBody.appendChild(row);
    });
}



// Event listener - Match dropdown
$('#match-select').on('change', async function () {
    const matchId = $(this).val();
    console.log("Match selected, ID:", matchId);

    try {
        // Fetch match data (from cache or API)
        const matchData = await fetchMatchData(matchId);

        document.getElementById('graph-container-1').classList.remove('hidden');
        document.getElementById('graph-container-2').classList.remove('hidden');
        document.getElementById('graph-container-3').classList.remove('hidden');

        // Run the rendering functions in parallel
        await Promise.all([
            renderGraph(matchData),
            renderMatchSummary(matchData),
            renderMomentumGraph(matchData)
        ]);
    } catch (error) {
        console.error("Failed to update plots:", error);
    }
});


