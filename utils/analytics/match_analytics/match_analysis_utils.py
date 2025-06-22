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
    # Initialize summary stats
    home_norm = away_norm = home_et = away_et = home_pen = away_pen = 0
    home_team_data = away_team_data = None

    for team in (home_team, away_team):
        team_df = match_data[match_data["team"] == team]

        # Build player roster DataFrame
        starters = extract_player_names(team_df[team_df["type"] == "Starting XI"]["tactics"].iloc[0])
        subs_out = team_df[team_df["type"] == "Substitution"]["player"]
        subs_in = team_df[team_df["type"] == "Substitution"]["substitution_replacement"]
        players = list(starters) + list(subs_in)
        pm = pd.DataFrame({"player": pd.unique(players)})

        # Count contributions
        shots = team_df[team_df["type"] == "Shot"]
        goals = shots[shots["shot_outcome"] == "Goal"]["player"].value_counts()
        assists = team_df[team_df.get("pass_goal_assist", False) == True]["player"].value_counts()
        yellow = team_df[team_df.get("bad_behaviour_card", "") == "Yellow Card"]["player"].value_counts()
        red = team_df[team_df.get("bad_behaviour_card", "") == "Red Card"]["player"].value_counts()
        off = subs_out.value_counts()
        on = subs_in.value_counts()

        # Map counts to DataFrame
        pm["goals"] = pm["player"].map(goals).fillna(0).astype(int)
        pm["assists"] = pm["player"].map(assists).fillna(0).astype(int)
        pm["yellow cards"] = pm["player"].map(yellow).fillna(0).astype(int)
        pm["red cards"] = pm["player"].map(red).fillna(0).astype(int)
        pm["subbed off"] = pm["player"].map(off).fillna(0).astype(int)
        pm["subbed on"] = pm["player"].map(on).fillna(0).astype(int)

        # Build contributions string with repeated emojis
        pm["contributions"] = (
            pm["goals"].apply(lambda x: "⚽" * x) +
            pm["assists"].apply(lambda x: "🅰️" * x) +
            pm["yellow cards"].apply(lambda x: "🟨" * x) +
            pm["red cards"].apply(lambda x: "🟥" * x) +
            pm["subbed on"].apply(lambda x: "🔺" * x) +
            pm["subbed off"].apply(lambda x: "🔻" * x)
        )

        # Update match stats based on periods
        goal_periods = shots[shots["shot_outcome"] == "Goal"][["period", "player"]]
        for _, row in goal_periods.iterrows():
            period = row["period"]
            if period in (1, 2):
                if team == home_team:
                    home_norm += 1
                else:
                    away_norm += 1
            elif period in (3, 4):
                if team == home_team:
                    home_et += 1
                else:
                    away_et += 1
            elif period == 5:
                if team == home_team:
                    home_pen += 1
                else:
                    away_pen += 1

        # Assign DataFrame to correct team
        team_data = pm[["player", "contributions"]]
        if team == home_team:
            home_team_data = team_data
        else:
            away_team_data = team_data

    # Return all ten values in the original signature
    return (
        home_team_data,
        away_team_data,
        home_team,
        away_team,
        home_norm,
        away_norm,
        home_et,
        away_et,
        home_pen,
        away_pen,
    )



