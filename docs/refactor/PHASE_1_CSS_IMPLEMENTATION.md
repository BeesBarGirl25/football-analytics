# Phase 1: CSS Modularization Implementation Guide

## Step 1: Create New CSS Directory Structure

```bash
mkdir -p static/css/components
mkdir -p static/css/layouts
mkdir -p static/css/themes
```

## Step 2: Extract CSS Modules from base.css

### A. Core Variables & Base Layout (static/css/base.css)
```css
/* === CSS Variables === */
:root {
  --bg-primary: #121212;
  --bg-secondary: #1f1f1f;
  --bg-tertiary: #2a2a2a;
  --text-primary: #e0e0e0;
  --text-secondary: #dcdcdc;
  --accent-blue: #90caf9;
  --accent-orange: #ff6b35;
  --border-color: #333;
  --shadow: 0 0 10px rgba(0, 0, 0, 0.5);
}

/* === Base Reset === */
html, body {
  height: 100%;
  margin: 0;
  padding: 0;
  overflow: hidden;
  font-family: 'Segoe UI', sans-serif;
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

/* === Main Grid Layout === */
.wrapper {
  display: grid;
  grid-template-areas:
    "sidebar top-navbar"
    "sidebar content";
  grid-template-columns: 60px 1fr;
  grid-template-rows: auto 1fr;
  height: 100vh;
  overflow: hidden;
}

.content {
  grid-area: content;
  padding: 0.5rem;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100%;
  width: 100%;
  box-sizing: border-box;
}
```

### B. Navigation Components (static/css/components/navigation.css)
```css
/* === Sidebar === */
.sidebar {
  grid-area: sidebar;
  background-color: var(--bg-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 60px;
  overflow-y: auto;
  gap: 20px;
}

.icon-button {
  color: var(--accent-blue);
  font-size: 1.5rem;
  transition: transform 0.2s ease;
}
.icon-button:hover {
  transform: scale(1.2);
}

/* === Top Navbar === */
.top-navbar {
  grid-area: top-navbar;
  background-color: var(--bg-secondary);
  display: flex;
  align-items: center;
  padding: 5px 20px;
  border-bottom: 1px solid var(--border-color);
  height: 45px;
  z-index: 1000;
  gap: 1rem;
  flex-wrap: nowrap;
}

.top-navbar .logo {
  color: var(--accent-blue);
  font-size: 1.8rem;
  font-weight: bold;
  white-space: nowrap;
}

/* === Tab Navigation === */
.analysis-nav {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.tab-btn {
  flex: 1;
  background-color: #2d2d2d;
  border: none;
  padding: 0.75rem;
  border-radius: 8px;
  color: var(--text-secondary);
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
  text-align: center;
}
.tab-btn:hover {
  background-color: #3d3d3d;
}
.tab-btn.active {
  background-color: #007bff;
  color: #fff;
}
```

### C. Graph Components (static/css/components/graphs.css)
```css
/* === Graph Containers === */
.graph-container {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  display: flex;
  align-items: stretch;
  justify-content: center;
  overflow: hidden;
  color: var(--text-primary);
  text-align: center;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  font-size: 0.85rem;
}

.graph-container.tall {
  height: 100%;
  min-height: 400px;
}

.graph-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: stretch;
  width: 100%;
  height: 100%;
  padding: 0.5rem;
  gap: 1rem;
  box-sizing: border-box;
}

.plotly-wrapper {
  flex-grow: 1;
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
}

.plotly-wrapper .js-plotly-plot,
.plotly-wrapper .plot-container,
.plotly-wrapper .main-svg {
  width: 100% !important;
  height: 100% !important;
}
```

### D. Controls (static/css/components/controls.css)
```css
/* === Toggle Buttons === */
.toggle-btn,
.phase-btn {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid #444;
  border-radius: 16px;
  padding: 4px 10px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  font-weight: 500;
}

.toggle-btn:hover,
.phase-btn:hover {
  background-color: var(--bg-tertiary);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.toggle-btn.active {
  background-color: var(--accent-blue);
  color: var(--bg-primary);
  font-weight: 600;
  border-color: var(--accent-blue);
  box-shadow: 0 2px 6px rgba(144, 202, 249, 0.3);
}

.phase-btn.active {
  background-color: var(--accent-orange);
  color: #fff;
  font-weight: 600;
  border-color: var(--accent-orange);
  box-shadow: 0 2px 6px rgba(255, 107, 53, 0.3);
}

/* === Control Groups === */
.heatmap-controls-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 0.3rem 0;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  gap: 0.25rem;
  align-items: center;
}

.control-separator {
  width: 1px;
  height: 20px;
  background-color: #444;
  margin: 0 0.5rem;
}

/* === Switch Toggle === */
.switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  background-color: #444;
  border-radius: 24px;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  transition: 0.4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 14px;
  width: 14px;
  border-radius: 50%;
  left: 3px;
  bottom: 3px;
  background-color: var(--accent-blue);
  transition: 0.4s;
}

input:checked + .slider {
  background-color: var(--accent-blue);
}

input:checked + .slider:before {
  transform: translateX(20px);
}
```

