# Football Dashboard API Documentation

This document provides comprehensive documentation for all API endpoints in the Football Dashboard application.

## 🌐 Base URL

- **Development**: `http://localhost:5000`
- **Production**: `https://your-app.herokuapp.com`

## 📋 API Overview

The Football Dashboard API follows RESTful principles and returns JSON responses. All endpoints are prefixed with `/api` for API routes, while page routes serve HTML templates.

## 🔐 Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## 📊 Response Format

### Success Response
```json
{
  "status": "success",
  "data": {
    // Response data
  }
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Error description",
  "code": 400
}
```

## 🏠 Page Routes

### Get Match Analysis Page
```http
GET /
```

**Description**: Returns the main match analysis page.

**Response**: HTML template with match analysis interface.

### Get Competition Analysis Page
```http
GET /competition
```

**Description**: Returns the competition analysis page.

**Response**: HTML template with competition analysis interface.

## 🏈 Match API Endpoints

### Get All Matches
```http
GET /api/matches
```

**Description**: Retrieve all available matches with basic information.

**Parameters**: None

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "match_id": 3895302,
      "home_team": "Bayer Leverkusen",
      "away_team": "Werder Bremen",
      "match_date": "2023-04-15",
      "home_score": 5,
      "away_score": 2,
      "competition_name": "Bundesliga",
      "season_name": "2022/2023"
    }
  ]
}
```

### Get Match Details
```http
GET /api/matches/{match_id}
```

**Description**: Get detailed information for a specific match.

**Parameters**:
- `match_id` (integer, required): The unique identifier for the match

**Response**:
```json
{
  "status": "success",
  "data": {
    "match_id": 3895302,
    "home_team": "Bayer Leverkusen",
    "away_team": "Werder Bremen",
    "match_date": "2023-04-15T15:30:00Z",
    "home_score": 5,
    "away_score": 2,
    "competition_id": 9,
    "season_id": 106,
    "competition_name": "Bundesliga",
    "season_name": "2022/2023"
  }
}
```

### Get Match Plots
```http
GET /api/matches/{match_id}/plots
```

**Description**: Retrieve all pre-generated plots and analytics for a specific match.

**Parameters**:
- `match_id` (integer, required): The unique identifier for the match

**Response**:
```json
{
  "match_summary": {
    "homeTeam": "Bayer Leverkusen",
    "awayTeam": "Werder Bremen",
    "homeTeamNormalTime": 5,
    "awayTeamNormalTime": 2,
    "homeTeamExtraTime": 0,
    "awayTeamExtraTime": 0,
    "homeTeamPenalties": 0,
    "awayTeamPenalties": 0,
    "scoreline": "Bayer Leverkusen 5 - 2 Werder Bremen",
    "home": [
      {
        "player": "Florian Wirtz",
        "contributions": "⚽⚽🅰️"
      }
    ],
    "away": [
      {
        "player": "Niclas Füllkrug",
        "contributions": "⚽"
      }
    ]
  },
  "xg_graph": {
    "data": [
      {
        "x": [0, 15, 30, 45, 60, 75, 90],
        "y": [0, 0.5, 1.2, 1.8, 2.3, 2.8, 3.1],
        "name": "Bayer Leverkusen",
        "type": "scatter",
        "mode": "lines+markers"
      }
    ],
    "layout": {
      "title": "Expected Goals (xG) Timeline",
      "xaxis": {"title": "Minute"},
      "yaxis": {"title": "Cumulative xG"}
    }
  },
  "momentum_graph": {
    "data": [
      {
        "x": [0, 5, 10, 15, 20],
        "y": [0, 2, -1, 3, 1],
        "type": "bar",
        "name": "Momentum"
      }
    ],
    "layout": {
      "title": "Match Momentum",
      "xaxis": {"title": "Time Period"},
      "yaxis": {"title": "Momentum Score"}
    }
  },
  "dominance_heatmap": {
    "data": [
      {
        "z": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
        "type": "heatmap",
        "colorscale": "RdBu"
      }
    ],
    "layout": {
      "title": "Team Dominance Heatmap - Full Match"
    }
  },
  "home_team_stats": {
    "team_stats": {
      "team_name": "Bayer Leverkusen",
      "stats": [
        {"stat_name": "Goals", "value": 5},
        {"stat_name": "Total Shots", "value": 20},
        {"stat_name": "Shots on Target", "value": 12},
        {"stat_name": "xG", "value": "3.45"},
        {"stat_name": "Passes", "value": 651},
        {"stat_name": "Pass Accuracy", "value": "87.2%"},
        {"stat_name": "Possession", "value": "58.3%"},
        {"stat_name": "Fouls", "value": 11},
        {"stat_name": "Yellow Cards", "value": 2},
        {"stat_name": "Red Cards", "value": 0},
        {"stat_name": "Corners", "value": 7},
        {"stat_name": "Offsides", "value": 3}
      ]
    }
  },
  "away_team_stats": {
    "team_stats": {
      "team_name": "Werder Bremen",
      "stats": [
        {"stat_name": "Goals", "value": 2},
        {"stat_name": "Total Shots", "value": 14},
        {"stat_name": "Shots on Target", "value": 6},
        {"stat_name": "xG", "value": "1.89"},
        {"stat_name": "Passes", "value": 423},
        {"stat_name": "Pass Accuracy", "value": "79.4%"},
        {"stat_name": "Possession", "value": "41.7%"},
        {"stat_name": "Fouls", "value": 15},
        {"stat_name": "Yellow Cards", "value": 3},
        {"stat_name": "Red Cards", "value": 1},
        {"stat_name": "Corners", "value": 4},
        {"stat_name": "Offsides", "value": 2}
      ]
    }
  }
}
```

**Plot Types Available**:
- `match_summary`: Match overview with scores and player contributions
- `xg_graph`: Expected Goals timeline
- `momentum_graph`: Match momentum visualization
- `dominance_heatmap`: Full match dominance heatmap
- `dominance_heatmap_first`: First half dominance heatmap
- `dominance_heatmap_second`: Second half dominance heatmap
- `home_team_possession_full`: Home team possession heatmap (full match)
- `home_team_possession_first`: Home team possession heatmap (first half)
- `home_team_possession_second`: Home team possession heatmap (second half)
- `home_team_attack_full`: Home team attack heatmap (full match)
- `home_team_attack_first`: Home team attack heatmap (first half)
- `home_team_attack_second`: Home team attack heatmap (second half)
- `home_team_defense_full`: Home team defense heatmap (full match)
- `home_team_defense_first`: Home team defense heatmap (first half)
- `home_team_defense_second`: Home team defense heatmap (second half)
- `away_team_possession_full`: Away team possession heatmap (full match)
- `away_team_possession_first`: Away team possession heatmap (first half)
- `away_team_possession_second`: Away team possession heatmap (second half)
- `away_team_attack_full`: Away team attack heatmap (full match)
- `away_team_attack_first`: Away team attack heatmap (first half)
- `away_team_attack_second`: Away team attack heatmap (second half)
- `away_team_defense_full`: Away team defense heatmap (full match)
- `away_team_defense_first`: Away team defense heatmap (first half)
- `away_team_defense_second`: Away team defense heatmap (second half)
- `home_team_heatmap`: Home team general heatmap
- `home_team_heatmap_first`: Home team general heatmap (first half)
- `home_team_heatmap_second`: Home team general heatmap (second half)
- `away_team_heatmap`: Away team general heatmap
- `away_team_heatmap_first`: Away team general heatmap (first half)
- `away_team_heatmap_second`: Away team general heatmap (second half)
- `home_team_stats`: Home team statistics
- `away_team_stats`: Away team statistics

## 🏆 Competition API Endpoints

### Get All Competitions
```http
GET /api/competitions
```

**Description**: Retrieve all available competitions.

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "competition_id": 9,
      "competition_name": "Bundesliga",
      "country_name": "Germany",
      "season_name": "2022/2023"
    },
    {
      "competition_id": 2,
      "competition_name": "Premier League",
      "country_name": "England",
      "season_name": "2022/2023"
    }
  ]
}
```

