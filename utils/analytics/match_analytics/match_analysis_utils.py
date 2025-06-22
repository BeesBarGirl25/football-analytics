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
    # Initialize scoring counters
    home_norm = away_norm = home_et = away_et = home_pen = away_pen = 0

    def process_team(team):
        nonlocal home_norm, away_norm, home_et, away_et, home_pen, away_pen
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
            period = shot.get("period", None)
            is_home = team == home_team
            if period in (1, 2):
                if df["period"].max() < 3:
                    home_norm += is_home
                    away_norm += not is_home
                else:
                    home_norm += is_home
                    away_norm += not is_home
                    home_et += is_home
                    away_et += not is_home
            elif period in (3, 4):
                home_et += is_home
                away_et += not is_home
            elif period == 5:
                home_pen += is_home
                away_pen += not is_home

        # Assists
        if "pass_goal_assist" in df.columns:
            for player in df[df["pass_goal_assist"] == True]["player"]:
                pm.loc[pm["player"] == player, "assists"] += 1

        # Cards
        if "bad_behaviour_card" in df.columns:
            for card_type, colname in [("Yellow Card", "yellow cards"), ("Red Card", "red cards")]:
                for player in df[df["bad_behaviour_card"] == card_type]["player"]:
                    pm.loc[pm["player"] == player, colname] += 1

        # Substitution counts
        for player in replacements:
            pm.loc[pm["player"] == player, "subbed on"] += 1
        for player in subs["player"].dropna():
            pm.loc[pm["player"] == player, "subbed off"] += 1

        # Ensure ints and build contributions without commas
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

    return (
        home_df, away_df,
        home_team, away_team,
        home_norm, away_norm,
        home_et, away_et,
        home_pen, away_pen
    )