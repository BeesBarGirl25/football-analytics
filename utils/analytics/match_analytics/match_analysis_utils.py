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
    # Counters
    home_score_norm = away_score_norm = 0
    home_score_et = away_score_et = 0
    home_score_pen = away_score_pen = 0

    home_team_data = away_team_data = None

    for team in (home_team, away_team):
        team_df = match_data[match_data["team"] == team]

        # Build player list
        starting = extract_player_names(team_df[team_df["type"] == "Starting XI"]["tactics"].iloc[0])
        subbed = team_df[team_df["type"] == "Substitution"]["substitution_replacement"].tolist()
        players = starting + subbed

        # Init player count matrix
        pm = pd.DataFrame(players, columns=["player"]).drop_duplicates()
        stats = ["goals", "assists", "yellow cards", "red cards", "subbed on", "subbed off"]
        pm[stats] = 0

        # Count goal & assist events
        goal_events = team_df[(team_df["type"] == "Shot") & (team_df["shot_outcome"] == "Goal")]
        pm.loc[pm["player"].isin(goal_events["player"]), "goals"] = (
            goal_events["player"].value_counts()
        )

        if "pass_goal_assist" in team_df.columns:
            assist_events = team_df[team_df["pass_goal_assist"] == True]
            pm.loc[pm["player"].isin(assist_events["player"]), "assists"] = (
                assist_events["player"].value_counts()
            )

        # Cards
        if "bad_behaviour_card" in team_df.columns:
            yc = team_df[team_df["bad_behaviour_card"] == "Yellow Card"]
            rc = team_df[team_df["bad_behaviour_card"] == "Red Card"]
            pm.loc[pm["player"].isin(yc["player"]), "yellow cards"] = yc["player"].value_counts()
            pm.loc[pm["player"].isin(rc["player"]), "red cards"] = rc["player"].value_counts()

        # Substitutions
        subs = team_df[team_df["type"] == "Substitution"]
        pm.loc[pm["player"].isin(subs["player"]), "subbed off"] = subs["player"].value_counts()
        pm.loc[pm["player"].isin(subs["substitution_replacement"]), "subbed on"] = (
            subs["substitution_replacement"].value_counts()
        )

        # Score breakdown by period
        for _, shot in goal_events.iterrows():
            period = shot.get("period", None)
            if period in (1, 2):
                if team == home_team:
                    home_score_norm += 1
                else:
                    away_score_norm += 1
            elif period in (3, 4):
                if team == home_team:
                    home_score_et += 1
                else:
                    away_score_et += 1
            elif period == 5:
                if team == home_team:
                    home_score_pen += 1
                else:
                    away_score_pen += 1

        # Build emoji string
        pm["contributions"] = (
            pm["goals"].apply(lambda x: "⚽" * int(x)) +
            pm["assists"].apply(lambda x: "🅰️" * int(x)) +
            pm["yellow cards"].apply(lambda x: "🟨" * int(x)) +
            pm["red cards"].apply(lambda x: "🟥" * int(x)) +
            pm["subbed on"].apply(lambda x: "🔺" * int(x)) +
            pm["subbed off"].apply(lambda x: "🔻" * int(x))
        )

        # Assign to correct side
        if team == home_team:
            home_team_data = pm[["player", "contributions"]]
        else:
            away_team_data = pm[["player", "contributions"]]

    return (
        home_team_data,
        away_team_data,
        home_team,
        away_team,
        home_score_norm,
        away_score_norm,
        home_score_et,
        away_score_et,
        home_score_pen,
        away_score_pen,
    )