### Get Competition Matches
```http
GET /api/competitions/{competition_id}/matches
```

**Description**: Get all matches for a specific competition.

**Parameters**:
- `competition_id` (integer, required): The unique identifier for the competition

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "match_id": 3895302,
      "home_team": "Bayer Leverkusen",
      "away_team": "Werder Bremen",
      "match_date": "2023-04-15",
      "home_score": 5,
      "away_score": 2
    }
  ]
}
```

## 📊 Dropdown API Endpoints

### Get Competition Dropdown Data
```http
GET /api/dropdowns/competitions
```

**Description**: Get formatted competition data for dropdown menus.

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "value": "9",
      "text": "Bundesliga (Germany) - 2022/2023",
      "competition_id": 9,
      "competition_name": "Bundesliga",
      "country_name": "Germany",
      "season_name": "2022/2023"
    }
  ]
}
```

### Get Match Dropdown Data
```http
GET /api/dropdowns/matches
```

**Description**: Get formatted match data for dropdown menus.

**Query Parameters**:
- `competition_id` (integer, optional): Filter matches by competition

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "value": "3895302",
      "text": "Bayer Leverkusen vs Werder Bremen (2023-04-15)",
      "match_id": 3895302,
      "home_team": "Bayer Leverkusen",
      "away_team": "Werder Bremen",
      "match_date": "2023-04-15"
    }
  ]
}
```

## ❌ Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error - Server error |

### Common Error Responses

#### Match Not Found
```json
{
  "status": "error",
  "message": "Match not found",
  "code": 404
}
```

#### Invalid Match ID
```json
{
  "status": "error",
  "message": "Invalid match ID format",
  "code": 400
}
```

#### No Plots Available
```json
{
  "status": "error",
  "message": "No plot data available for this match",
  "code": 404
}
```

## 🔧 Data Models

### Match Model
```python
class Match(db.Model):
    match_id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer)
    season_id = db.Column(db.Integer)
    home_team = db.Column(db.String(100))
    away_team = db.Column(db.String(100))
    match_date = db.Column(db.Date)
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
```

### MatchPlot Model
```python
class MatchPlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.match_id'))
    plot_type = db.Column(db.String(50))
    plot_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Competition Model
