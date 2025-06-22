import pandas as pd
import logging

def cumulative_stats(team_data: pd.DataFrame):
    team_data = team_data.copy()
    team_data['goals'] = team_data['shot_outcome'].apply(lambda x: 1 if x == 'Goal' else 0)
    team_data.replace(-999, 0, inplace=True)
    team_data.sort_values('minute', inplace=True)
    team_data['cum_goals'] = team_data['goals'].cumsum()
    team_data['cum_xg'] = team_data['shot_statsbomb_xg'].cumsum()
    return team_data

def extract_player_names(row):
    return [player['player']['name'] for player in row['lineup']]

def goal_assist_stats(match_data: pd.DataFrame, home_team: str, away_team: str):
    # Initialize scoring counters
    home_norm = away_norm = home_et = away_et = home_pen = away_pen = 0

    def process_team(team):
        df = match_data[match_data["team"] == team]

        if df.empty:
            logging.warning(f"No data for team: {team}")
            return pd.DataFrame(columns=["player", "contributions"])

        starting_events = df.loc[df["type"] == "Starting XI", "tactics"]
        if starting_events.empty:
            starters = []
        else:
            starters = extract_player_names(starting_events.iloc[0])

        replacements = df.loc[df["type"] == "Substitution", "substitution_replacement"].dropna().tolist()
        players = starters + replacements
        pm = pd.DataFrame({"player": players})

        for col in ("goals", "assists", "yellow cards", "red cards", "subbed on", "subbed off"):
            pm[col] = 0

        # Retrieve event series safely
        shots = df[df["type"] == "Shot"]
        goals = shots.loc[shots["shot_outcome"] == "Goal", "player"]
        assists = df.loc[df.get("pass_goal_assist", False) == True, "player"]
        yellows = df.loc[df.get("bad_behaviour_card", "") == "Yellow Card", "player"]
        reds = df.loc[df.get("bad_behaviour_card", "") == "Red Card", "player"]

        nonlocal home_norm, away_norm, home_et, away_et, home_pen, away_pen
        for _, shot in shots[shots["shot_outcome"] == "Goal"].iterrows():
            period = shot.get("period", None)
            if period in (1, 2):
                home_norm += int(team == home_team)
                away_norm += int(team == away_team)
            elif period in (3, 4):
                home_et += int(team == home_team)
                away_et += int(team == away_team)
            elif period == 5:
                home_pen += int(team == home_team)
                away_pen += int(team == away_team)

        subs = df[df["type"] == "Substitution"]
        if not subs.empty:
            pm.loc[pm["player"].isin(subs["substitution_replacement"]), "subbed on"] += 1
            pm.loc[pm["player"].isin(subs["player"]), "subbed off"] += 1

        pm.loc[pm["player"].isin(goals), "goals"] += 1
        pm.loc[pm["player"].isin(assists), "assists"] += 1
        pm.loc[pm["player"].isin(yellows), "yellow cards"] += 1
        pm.loc[pm["player"].isin(reds), "red cards"] += 1

        for col in ("goals", "assists", "yellow cards", "red cards", "subbed on", "subbed off"):
            pm[col] = pm[col].fillna(0).astype("Int64")

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

    return home_df, away_df, home_team, away_team, home_norm, away_norm, home_et, away_et, home_pen, away_pen
