# Configurable Layout System

The Football Dashboard now features a comprehensive configurable layout system that allows users to customize how plots and data are displayed across both the match overview and team analysis sections.

## Overview

The layout system provides:
- **6 predefined layouts** for both overview and team analysis
- **Persistent user preferences** saved to localStorage
- **Responsive design** that adapts to screen size
- **Real-time layout switching** with smooth transitions
- **Automatic plot resizing** when layouts change

## Match Overview Layouts

### Available Layouts

1. **Classic** (Default)
   - 3-column layout: Momentum | Summary | Heatmap
   - XG chart spans bottom left
   - Traditional dashboard feel

2. **Horizontal**
   - All 4 components in a single row
   - Good for wide screens
   - Equal spacing for all elements

3. **Vertical**
   - All components stacked vertically
   - Optimal for mobile devices
   - Auto-selected on small screens

4. **Summary Focus**
   - Large summary area at top
   - Charts and heatmap below
   - Emphasizes match details

5. **Charts Focus**
   - Large area for momentum and XG charts
   - Summary and heatmap on the right
   - Data visualization emphasis

6. **Balanced**
   - 2x2 grid layout
   - Equal space for all components
   - Clean, organized appearance

### Usage

```html
<!-- Layout controls appear at top of overview tab -->
<div class="layout-controls">
    <button class="layout-btn active" data-layout="classic">Classic</button>
    <button class="layout-btn" data-layout="horizontal">Horizontal</button>
    <!-- ... more buttons ... -->
</div>
```

## Team Analysis Layouts

### Available Layouts

1. **Classic** (Default)
   - Stats table on left (280px)
   - Heatmap on right (remaining space)
   - Traditional two-column layout

2. **Vertical**
   - Stats table on top
   - Heatmap below
   - Good for mobile and narrow screens

3. **Heatmap Focus**
   - Small stats area (200px)
   - Large heatmap area
   - Emphasizes spatial data

4. **Stats Focus**
   - Equal width columns
   - More space for statistics
   - Better readability for data

5. **Balanced**
   - 50/50 split between stats and heatmap
   - Symmetric layout

6. **Wide Stats**
   - Stats take 40% of width
   - Heatmap takes 60%
   - Compromise between focus modes

### Usage

```html
<!-- Team layout controls for each team tab -->
<div class="team-layout-controls">
    <button class="team-layout-btn active" data-layout="classic" data-team="home_team">Classic</button>
    <button class="team-layout-btn" data-layout="vertical" data-team="home_team">Vertical</button>
    <!-- ... more buttons ... -->
</div>
```

## Technical Implementation

### CSS Grid System

The layout system uses CSS Grid with named areas for flexible positioning:

```css
/* Overview Grid Example */
.overview-grid.layout-classic {
  grid-template-columns: 1fr 2fr 2fr;
  grid-template-rows: 1fr 1fr;
  grid-template-areas:
    "momentum summary heatmap"
    "xg       summary heatmap";
}

/* Team Grid Example */
.team-analysis-grid.layout-classic {
  grid-template-columns: 280px 1fr;
  grid-template-rows: 1fr;
  grid-template-areas: "stats heatmap";
}
```

### JavaScript Components

#### LayoutManager
Handles overview tab layout switching:

```javascript
const layoutManager = new LayoutManager();
layoutManager.initialize();
layoutManager.switchLayout('horizontal');
```

#### TeamLayoutManager
Handles team-specific layout switching:

```javascript
const homeLayoutManager = new TeamLayoutManager('home_team');
homeLayoutManager.initialize();
homeLayoutManager.switchLayout('stats-focus');
```

### Key Features

#### Persistent Preferences
- Overview layout saved as: `football-dashboard-layout`
- Team layouts saved as: `football-dashboard-team-layout-{team_prefix}`
- Automatically loaded on page refresh

#### Responsive Behavior
- Mobile devices (≤768px): Auto-switch to vertical layouts
- Tablet devices (≤1200px): Adjust column widths
- Layout controls hidden on mobile

#### Plot Integration
- Automatic plot resizing when layouts change
- 300ms delay to ensure smooth transitions
- Integration with existing PlotManager

## File Structure

```
static/
├── css/layouts/
│   ├── overview-grid.css          # Overview layout styles
│   └── team-analysis-grid.css     # Team layout styles
├── js/components/
│   ├── layout-manager.js          # Overview layout manager
│   └── team-layout-manager.js     # Team layout manager
└── js/pages/
    └── match-analysis.js          # Integration with page
```

## API Reference

### LayoutManager Methods

```javascript
// Switch to a layout
layoutManager.switchLayout('horizontal');

// Get current layout
const current = layoutManager.getCurrentLayout();

// Get available layouts
const layouts = layoutManager.getAvailableLayouts();

// Save/load preferences
layoutManager.saveLayoutPreference('classic');
layoutManager.loadLayoutPreference();

// Custom positioning (12-column grid)
layoutManager.setCustomPosition('element-id', '1 / 4', '1 / 3');
layoutManager.applySizeClass('element-id', 'large');
```

### TeamLayoutManager Methods

```javascript
// Initialize for specific team
const teamManager = new TeamLayoutManager('home_team');

// Update team name in headers
teamManager.updateTeamName('Arsenal');

// All other methods same as LayoutManager
```

## Customization

### Adding New Layouts

1. **Add CSS Grid Definition**:
```css
.overview-grid.layout-custom {
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: 1fr 1fr;
  grid-template-areas:
    "momentum momentum xg xg"
    "summary summary heatmap heatmap";
}
```

2. **Update Available Layouts**:
```javascript
getAvailableLayouts() {
  return [
    // ... existing layouts ...
    { id: 'custom', name: 'Custom', description: 'Custom layout description' }
  ];
}
```

3. **Add Layout Button**:
```html
<button class="layout-btn" data-layout="custom">Custom</button>
```

### Custom Grid Positioning

For advanced users, the system supports 12-column grid positioning:

```javascript
// Position element at specific grid coordinates
layoutManager.setCustomPosition('my-element', '1 / 4', '1 / 3');

// Apply size classes
layoutManager.applySizeClass('my-element', 'xlarge');
```

Available size classes:
- `small`: 2 columns × 1 row
- `medium`: 3 columns × 2 rows  
- `large`: 4 columns × 2 rows
- `xlarge`: 6 columns × 3 rows
- `wide`: 6 columns × 2 rows
- `tall`: 3 columns × 4 rows
- `full`: 12 columns × 6 rows

## Browser Support

- Modern browsers with CSS Grid support
- localStorage for preference persistence
- Responsive design for mobile devices
- Graceful degradation for older browsers

## Performance Considerations

- Layout changes trigger plot resize with 300ms delay
- CSS transitions for smooth visual changes
- Minimal DOM manipulation during layout switches
- Efficient localStorage usage for preferences

## Troubleshooting

### Common Issues

1. **Layout buttons not working**
   - Check if layout manager is properly initialized
   - Verify button `data-layout` attributes match available layouts

2. **Plots not resizing**
   - Ensure PlotManager is available globally
   - Check for JavaScript errors in console

3. **Preferences not saving**
   - Verify localStorage is available
   - Check browser privacy settings

4. **Mobile layout issues**
   - Responsive breakpoints at 768px and 1200px
   - Layout controls hidden on mobile by design

### Debug Mode

Enable debug logging:
```javascript
// In browser console
localStorage.setItem('debug-layout', 'true');
```

This will show detailed logging for layout operations in the console.
