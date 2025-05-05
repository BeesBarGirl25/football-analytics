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

def extract_player_names(row):
    return [player['player']['name'] for player in row['lineup']]

def goal_assist_stats(match_data):
    home_team, away_team = match_data['team'].unique()
    home_team_score_normal_time = 0
    away_team_score_normal_time = 0
    home_team_extra_time_score = 0
    away_team_extra_time_score = 0
    home_team_penalty_score = 0
    away_team_penalty_score = 0

    for team in home_team, away_team:
        team_data = match_data[match_data['team'] == team]
        starting_list = team_data[team_data['type'] == 'Starting XI']['tactics'].iloc[0]
        starting_players = extract_player_names(starting_list)
        subbed_players = team_data[team_data['type'] == 'Substitution']['substitution_replacement'].tolist()
        player_list = starting_players + subbed_players

        player_matrix = pd.DataFrame(player_list, columns=['player'])
        player_matrix[['goals', 'assists', 'red cards', 'yellow cards', 'subbed on', 'subbed off']] = 0

        # Initialize empty DataFrames
        assist_rows = pd.DataFrame(columns=['player'])
        yellow_rows = pd.DataFrame(columns=['player'])
        red_rows = pd.DataFrame(columns=['player'])

        if 'pass_goal_assist' in team_data.columns:
            assist_rows = team_data[team_data['pass_goal_assist'] == True][['player']]

        goal_rows = team_data[(team_data['type'] == 'Shot') & (team_data['shot_outcome'] == 'Goal')][['player']]
        logging.info(f"Team: {team}")
        logging.info(f"goal_rows: {goal_rows}")
        for period in team_data[(team_data['type'] == 'Shot') & (team_data['shot_outcome'] == 'Goal')][
            'period'].tolist():
            logging.info(f"Period: {period}")
            logging.info(f"period type: {type(period)}")

            # Ensure 'period' is treated as a string or integer as appropriate
            if period in [1, 2] and team_data['period'].max() < 3:
                # Normal time score
                logging.info(f"Normal time score")
                if team == home_team:
                    home_team_score_normal_time += 1
                else:
                    away_team_score_normal_time += 1

            elif period in [1, 2] and team_data['period'].max() > 2:
                logging.info(f"Normal Time Extra time score")
                # Normal and extra time combined
                if team == home_team:
                    home_team_score_normal_time += 1
                    home_team_extra_time_score += 1
                else:
                    away_team_score_normal_time += 1
                    away_team_extra_time_score += 1

            elif period in [3, 4]:
                logging.info(f"Extra time score")
                # Extra time score
                if team == home_team:
                    home_team_extra_time_score += 1
                else:
                    away_team_extra_time_score += 1

            elif period == 5:
                logging.info(f"Penalty shootout score")
                # Penalty shootout score
                if team == home_team:
                    home_team_penalty_score += 1
                else:
                    away_team_penalty_score += 1

        logging.info(f"Home team score: {home_team_score_normal_time}")
        logging.info(f"Away team score: {away_team_score_normal_time}")
        logging.info(f"Home team extra time score: {home_team_extra_time_score}")
        logging.info(f"Away team extra time score: {away_team_extra_time_score}")
        logging.info(f"Home team penalty score: {home_team_penalty_score}")
        logging.info(f"Away team penalty score: {away_team_penalty_score}")



        if 'bad_behaviour_card' in team_data.columns:
            yellow_rows = team_data[team_data['bad_behaviour_card'] == 'Yellow Card'][['player']]
            red_rows = team_data[team_data['bad_behaviour_card'] == 'Red Card'][['player']]

        subs_rows = team_data[team_data['type'] == 'Substitution']
        off = subs_rows[['player']]
        on = subs_rows[['substitution_replacement']]

        # Update stats
        player_matrix.loc[player_matrix['player'].isin(assist_rows['player']), 'assists'] += 1
        player_matrix.loc[player_matrix['player'].isin(goal_rows['player']), 'goals'] += 1
        player_matrix.loc[player_matrix['player'].isin(yellow_rows['player']), 'yellow cards'] += 1
        player_matrix.loc[player_matrix['player'].isin(red_rows['player']), 'red cards'] += 1
        player_matrix.loc[player_matrix['player'].isin(off['player']), 'subbed off'] += 1
        player_matrix.loc[player_matrix['player'].isin(on['substitution_replacement']), 'subbed on'] += 1

        # Emoji mapping
        goal_emoji = '⚽'
        assist_emoji = '🅰️'
        yellow_card_emoji = '🟨'
        red_card_emoji = '🟥'
        sub_on_emoji = '🔼'
        sub_off_emoji = '🔽'

        player_matrix['contributions'] = (
            player_matrix['goals'].apply(lambda x: goal_emoji * x) +
            player_matrix['assists'].apply(lambda x: assist_emoji * x) +
            player_matrix['yellow cards'].apply(lambda x: yellow_card_emoji * x) +
            player_matrix['red cards'].apply(lambda x: red_card_emoji * x) +
            player_matrix['subbed on'].apply(lambda x: sub_on_emoji * x) +
            player_matrix['subbed off'].apply(lambda x: sub_off_emoji * x)
        )

        if team == home_team:
            home_team_data = player_matrix[['player', 'contributions']]
        else:
            away_team_data = player_matrix[['player', 'contributions']]

    return home_team_data, away_team_data, home_team, away_team, home_team_score_normal_time, away_team_score_normal_time, home_team_extra_time_score, away_team_extra_time_score, home_team_penalty_score, away_team_penalty_score
