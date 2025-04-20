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

async function renderMatchSummary(matchData) {
    try {
        // Fetch match summary from the backend
        const response = await fetch('/api/generate_match_summary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ matchData }),
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch match summary: ${response.status}`);
        }

        const result = await response.json();

        console.log(result)

        // 1. Update Scoreline
        const homeTeamElement = document.getElementById('home-team');
        const awayTeamElement = document.getElementById('away-team');
        const scoreElement = document.getElementById('score');

        homeTeamElement.textContent = result.home_team || 'Home Team';
        awayTeamElement.textContent = result.away_team || 'Away Team';
        scoreElement.textContent = `${result.home_score} - ${result.away_score}`;

        // 2. Populate Home Team Events
        populateEventList('home-goals-list', result.home_goals);
        populateEventList('home-assists-list', result.home_assists);
        populateEventList('home-yellow-cards-list', result.home_yellow);
        populateEventList('home-red-cards-list', result.home_red);

        // 3. Populate Away Team Events
        populateEventList('away-goals-list', result.away_goals);
        populateEventList('away-assists-list', result.away_assists);
        populateEventList('away-yellow-cards-list', result.away_yellow);
        populateEventList('away-red-cards-list', result.away_red);
    } catch (error) {
        console.error('Error rendering match summary:', error);
    }
}

// Helper function to populate event lists dynamically
function populateEventList(elementId, events) {
    const listElement = document.getElementById(elementId);
    listElement.innerHTML = ''; // Clear the list

    if (events && events.length > 0) {
        events.forEach(event => {
            const listItem = document.createElement('li');
            listItem.classList.add('event-item');
            listItem.textContent = event; // Add event details
            listElement.appendChild(listItem);
        });
    } else {
        const emptyItem = document.createElement('li');
        emptyItem.classList.add('event-item', 'empty');
        emptyItem.textContent = 'No events recorded.';
        listElement.appendChild(emptyItem);
    }
}



// Event listener - Match dropdown
$('#match-select').on('change', async function () {
    const matchId = $(this).val();
    console.log("Match selected, ID:", matchId);

    try {
        // Fetch match data (from cache or API)
        const matchData = await fetchMatchData(matchId);

        // Pass matchData directly to renderGraph
        await renderGraph(matchData);

        await renderMatchSummary(matchData);
    } catch (error) {
        console.error("Failed to update plots:", error);
    }
});


