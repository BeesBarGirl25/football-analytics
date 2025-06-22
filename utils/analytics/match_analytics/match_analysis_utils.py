import pandas as pd
import logging

def cumulative_stats(team_data: pd.DataFrame):
    team_data['goals'] = team_data['shot_outcome'].apply(lambda x: 1 if x == 'Goal' else 0)
    team_data.replace(-999, 0, inplace=True)
    team_data = team_data.sort_values('minute')
    team_data['cum_goals'] = team_data['goals'].cumsum()
    team_data['cum_xg'] = team_data['shot_statsbomb_xg'].cumsum()
    return team_data


def extract_player_names(row):
    return [player['player']['name'] for player in row['lineup']]

def goal_assist_stats(match_data: pd.DataFrame, home_team: str, away_team: str):
    home_norm = away_norm = home_et = away_et = home_pen = away_pen = 0

    def process_team(team):
        df = match_data[match_data["team"] == team]
        # Starting XI
        starters = []
        home_start = df[df["type"] == "Starting XI"]["tactics"]
        if not home_start.empty:
            starters = extract_player_names(home_start.iloc[0])
        # Substitutes
        subs = df[df["type"] == "Substitution"]
        replacements = subs["substitution_replacement"].dropna().tolist()
        players = starters + replacements

        pm = pd.DataFrame({"player": players})
        for col in ("goals","assists","yellow cards","red cards","subbed on","subbed off"):
            pm[col] = 0

        # Shots → goals
        goals_idx = df[(df["type"] == "Shot") & (df["shot_outcome"] == "Goal")].index
        goals = df.loc[goals_idx, "player"]

        # Assists (safe fallback)
        if "pass_goal_assist" in df.columns:
            assists = df[df["pass_goal_assist"] == True]["player"]
        else:
            assists = pd.Series([], dtype=object)

        # Cards (safe fallback)
        if "bad_behaviour_card" in df.columns:
            yellows = df[df["bad_behaviour_card"] == "Yellow Card"]["player"]
            reds = df[df["bad_behaviour_card"] == "Red Card"]["player"]
        else:
            yellows = reds = pd.Series([], dtype=object)

        # Count goal types per period
        for _, shot in df.loc[goals_idx].iterrows():
            period = shot.get("period", None)
            is_home = (team == home_team)
            if period in [1,2]:
                home_norm += is_home
                away_norm += not is_home
            elif period in [3,4]:
                home_et += is_home
                away_et += not is_home
            elif period == 5:
                home_pen += is_home
                away_pen += not is_home

        # Substitution counts
        pm.loc[pm["player"].isin(replacements), "subbed on"] += 1
        pm.loc[pm["player"].isin(subs["player"].dropna()), "subbed off"] += 1

        # Aggregate stats
        pm.loc[pm["player"].isin(goals), "goals"] += 1
        pm.loc[pm["player"].isin(assists), "assists"] += 1
        pm.loc[pm["player"].isin(yellows), "yellow cards"] += 1
        pm.loc[pm["player"].isin(reds), "red cards"] += 1

        pm = pm.fillna(0).astype({c: "Int64" for c in pm.columns if c != "player"})
        pm["contributions"] = (
            pm["goals"].apply(lambda x: "⚽" * int(x)) +
            pm["assists"].apply(lambda x: "🅰️" * int(x)) +
            pm["yellow cards"].apply(lambda x: "🟨" * int(x)) +
            pm["red cards"].apply(lambda x: "🟥" * int(x)) +
            pm["subbed on"].apply(lambda x: "🔺" * int(x)) +
            pm["subbed off"].apply(lambda x: "🔻" * int(x))
        )

        return pm[["player","contributions"]]

    home_df = process_team(home_team)
    away_df = process_team(away_team)

    return home_df, away_df, home_team, away_team, home_norm, away_norm, home_et, away_et, home_pen, away_pen
