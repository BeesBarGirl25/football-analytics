import pandas as pd
import logging

def cumulative_stats(team_data: pd.DataFrame):
    team_data = team_data.copy()
    team_data['goals'] = team_data['shot_outcome'].eq('Goal').astype(int)
    team_data.replace(-999, 0, inplace=True)
    team_data.sort_values('minute', inplace=True)
    team_data['cum_goals'] = team_data['goals'].cumsum()
    team_data['cum_xg'] = team_data.get('shot_statsbomb_xg', 0).cumsum()
    return team_data

def extract_player_names(row):
    return [player['player']['name']
            for player in row.get('lineup', []) if 'player' in player]

def goal_assist_stats(match_data: pd.DataFrame, home_team: str, away_team: str):
    home_norm = away_norm = home_et = away_et = home_pen = away_pen = 0

    def process_team(team):
        df = match_data[match_data.get("team") == team].copy()
        if df.empty:
            logging.warning(f"No events for team {team}")
            return pd.DataFrame(columns=["player", "contributions"])

        starters_row = df.loc[df["type"] == "Starting XI", "tactics"]
        starters = []
        if not starters_row.empty:
            starters = extract_player_names(starters_row.iloc[0])
        replacements = df.loc[df["type"] == "Substitution", "substitution_replacement"].dropna().tolist()
        players = list(pd.unique(starters + replacements))

        pm = pd.DataFrame({"player": players})
        for col in ["goals", "assists", "yellow cards", "red cards", "subbed on", "subbed off"]:
            pm[col] = 0

        shots = df[df["type"] == "Shot"]
        goals = shots.loc[shots["shot_outcome"] == "Goal", "player"]
        assists = df.loc[df.get("pass_goal_assist", False) == True, "player"]
        yellows = df.loc[df.get("bad_behaviour_card", "") == "Yellow Card", "player"]
        reds = df.loc[df.get("bad_behaviour_card", "") == "Red Card", "player"]

        for _, shot in shots[shots["shot_outcome"] == "Goal"].iterrows():
            period = shot.get("period")
            nonlocal home_norm, away_norm, home_et, away_et, home_pen, away_pen
            if period in {1, 2}:
                home_norm += (team == home_team)
                away_norm += (team == away_team)
            elif period in {3, 4}:
                home_et += (team == home_team)
                away_et += (team == away_team)
            elif period == 5:
                home_pen += (team == home_team)
                away_pen += (team == away_team)

        subs = df[df["type"] == "Substitution"]
        pm.loc[pm["player"].isin(subs["substitution_replacement"].dropna()), "subbed on"] += 1
        pm.loc[pm["player"].isin(subs["player"].dropna()), "subbed off"] += 1

        for col, players_list in [("goals", goals), ("assists", assists),
                                   ("yellow cards", yellows), ("red cards", reds)]:
            pm.loc[pm["player"].isin(players_list.dropna()), col] += 1

        pm = pm.fillna(0).astype({c: "Int64" for c in pm.columns if c != "player"})

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

    return (home_df, away_df, home_team, away_team,
            home_norm, away_norm, home_et, away_et, home_pen, away_pen)
