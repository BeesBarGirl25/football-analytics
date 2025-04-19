# Football Dashboard
This repository contains the implementation of a Football Dashboard application. The dashboard allows users to visualize various match and player analytics, including xG (expected goals) comparison graphs, team performance insights, and more.
## Project Structure
The repository is organized into the following sections:
### **Static Files**
This folder contains frontend JavaScript logic that enables dynamic functionality for the web app.
1. **`static/js/match_analysis.js` **
    - Handles retrieving and rendering match-specific graphs dynamically in HTML using `Plotly.js` and AJAX requests.
    - Functions:
        - **Fetch Match Graph Data:** Fetches the graph data from the backend API for a selected match.
        - **Dynamic Graph Rendering:** Renders the fetched Plotly graph in the specified container (`#graph-container-1`).
        - **Match Dropdown Listener:** Handles events when a specific match is selected by the user.

    - Dependencies: `Plotly.js`, jQuery.

2. **`static/js/dropdowns.js` **
    - Manages dropdown functionality for selecting matches, competitions, or players.
    - Provides utility functions to dynamically populate dropdowns with data fetched from the backend.

### **Backend Routes**
The server-side logic powering the API and data fetching for the frontend.
1. **`routes/match_routes.py` **
    - Contains Flask API routes for match-related operations.
    - Key Routes:
        - **`/api/match_graph/<match_id>`**:
            - Returns Plotly graph data JSON for a specific match ID, fetched from a cached data store.

        - Integrates with the xG plotting logic in `xG_per_game.py`.

### **Utilities**
Helper functions and modules for analytics, visualizations, and data operations.
1. **`utils/plots/match_plots/xG_per_game.py` **
    - Contains the `generate_match_graph` function that generates interactive Plotly graphs for xG analysis.
    - Key Features:
        - Dynamically generates cumulative xG and goals plots for two teams in a match.
        - Adds visual indicators for extra time and penalties.
        - Configures interactive graph styling using Plotly.

    - Input: `match_data` (shot and period details for a match).
    - Output: Plotly graph object.

2. **`utils/analytics/match_analytics/match_analysis_utils.py` **
    - Includes helper functions for various analytics computation tasks.
    - Could include functions like:
        - Computing cumulative goals/xG for each team.
        - Summarizing key statistics for a match.
        - Formatting data for visualization.

### **Templates**
HTML templates used for rendering pages in the web app.
1. **`templates/match_analysis.html` **
    - Frontend page for match analysis visualization.
    - Key Elements:
        - Dropdown for selecting matches.
        - Graph container (`#graph-container-1`) to dynamically display xG visualizations.
        - Navigation tabs for switching between overview, teams, and player analysis.

### **How the Application Works**
1. **Frontend Flow:**
    - The user selects a match from a dropdown menu in the `match_analysis.html` page.
    - The selected match triggers an AJAX call (via `match_analysis.js`) to fetch graph data from the backend API.

2. **Backend Flow:**
    - The backend API fetches the relevant match data from the **cache** or another data source.
    - The `generate_match_graph` function in `xG_per_game.py` creates a Plotly graph object.
    - The graph data (in JSON format) is returned to the frontend.

3. **Graph Rendering:**
    - The frontend receives the JSON graph data and renders it inside `graph-container-1` using `Plotly.js`.

### **Setup and Installation**
Follow the steps below to run the application locally:
#### **1. Clone the Repository:**
``` bash
git clone https://github.com/username/football_dashboard.git
cd football_dashboard
```
#### **2. Install Dependencies:**
``` bash
pip install -r requirements.txt
```
Ensure you have all necessary Python libraries like Flask, Plotly, and Flask-Caching installed.
#### **3. Run the Application:**
``` bash
flask run
```
#### **4. Visit the Application:**
Open your browser and navigate to:
``` 
http://127.0.0.1:5000
```
### **Key Features**
1. **Expected Goals Analysis:**
    - Compare cumulative xG and goals for both teams in a match with dynamic graphs.

2. **Dynamic Match Selection:**
    - Seamlessly switch between matches and update graphs without reloading the page.

3. **Customization and Extendibility:**
    - Modular structure allows for easy addition of new visualizations, analytics, or API endpoints.

### **Future Enhancements**
- Cache Implementation:
    - Automate caching of match data from database or external APIs.

- Expanded Analytics:
    - Add additional tabs for player-specific and competition-wide analytics.

- Responsive Design:
    - Enhance the frontend to ensure compatibility across all device sizes.

### **Credits**
- **Frameworks & Libraries:**
    - Flask
    - Plotly.js
    - Flask-Caching

Feel free to contribute to this project by submitting pull requests or reporting issues!
