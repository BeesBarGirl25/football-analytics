import pandas as pd
import logging

def goal_assist_stats(match_data: pd.DataFrame, home_team: str, away_team: str):
    logging.info("Starting goal_assist_stats")

    # initialize team summary containers
    summaries = {}

    for team in [home_team, away_team]:
        team_df = match_data[match_data['team'] == team]
        players = []
        # collect starter + substitutes
        try:
            starters = extract_player_names(team_df[team_df['type'] == 'Starting XI']['tactics'].iloc[0])
        except IndexError:
            starters = []
        subs = team_df[team_df['type'] == 'Substitution']['substitution_replacement'].tolist()
        players = list(set(starters + subs))

        # table to fill
        pm = pd.DataFrame({'player': players})
        pm[['goals','assists','yellow cards','red cards','subbed on','subbed off']] = 0

        # count each event type
        goal_counts = team_df.query("type=='Shot' and shot_outcome=='Goal'")['player'].value_counts()
        assist_counts = team_df.query("pass_goal_assist==True")['player'].value_counts()
        yellow_counts = team_df.query("bad_behaviour_card=='Yellow Card'")['player'].value_counts()
        red_counts = team_df.query("bad_behaviour_card=='Red Card'")['player'].value_counts()
        sub_on_counts = team_df.query("type=='Substitution'")['substitution_replacement'].value_counts()
        sub_off_counts = team_df.query("type=='Substitution'")['player'].value_counts()

        # apply counts
        for col, vc in [('goals', goal_counts), ('assists', assist_counts),
                        ('yellow cards', yellow_counts), ('red cards', red_counts),
                        ('subbed on', sub_on_counts), ('subbed off', sub_off_counts)]:
            pm[col] = pm['player'].map(vc).fillna(0).astype(int)

        # build emoji string
        pm['contributions'] = (
            pm['goals'].apply(lambda x: '⚽' * x) +
            pm['assists'].apply(lambda x: '🅰️' * x) +
            pm['yellow cards'].apply(lambda x: '🟨' * x) +
            pm['red cards'].apply(lambda x: '🟥' * x) +
            pm['subbed on'].apply(lambda x: '🔺' * x) +
            pm['subbed off'].apply(lambda x: '🔻' * x)
        )

        summaries[team] = pm[['player','contributions']]

    # extract team summaries
    home_df = summaries[home_team]
    away_df = summaries[away_team]

    logging.info(f"{home_team} contributions:\n{home_df}")
    logging.info(f"{away_team} contributions:\n{away_df}")

    return home_df, away_df
