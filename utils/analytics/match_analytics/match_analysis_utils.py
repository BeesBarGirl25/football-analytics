import pandas as pd
import logging

def cumulative_stats(team_data: pd.DataFrame):
    team_data['goals']=team_data['shot_outcome'].apply(lambda x: 1 if x == 'Goal' else 0)
    team_data.replace(-999, 0, inplace=True)
    team_data=team_data.sort_values('minute')
    team_data['cum_goals']=0
    team_data['cum_xg']=0
    team_data['cum_goals']=team_data['goals'].cumsum()
    team_data['cum_xg']=team_data['shot_statsbomb_xg'].cumsum()
    return team_data

def extract_player_names(row):
    return [player['player']['name'] for player in row['lineup']]

def goal_assist_stats(match_data: pd.DataFrame, home_team: str, away_team: str):
    # Initialize scoring counters
    home_norm = away_norm = home_et = away_et = home_pen = away_pen = 0

    def process_team(team):
        df = match_data[match_data["team"] == team]

        # Starting + subs list
        starting = df.loc[df["type"] == "Starting XI", "tactics"].iloc[0]
        starters = extract_player_names(starting)
        replacements = df.loc[df["type"] == "Substitution", "substitution_replacement"].tolist()
        players = starters + replacements
        pm = pd.DataFrame({"player": players})

        # Ensure count columns exist and are integer
        for col in ("goals", "assists", "yellow cards", "red cards", "subbed on", "subbed off"):
            pm[col] = 0

        # Shots → goals
        goals = df.loc[(df["type"] == "Shot") & (df["shot_outcome"] == "Goal"), "player"]
        assists = df.loc[df.get("pass_goal_assist", False) == True, "player"]
        yellows = df.loc[df.get("bad_behaviour_card", "") == "Yellow Card", "player"]
        reds = df.loc[df.get("bad_behaviour_card", "") == "Red Card", "player"]

        # Compute type of goal
        for period in df.loc[(df["type"] == "Shot") & (df["shot_outcome"] == "Goal"), "period"]:
            nonlocal home_norm, away_norm, home_et, away_et, home_pen, away_pen
            if period in [1, 2]:
                if df["period"].max() < 3:
                    home_norm += (team == home_team)
                    away_norm += (team == away_team)
                else:
                    home_norm += (team == home_team)
                    away_norm += (team == away_team)
                    home_et += (team == home_team)
                    away_et += (team == away_team)
            elif period in [3, 4]:
                home_et += (team == home_team)
                away_et += (team == away_team)
            elif period == 5:
                home_pen += (team == home_team)
                away_pen += (team == away_team)

        # Substitution counts
        subs = df.loc[df["type"] == "Substitution", :]
        pm.loc[pm["player"].isin(subs["substitution_replacement"]), "subbed on"] += 1
        pm.loc[pm["player"].isin(subs["player"]), "subbed off"] += 1

        # Aggregate stats
        pm.loc[pm["player"].isin(goals), "goals"] += 1
        pm.loc[pm["player"].isin(assists), "assists"] += 1
        pm.loc[pm["player"].isin(yellows), "yellow cards"] += 1
        pm.loc[pm["player"].isin(reds), "red cards"] += 1

        # Convert to nullable int before emoji
        pm = pm.fillna(0).astype({col: "Int64" for col in pm.columns if col != "player"})

        # Emoji build
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




