import pandas as pd
import logging

def cumulative_stats(team_data):
    team_data['goals']=team_data['shot_outcome'].apply(lambda x: 1 if x == 'Goal' else 0)
    team_data.replace(-999, 0, inplace=True)
    team_data=team_data.sort_values('minute')
    team_data['cum_goals']=0
    team_data['cum_xg']=0
    team_data['cum_goals']=team_data['goals'].cumsum()
    team_data['cum_xg']=team_data['shot_statsbomb_xg'].cumsum()
    return team_data

def goal_assist_data(match_data):
    home_team, away_team = match_data['team'].unique()
    goals = match_data[match_data['shot_outcome'] == 'Goal']

    logging.debug(f"goals: {goals}")

    goals_home = {}
    assists_home = {}
    goals_away = {}
    assists_away = {}

    for id, row in goals.iterrows():
        if row['team'] == home_team:
            if row['player'] not in goals_home:
                goals_home[row['player']] = []
            goals_home[row['player']].append(str(row['minute']))
            if not (row['shot_key_pass_id'] == -999):
                assist = match_data[match_data['id'] == row['shot_key_pass_id']]
                if not assist.empty:
                    assist_player = assist['player'].iloc[0]
                    if assist_player not in assists_home:
                        assists_home[assist_player] = []
                    assists_home[assist_player].append(
                        str(assist['minute'].iloc[0]))  # Store all assist minutes for this player

        # Process goals for the away team
        if row['team'] == away_team:
            if row['player'] not in goals_away:
                goals_away[row['player']] = []
            goals_away[row['player']].append(str(row['minute']))  # Store all minutes for this player
            if not pd.isna(row['shot_key_pass_id']):
                assist = match_data[match_data['id'] == row['shot_key_pass_id']]
                if not assist.empty:
                    assist_player = assist['player'].iloc[0]
                    if assist_player not in assists_away:
                        assists_away[assist_player] = []
                    assists_away[assist_player].append(
                        str(assist['minute'].iloc[0]))  # Store all assist minutes for this player

    logging.debug(f"goals_home: {goals_home}")
    logging.debug(f"assists_home: {assists_home}")
    logging.debug(f"goals_away: {goals_away}")
    logging.debug(f"assists_away: {assists_away}")



    # Format the results with combined minutes for multiple goals/assists
    formatted_goals_home = [
        ' '.join([f"{minute}'" for minute in minutes]) + f" {player} {'⚽' * len(minutes)}"
        for player, minutes in goals_home.items()
    ]
    formatted_assists_home = [
        ' '.join([f"{minute}'" for minute in minutes]) + f" {player} {'👟' * len(minutes)}"
        for player, minutes in assists_home.items()
    ]
    formatted_goals_away = [
        ' '.join([f"{minute}'" for minute in minutes]) + f" {player} {'⚽' * len(minutes)}"
        for player, minutes in goals_away.items()
    ]
    formatted_assists_away = [
        ' '.join([f"{minute}'" for minute in minutes]) + f" {player} {'👟' * len(minutes)}"
        for player, minutes in assists_away.items()
    ]

    home_score = match_data[(match_data['team'] == home_team) & (match_data['shot_outcome'] == 'Goal') & ((match_data['period'] == 1) | (match_data['period'] == 2))].shape[0]
    away_score = match_data[(match_data['team'] == away_team) & (match_data['shot_outcome'] == 'Goal') & ((match_data['period'] == 1) | (match_data['period'] == 2))].shape[0]

    return formatted_goals_home, formatted_assists_home, formatted_goals_away, formatted_assists_away, home_score, away_score, home_team, away_team



def discipline_analysis(match_data):

    def generate_strings(dataframe):
        return [f"Player: {row['player']}, Minute: {row['minute']}" for _, row in dataframe.iterrows()]

    if 'bad_behaviour_card' not in match_data.columns:
        return [],[],[],[]
    else:
        home_team, away_team = match_data['team'].unique()
        home_team_data = match_data[match_data['team'] == home_team]
        away_team_data = match_data[match_data['team'] == away_team]
        home_team_yellow = home_team_data[home_team_data['bad_behaviour_card'] == 'Yellow Card']
        home_team_red = home_team_data[home_team_data['bad_behaviour_card'] == 'Red Card']
        away_team_yellow = away_team_data[away_team_data['bad_behaviour_card'] == 'Yellow Card']
        away_team_red = away_team_data[away_team_data['bad_behaviour_card'] == 'Red Card']
        return generate_strings(home_team_yellow), generate_strings(home_team_red), generate_strings(away_team_yellow), generate_strings(away_team_red)