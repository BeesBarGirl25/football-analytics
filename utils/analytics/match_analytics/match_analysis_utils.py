import pandas as pd
import logging

def cumulative_stats(team_data: pd.DataFrame):
    team_data['goals'] = team_data['shot_outcome'].apply(lambda x: 1 if x == 'Goal' else 0)
    team_data.replace(-999, 0, inplace=True)
    team_data = team_data.sort_values('minute')
    team_data['cum_goals'] = team_data['goals'].cumsum().astype(float)  # Convert to float for JSON serialization
    team_data['cum_xg'] = team_data['shot_statsbomb_xg'].cumsum().astype(float)  # Convert to float for JSON serialization
    return team_data


def extract_player_names(row):
    return [player['player']['name'] for player in row['lineup']]


def goal_assist_stats(match_data: pd.DataFrame, home_team: str, away_team: str):
    # Initialize scoring counters
    home_norm = away_norm = home_et = away_et = home_pen = away_pen = 0

    # Count goals for both teams first
    all_goals = match_data[(match_data["type"] == "Shot") & (match_data["shot_outcome"] == "Goal")]
    for _, goal in all_goals.iterrows():
        period = goal.get("period", None)
        is_home = goal["team"] == home_team
        
        if period in (1, 2):
            # Normal time goals
            if is_home:
                home_norm += 1
            else:
                away_norm += 1
        elif period in (3, 4):
            # Extra time goals
            if is_home:
                home_et += 1
            else:
                away_et += 1
        elif period == 5:
            # Penalty shootout goals
            if is_home:
                home_pen += 1
            else:
                away_pen += 1

    def process_team(team):
        df = match_data[match_data["team"] == team]

        # Starting XI
        starters = []
        start_rows = df[df["type"] == "Starting XI"]["tactics"]
        if not start_rows.empty:
            starters = extract_player_names(start_rows.iloc[0])

        # Substitutes
        subs = df[df["type"] == "Substitution"]
        replacements = subs["substitution_replacement"].dropna().tolist()
        players = starters + replacements

        pm = pd.DataFrame({"player": players})
        for col in ("goals","assists","yellow cards","red cards","subbed on","subbed off"):
            pm[col] = 0

        # Goals (shots with outcome == Goal)
        goal_shots = df[(df["type"] == "Shot") & (df["shot_outcome"] == "Goal")]
        for _, shot in goal_shots.iterrows():
            player = shot["player"]
            pm.loc[pm["player"] == player, "goals"] += 1

        # Assists
        if "pass_goal_assist" in df.columns:
            assist_players = df[df["pass_goal_assist"] == True]["player"].dropna()
            for player in assist_players:
                pm.loc[pm["player"] == player, "assists"] += 1

        # Cards
        if "bad_behaviour_card" in df.columns:
            for card_type, colname in [("Yellow Card", "yellow cards"), ("Red Card", "red cards")]:
                card_players = df[df["bad_behaviour_card"] == card_type]["player"].dropna()
                for player in card_players:
                    pm.loc[pm["player"] == player, colname] += 1

        # Substitution counts
        for player in replacements:
            pm.loc[pm["player"] == player, "subbed on"] += 1
        for player in subs["player"].dropna():
            pm.loc[pm["player"] == player, "subbed off"] += 1

        # Ensure ints and build contributions without commas - use regular int for JSON serialization
        pm = pm.fillna(0).astype({c: int for c in pm.columns if c != "player"})
        pm["contributions"] = (
            pm["goals"].apply(lambda x: "⚽" * int(x)) +
            pm["assists"].apply(lambda x: "🅰️" * int(x)) +
            pm["yellow cards"].apply(lambda x: "🟨" * int(x)) +
            pm["red cards"].apply(lambda x: "🟥" * int(x)) +
            pm["subbed on"].apply(lambda x: "🔺" * int(x)) +
            pm["subbed off"].apply(lambda x: "🔻" * int(x))
        )

        return pm[["player", "contributions"]]

    home_df = process_team(home_team)
    away_df = process_team(away_team)

    return (
        home_df, away_df,
        home_team, away_team,
        home_norm, away_norm,
        home_et, away_et,
        home_pen, away_pen
    )


def generate_team_stats(team_data: pd.DataFrame, team_name: str):
    """Generate team statistics for the stats table"""
    
    # Initialize stats
    stats = []
    
    # Goals
    goals = len(team_data[(team_data['type'] == 'Shot') & (team_data['shot_outcome'] == 'Goal')])
    stats.append({"stat_name": "Goals", "value": goals})
    
    # Total shots
    total_shots = len(team_data[team_data['type'] == 'Shot'])
    stats.append({"stat_name": "Total Shots", "value": total_shots})
    
    # Shots on target
    shots_on_target = len(team_data[(team_data['type'] == 'Shot') & 
                                   (team_data['shot_outcome'].isin(['Goal', 'Saved']))])
    stats.append({"stat_name": "Shots on Target", "value": shots_on_target})
    
    # xG (Expected Goals)
    xg = team_data[team_data['type'] == 'Shot']['shot_statsbomb_xg'].fillna(0).sum()
    stats.append({"stat_name": "xG", "value": f"{xg:.2f}"})
    
    # Passes
    total_passes = len(team_data[team_data['type'] == 'Pass'])
    stats.append({"stat_name": "Passes", "value": total_passes})
    
    # Pass accuracy - fix the logic for successful passes
    if total_passes > 0:
        # In StatsBomb data, successful passes have NaN in pass_outcome, failed passes have a value
        successful_passes = len(team_data[(team_data['type'] == 'Pass') & 
                                         (team_data['pass_outcome'].isna())])
        pass_accuracy = (successful_passes / total_passes * 100)
    else:
        pass_accuracy = 0
    stats.append({"stat_name": "Pass Accuracy", "value": f"{pass_accuracy:.1f}%"})
    
    # Possession - calculate based on total events, not just pass accuracy
    total_events = len(team_data)
    possession_pct = (total_events / (total_events + 1) * 50) if total_events > 0 else 0  # Rough approximation
    stats.append({"stat_name": "Possession", "value": f"{possession_pct:.1f}%"})
    
    # Fouls
    fouls = len(team_data[team_data['type'] == 'Foul Committed'])
    stats.append({"stat_name": "Fouls", "value": fouls})
    
    # Yellow cards
    if 'bad_behaviour_card' in team_data.columns:
        yellow_cards = len(team_data[(team_data['type'] == 'Bad Behaviour') & 
                                    (team_data['bad_behaviour_card'] == 'Yellow Card')])
    else:
        yellow_cards = 0
    stats.append({"stat_name": "Yellow Cards", "value": yellow_cards})
    
    # Red cards
    if 'bad_behaviour_card' in team_data.columns:
        red_cards = len(team_data[(team_data['type'] == 'Bad Behaviour') & 
                                 (team_data['bad_behaviour_card'] == 'Red Card')])
    else:
        red_cards = 0
    stats.append({"stat_name": "Red Cards", "value": red_cards})
    
    # Corners
    corners = len(team_data[team_data['type'] == 'Corner'])
    stats.append({"stat_name": "Corners", "value": corners})
    
    # Offsides
    offsides = len(team_data[team_data['type'] == 'Offside'])
    stats.append({"stat_name": "Offsides", "value": offsides})
    
    return {
        "team_stats": {
            "team_name": team_name,
            "stats": stats
        }
    }
