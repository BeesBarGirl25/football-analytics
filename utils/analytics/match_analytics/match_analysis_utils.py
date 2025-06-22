import pandas as pd

def extract_player_names(row):
    return [player['player']['name'] for player in row['lineup']]

def goal_assist_stats(match_data: pd.DataFrame, home_team: str, away_team: str):
    home_norm = away_norm = home_et = away_et = home_pen = away_pen = 0

    def process_team(team):
        df = match_data[match_data['team'] == team].copy()

        # Get starters and subs:
        starting = df.loc[df['type']=='Starting XI', 'tactics']
        starters = extract_player_names(starting.iloc[0]) if not starting.empty else []
        replacements = df.loc[df['type']=='Substitution','substitution_replacement'].dropna().tolist()
        players = starters + replacements
        pm = pd.DataFrame({'player': players})

        # initialize counters
        for col in ('goals','assists','yellow cards','red cards','subbed on','subbed off'):
            pm[col] = 0

        # count goals per player
        goal_players = df.loc[df['type']=='Shot']
        gp_counts = goal_players[goal_players['shot_outcome']=='Goal'].groupby('player').size()
        for pl, cnt in gp_counts.items():
            pm.loc[pm['player']==pl, 'goals'] = cnt

        # count assists, yellows, reds
        for col, pref, val in [
            ('assists','pass_goal_assist', True),
            ('yellow cards','bad_behaviour_card','Yellow Card'),
            ('red cards','bad_behaviour_card','Red Card')
        ]:
            sel = df[df[pref].fillna(False) == val] if col!='assists' else df[df[pref]==True]
            counts = sel.groupby('player').size()
            for pl, cnt in counts.items():
                pm.loc[pm['player']==pl, col] = cnt

        # subs on/off
        subs = df[df['type']=='Substitution']
        pm.loc[pm['player'].isin(subs['substitution_replacement']), 'subbed on'] += 1
        pm.loc[pm['player'].isin(subs['player']), 'subbed off'] += 1

        # periods/goals for types
        shots = df[df['type']=='Shot'][['period','player','shot_outcome']]
        for _, row in shots[shots['shot_outcome']=='Goal'].iterrows():
            period = row['period']
            is_home = (team == home_team)
            if period in [1,2]:
                home_norm if is_home else away_norm
            elif period in [3,4]:
                home_et if is_home else away_et
            elif period==5:
                home_pen if is_home else away_pen

        # build emojis
        pm = pm.fillna(0).astype({c:'Int64' for c in pm.columns if c!='player'})
        pm['contributions'] = (
            pm['goals'].apply(lambda x: '⚽'*x) +
            pm['assists'].apply(lambda x: '🅰️'*x) +
            pm['yellow cards'].apply(lambda x: '🟨'*x) +
            pm['red cards'].apply(lambda x: '🟥'*x) +
            pm['subbed on'].apply(lambda x: '🔺'*x) +
            pm['subbed off'].apply(lambda x: '🔻'*x)
        )
        return pm[['player','contributions']]

    home_df = process_team(home_team)
    away_df = process_team(away_team)

    return home_df, away_df, home_team, away_team, home_norm, away_norm, home_et, away_et, home_pen, away_pen
