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

                // Additional scorelines (extra time and penalties)
        const scorelineElement = document.getElementById('match-scoreline');

        // Remove any previously added additional scores
        const existingExtras = document.querySelectorAll('.additional-scoreline');
        existingExtras.forEach(extra => extra.remove());

        // Add extra time score if present
        if (result.home_team_extra_time !== 0 || result.away_team_extra_time !== 0) {
            const extraTimeScoreElement = document.createElement('div');
            extraTimeScoreElement.classList.add('additional-scoreline', 'extra-time');
            extraTimeScoreElement.textContent = `ET: ${result.home_team_extra_time} - ${result.away_team_extra_time}`;
            scorelineElement.appendChild(extraTimeScoreElement);
        }

        // Add penalty score if present
        if (result.home_team_penalties !== 0 || result.away_team_penalties !== 0) {
            const penaltyScoreElement = document.createElement('div');
            penaltyScoreElement.classList.add('additional-scoreline', 'penalty');
            penaltyScoreElement.textContent = `Pen: ${result.home_team_penalties} - ${result.away_team_penalties}`;
            scorelineElement.appendChild(penaltyScoreElement);
        }



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
function populateEventList(categoryId, eventData) {
    const categoryElement = document.getElementById(categoryId);
    const categoryContainer = categoryElement.parentElement;
    const categoryHeading = categoryContainer.querySelector('.event-category-title');

    // Clear previous data
    categoryElement.innerHTML = '';

    if (eventData && eventData.length > 0) {
        // Populate items
        eventData.forEach(event => {
            const listItem = document.createElement('li');
            listItem.textContent = event;
            categoryElement.appendChild(listItem);
        });

        // Show heading if data exists
        categoryHeading.style.display = 'block';
    } else {
        // Hide heading if no data exists
        categoryHeading.style.display = 'none';
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


