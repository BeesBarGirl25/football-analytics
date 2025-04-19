import plotly.graph_objects as go
from utils.analytics.match_analytics.match_analysis_utils import cumulative_stats


def generate_match_graph_plot(match_data):
    # Filter match data for only the required columns
    match_data = match_data[['team', 'minute', 'shot_outcome', 'shot_statsbomb_xg', 'period']]

    # Separate stats for Team 1 and Team 2
    team_1 = match_data[match_data['team'] == match_data['team'].unique()[0]]
    team_2 = match_data[match_data['team'] == match_data['team'].unique()[1]]

    team_1_stats = cumulative_stats(team_1)
    team_2_stats = cumulative_stats(team_2)

    # Extract team names dynamically
    team_1_name = team_1_stats['team'].iloc[0]
    team_2_name = team_2_stats['team'].iloc[0]

    # Dynamically determine the max values for x and y axes
    y_max = max(team_1_stats['cum_xg'].max(), team_1_stats['cum_goals'].max(),
                team_2_stats['cum_xg'].max(), team_2_stats['cum_goals'].max())
    x_max = max(team_1_stats['minute'].max(), team_2_stats['minute'].max())

    # Convert data to lists here to avoid serialization issues
    x_team1_stats = team_1_stats['minute'].tolist()
    y_cum_xg_team1 = team_1_stats['cum_xg'].tolist()
    y_cum_goals_team1 = team_1_stats['cum_goals'].tolist()

    x_team2_stats = team_2_stats['minute'].tolist()
    y_cum_xg_team2 = team_2_stats['cum_xg'].tolist()
    y_cum_goals_team2 = team_2_stats['cum_goals'].tolist()

    # Initialize Plotly traces (data)
    data = [
        # Team 1 traces
        go.Scatter(
            x=x_team1_stats,
            y=y_cum_xg_team1,
            mode='lines',
            name=f'{team_1_name} xG',
            line=dict(color='red', dash='dash')
        ),
        go.Scatter(
            x=x_team1_stats,
            y=y_cum_goals_team1,
            mode='lines',
            name=f'{team_1_name} Goals',
            line=dict(color='red')
        ),
        # Team 2 traces
        go.Scatter(
            x=x_team2_stats,
            y=y_cum_xg_team2,
            mode='lines',
            name=f'{team_2_name} xG',
            line=dict(color='blue', dash='dash')
        ),
        go.Scatter(
            x=x_team2_stats,
            y=y_cum_goals_team2,
            mode='lines',
            name=f'{team_2_name} Goals',
            line=dict(color='blue')
        )
    ]

    # Add annotations and shading for extra time and penalties if applicable
    unique_periods = match_data['period'].unique()
    shapes = []
    annotations = []

    # Extra time shading (90–120 mins)
    if not set(unique_periods).issubset({1, 2}):
        shapes.append(dict(
            type="rect",
            x0=90, x1=x_max, y0=0, y1=y_max + 0.5,
            fillcolor="rgba(0, 255, 0, 0.2)",  # Semi-transparent green fill
            line=dict(color="rgba(0, 255, 0, 0)")
        ))
        annotations.append(dict(
            x=(90 + x_max) / 2, y=y_max + 0.5,
            text="Extra Time",
            showarrow=False,
            font=dict(color="green", size=12)
        ))

    # Penalty shootout shading (120+ mins)
    if match_data['period'].max() == 5:
        shapes.append(dict(
            type="rect",
            x0=120, x1=match_data['minute'].max(), y0=0, y1=y_max + 0.5,
            fillcolor="rgba(255, 0, 0, 0.2)",  # Semi-transparent red fill
            line=dict(color="rgba(255, 0, 0, 0)")
        ))
        annotations.append(dict(
            x=(120 + match_data['minute'].max()) / 2, y=y_max + 0.5,
            text="Penalties",
            showarrow=False,
            font=dict(color="red", size=12)
        ))

    # Define the layout of the graph
    layout = go.Layout(
        title=dict(
            text='xG and Goals per Game',
            font=dict(color='white', size=18),
            x=0.5
        ),
        xaxis=dict(
            title='Minutes',
            color='white',
            gridcolor='rgba(255, 255, 255, 0.1)',
            showline=True,
            linecolor='rgba(255, 255, 255, 0.2)'
        ),
        yaxis=dict(
            title='Goals',
            color='white',
            gridcolor='rgba(255, 255, 255, 0.1)',
            showline=True,
            linecolor='rgba(255, 255, 255, 0.2)',
            range=[0, y_max + 1]  # Add buffer
        ),
        legend=dict(
            orientation='h',  # horizontal layout
            yanchor='top',
            y=-0.25,  # adjust vertically (play with -0.3 or -0.35 if needed)
            xanchor='center',
            x=0.5,  # center it horizontally
            font=dict(color='white', size=12),
            bgcolor='rgba(0,0,0,0)'  # transparent background
        ),
        autosize=True,
        margin=dict(l=40, r=40, t=60, b=100),
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        shapes=shapes,
        annotations=annotations
    )

    return {"data": data, "layout": layout}

