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
        if df.empty:
            logging.warning(f"No data for team: {team}")
            return pd.DataFrame(columns=["player", "contributions"])

        # Players
        starting = df[df["type"] == "Starting XI"]["tactics"]
        starters = extract_player_names(starting.iloc[0]) if not starting.empty else []
        subs = df[df["type"] == "Substitution"]
        replacements = subs["substitution_replacement"].dropna().tolist()
        players = starters + replacements
        pm = pd.DataFrame({"player": players})

        # Initialize counts
        for stat in ("goals", "assists", "yellow cards", "red cards", "subbed on", "subbed off"):
            pm[stat] = 0

        # Stats extraction
        shots = df[df["type"] == "Shot"]
        goal_players = shots[shots["shot_outcome"] == "Goal"]["player"]

        assists = df[df.get("pass_goal_assist", False) == True]["player"] if "pass_goal_assist" in df.columns else pd.Series(dtype=str)
        yellows = df[df.get("bad_behaviour_card", "") == "Yellow Card"]["player"] if "bad_behaviour_card" in df.columns else pd.Series(dtype=str)
        reds = df[df.get("bad_behaviour_card", "") == "Red Card"]["player"] if "bad_behaviour_card" in df.columns else pd.Series(dtype=str)

        # Goal phase counting
        for _, shot in shots[shots["shot_outcome"] == "Goal"].iterrows():
            p = shot.get("period", None)
            nonlocal home_norm, away_norm, home_et, away_et, home_pen, away_pen
            if p in (1, 2):
                home_norm += (team == home_team)
                away_norm += (team == away_team)
            elif p in (3, 4):
                home_et += (team == home_team)
                away_et += (team == away_team)
            elif p == 5:
                home_pen += (team == home_team)
                away_pen += (team == away_team)

        # Sub goals and subs counts
        pm.loc[pm["player"].isin(goal_players), "goals"] += 1
        pm.loc[pm["player"].isin(assists), "assists"] += 1
        pm.loc[pm["player"].isin(yellows), "yellow cards"] += 1
        pm.loc[pm["player"].isin(reds), "red cards"] += 1
        pm.loc[pm["player"].isin(replacements), "subbed on"] += 1
        pm.loc[pm["player"].isin(subs["player"].dropna()), "subbed off"] += 1

        # Ensure int
        pm = pm.fillna(0).astype({c: "Int64" for c in pm.columns if c != "player"})

        # Build emoji string (no commas!)
        def build_emoji(count, emoji):
            return emoji * int(count) if pd.notna(count) and count > 0 else ""

        pm["contributions"] = pm.apply(
            lambda row:
                build_emoji(row["goals"], "⚽") +
                build_emoji(row["assists"], "🅰️") +
                build_emoji(row["yellow cards"], "🟨") +
                build_emoji(row["red cards"], "🟥") +
                build_emoji(row["subbed on"], "🔺") +
                build_emoji(row["subbed off"], "🔻"),
            axis=1
        )

        return pm[["player", "contributions"]]

    return (
        process_team(home_team),
        process_team(away_team),
        home_team, away_team,
        home_norm, away_norm,
        home_et, away_et,
        home_pen, away_pen
    )