```python
class Competition(db.Model):
    competition_id = db.Column(db.Integer, primary_key=True)
    competition_name = db.Column(db.String(100))
    country_name = db.Column(db.String(100))
    season_name = db.Column(db.String(50))
```

## 📈 Rate Limiting

Currently, no rate limiting is implemented. In production, consider implementing rate limiting to prevent abuse.

## 🔄 Caching

- **Plot Data**: Cached in database as JSON for performance
- **Match Data**: Cached in memory for 5 minutes
- **Competition Data**: Cached in memory for 1 hour

## 📝 Usage Examples

### JavaScript Fetch Examples

#### Get Match Plots
```javascript
async function getMatchPlots(matchId) {
    try {
        const response = await fetch(`/api/matches/${matchId}/plots`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching match plots:', error);
        throw error;
    }
}
```

#### Get All Matches
```javascript
async function getAllMatches() {
    try {
        const response = await fetch('/api/matches');
        const data = await response.json();
        return data.data; // Return the matches array
    } catch (error) {
        console.error('Error fetching matches:', error);
        return [];
    }
}
```

### Python Requests Examples

#### Get Match Data
```python
import requests

def get_match_plots(match_id):
    url = f"http://localhost:5000/api/matches/{match_id}/plots"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching match plots: {e}")
        return None
```

## 🚀 Future API Enhancements

### Planned Endpoints

#### Player Statistics
```http
GET /api/players/{player_id}/stats
```

#### Team Performance
```http
GET /api/teams/{team_name}/performance
```

#### Live Match Updates
```http
GET /api/matches/{match_id}/live
```

#### Custom Analytics
```http
POST /api/analytics/custom
```

### Planned Features

- **Authentication**: JWT-based authentication system
- **Rate Limiting**: Request throttling and quotas
- **Webhooks**: Real-time data updates
- **GraphQL**: Alternative query interface
- **API Versioning**: Backward compatibility support

## 📞 Support

For API-related questions or issues:

1. Check this documentation
2. Review the [Architecture Guide](ARCHITECTURE.md)
3. Create an issue in the repository
4. Contact the development team

---

**API Version**: 1.0  
**Last Updated**: 2025-06-30  
**Maintained by**: Football Dashboard Team
