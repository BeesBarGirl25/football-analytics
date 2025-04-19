### **How to Add a New Graph or Plot**
This tutorial explains how to add a new graph or plot to your site by creating a new backend endpoint, processing the data (if necessary), and integrating the graph into the frontend for rendering.
#### **Step 1. Update the Backend**
The backend is responsible for generating the graph/plot using a library like **Plotly** and serializing it for the frontend to render.
1. **Create a New Backend Endpoint**
    - Add a new route or function to your backend API to generate the graph. Here's a simple example assuming Flask:
``` python
import json
from plotly.utils import PlotlyJSONEncoder
import plotly.graph_objects as go
from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/api/new_graph', methods=['POST'])
def new_graph():
    # Generate your plotly figure
    fig = go.Figure()

    # Example: Add a trace (replace with your own logic)
    fig.add_trace(go.Bar(
        x=['Category A', 'Category B', 'Category C'],
        y=[10, 20, 30],
        name="Example Bar Chart"
    ))

    # Customize the layout
    fig.update_layout(
        title="New Graph",
        xaxis_title="Categories",
        yaxis_title="Values"
    )

    # Serialize the figure to JSON
    graph_json = json.dumps(fig, cls=PlotlyJSONEncoder)

    # Return the graph JSON
    return jsonify({"graph": graph_json})
```
- Replace `go.Bar(...)` with the specific traces (lines, scatter, histograms, etc.) you want in your graph.
- Ensure that you structure `data` and `layout` properly in the `fig`.

1. **Test the Backend Endpoint**
    - Use tools like **Postman**, **cURL**, or Flask's built-in development server to verify the endpoint is returning valid JSON.
    - Example:
``` bash
     curl -X POST http://127.0.0.1:5000/api/new_graph
```
- Expected Output:
``` json
     {
       "graph": "{\"data\": [...], \"layout\": {...}}"
     }
```
#### **Step 2. Add Frontend Handling**
The frontend is responsible for rendering the graph using the Plotly.js library.
1. **Set Up Frontend JavaScript Integration**
    - Locate the frontend JavaScript file where graph-related code resides (e.g., `script.js` or `new_graph.js`).
    - Add a new function to fetch the backend data and render the graph:
``` javascript
     async function fetchAndRenderNewGraph() {
         try {
             console.log("[Debug]: Fetching new graph data...");

             // Fetch the graph data from the backend
             const response = await fetch('/api/new_graph', {
                 method: 'POST',
                 headers: { 'Content-Type': 'application/json' }
             });

             if (!response.ok) {
                 throw new Error(`API call failed with status: ${response.status}`);
             }

             // Parse the response JSON
             const result = await response.json();
             console.log("[Debug]: Backend response received:", result);

             // Ensure the 'graph' object exists
             if (!result.graph) {
                 throw new Error("The 'graph' key is missing in the response.");
             }

             // Parse the graph data
             const graph = JSON.parse(result.graph);

             // Render the graph using Plotly
             Plotly.newPlot('new-graph-container', graph.data, graph.layout);
             console.log("[Debug]: New graph rendered successfully.");
         } catch (error) {
             console.error("[Error]: Failed to fetch and render new graph:", error);
         }
     }

     // Call the function (you can also bind it to specific events like a button click)
     fetchAndRenderNewGraph();
```
- Replace `/api/new_graph` with the backend endpoint URL.
- Ensure the `<div>` ID (`new-graph-container`) matches your intended container in the HTML.

1. **Add a Target Graph Container to Your HTML**
    - In `index.html`, or the appropriate HTML page, add a container for the graph:
``` html
     <div id="new-graph-container" style="width: 100%; height: 600px;"></div>
```
#### **Step 3. Add Navigation or Triggers**
Make sure users can interact with or navigate to the new plot from other parts of your site.
1. **Add a Menu Option or Button**
    - Add a link or button in your site’s navbar or landing page to load the new graph. For example:
``` html
     <button onclick="fetchAndRenderNewGraph()">Load New Graph</button>
```
- Alternatively, link to a page dedicated to the graph:
``` html
     <a href="/new_graph_page.html">View New Graph</a>
```
1. **Route Based on Framework**
    - If you're using a frontend framework like React, Vue, or Angular, ensure you properly route to the page or dynamically load the graph via events.

#### **Step 4. Test the Integration**
Test the full flow to ensure the new graph displays properly:
1. **Backend**:
    - Test the `/api/new_graph` endpoint with different input data to verify robust server-side handling.

2. **Frontend**:
    - Run the site in development mode.
    - Check the **browser console** for errors (e.g., network, JSON parsing, rendering issues).

3. **Cross-Browser Check**:
    - Test your graph on major browsers (e.g., Chrome, Firefox, Edge).

#### **Example Structure After Adding New Graph**
**Backend (`app.py`)**
``` python
# Add a new route for the new graph
@app.route('/api/new_graph', methods=['POST'])
def new_graph():
    # (Graph generation code here)
    ...
```
**Frontend (`new_graph.js`)**
``` javascript
// Function to fetch and render the graph
async function fetchAndRenderNewGraph() {
  ...
}
```
**HTML Updates (`index.html`)**
``` html
<button onclick="fetchAndRenderNewGraph()">Load New Graph</button>
<div id="new-graph-container" style="width: 100%; height: 600px;"></div>
```
#### Advanced Tips (Optional)
1. **Dynamic Graph Parameters**:
    - Pass options to the backend via POST (e.g., team name, time range):
``` javascript
     const teamName = "Liverpool";
     const response = await fetch('/api/new_graph', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify({ team: teamName })
     });
```
- Adjust backend logic to handle custom parameters.
    1. **Add Tests**:
        - Include unit tests for graph generation code.
        - Add frontend integration tests (e.g., using Cypress, Selenium).

    2. **Responsive Design**:
        - Use Plotly's `responsive: true` option in the layout to make graphs mobile-friendly:
``` javascript
     Plotly.newPlot('new-graph-container', graph.data, graph.layout, { responsive: true });
```