### E. Tables (static/css/components/tables.css)
```css
/* === Summary Tables === */
.team-tables {
  display: flex;
  flex-direction: row;
  justify-content: center;
  gap: 1rem;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.team-table {
  flex: 1;
  background-color: var(--bg-tertiary);
  padding: 0.5rem;
  border-radius: 10px;
  box-shadow: var(--shadow);
  overflow-y: auto;
  font-size: calc(0.65rem + 0.5vh);
  display: flex;
  flex-direction: column;
  justify-content: stretch;
  height: 100%;
}

/* === Stats Sidebar Table === */
.team-stats-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.team-stats-table tr {
  border-bottom: 1px solid var(--border-color);
  transition: background-color 0.2s ease;
}

.team-stats-table tr:hover {
  background-color: var(--border-color);
}

.team-stats-table td {
  padding: 0.6rem 0.4rem;
  vertical-align: middle;
}

.team-stats-table .stat-name {
  font-weight: 500;
  color: var(--text-secondary);
  text-align: left;
  width: 60%;
}

.team-stats-table .stat-value {
  font-weight: 600;
  color: var(--accent-blue);
  text-align: right;
  width: 40%;
  font-family: 'Courier New', monospace;
}

.team-stats-table tr.highlight-stat {
  background-color: rgba(144, 202, 249, 0.1);
}

.team-stats-table tr.highlight-stat .stat-value {
  color: #fff;
}
```

## Step 3: Create Layout Files

### A. Overview Layout (static/css/layouts/overview.css)
```css
.graphs-container.wide-mode {
  display: grid;
  grid-template-columns: 1fr 2fr 2fr;
  grid-template-rows: 1fr 1fr;
  gap: 1rem;
  width: 100%;
  height: 100%;
  grid-template-areas:
    "momentum summary heatmap"
    "xg       summary heatmap";
}

.graphs-container.compact-mode {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: auto auto auto auto;
  gap: 1rem;
  width: 100%;
  grid-template-areas:
    "momentum"
    "xg"
    "summary"
    "heatmap";
}

.graph-container.xg {
  grid-area: xg;
}

.graph-container.momentum {
  grid-area: momentum;
}

.graph-container.summary {
  grid-area: summary;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  gap: 0.5rem;
  overflow: hidden;
}

.graph-container.heatmap {
  grid-area: heatmap;
}
```

### B. Team Analysis Layout (static/css/layouts/team-analysis.css)
```css
.team-analysis-layout {
  display: flex;
  width: 100%;
  height: 100%;
  gap: 1rem;
}

.team-stats-sidebar {
  width: 280px;
  min-width: 280px;
  background-color: var(--bg-tertiary);
  border-radius: 8px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.heatmap-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.stats-header {
  margin-bottom: 1rem;
  text-align: center;
  border-bottom: 1px solid #444;
  padding-bottom: 0.5rem;
}

.stats-header h4 {
  margin: 0;
  color: var(--accent-blue);
  font-size: 1.1rem;
  font-weight: 600;
}

.stats-table-container {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #555 var(--bg-tertiary);
}

.heatmap-layout {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  height: 100%;
  width: 100%;
}

.heatmap-plot {
  flex-grow: 1;
  width: 100%;
  height: 100%;
  min-height: 0;
}
```

## Step 4: Update base.html Template

```html
<!-- In templates/base.html, replace single CSS link with: -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/navigation.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/graphs.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/controls.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/tables.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/layouts/overview.css') }}">
<link rel="stylesheet" href="{{ url_for('static', filename='css/layouts/team-analysis.css') }}">
```

## Step 5: Benefits of This Approach

### Immediate Benefits:
1. **Easier Debugging**: Find styles quickly by component
2. **Better Organization**: Related styles grouped together
3. **Reduced Conflicts**: Smaller files = fewer merge conflicts
4. **Selective Loading**: Load only needed CSS per page

### Future Benefits:
1. **CSS Variables**: Easy theme switching
2. **Component Reuse**: Consistent styling across features
3. **Performance**: Smaller initial CSS bundles
4. **Maintainability**: Clear separation of concerns

## Next Steps After Phase 1:
- Test all pages still work correctly
- Verify responsive design intact
- Move to Phase 2: JavaScript modularization
- Consider CSS build process for production
