import pandas as pd
import plotly.graph_objects as go
import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px

from collections import defaultdict



competitions_leagues = [
    'England',
    'France',
    'Germany',
    'Italy',
    'Spain'
]
competitions = [
    'England',
    'France',
    'Germany',
    'Italy',
    'Spain',
    'European_Championship',
    'World_Cup'
]


def preprare_data(competitions=competitions):
    folder_path = ''
    competitions_ranking = {}
    competitions_values = {}
    competitions_vaep_rating = {}
    competitions_player_list = {}
    for i in range(len(competitions)):
        competitions_ranking[competitions[i]] = pd.read_csv(folder_path + competitions[i] + '_ranking_p90.csv')
        competitions_values[competitions[i]] = pd.read_csv(folder_path + competitions[i] + '_values.csv')
        competitions_vaep_rating[competitions[i]] = competitions_ranking[competitions[i]]['vaep_rating'][:10].to_list()
        competitions_player_list[competitions[i]] = competitions_ranking[competitions[i]]['short_name'][:10].to_list()
    return competitions_ranking, competitions_values, competitions_vaep_rating, competitions_player_list


competitions_ranking, competitions_values, competitions_vaep_rating, competitions_player_list = preprare_data()

layout = go.Layout(
  margin=go.layout.Margin(
        l=2, # left margin
        r=0, # right margin
        b=0, # bottom margin
        t=0, # top margin
    ),paper_bgcolor='#002b36',plot_bgcolor='#002b36'
)


def fig_bars(competitions=competitions, competitions_player_list=competitions_player_list,
             competitions_vaep_rating=competitions_vaep_rating):
    bar_figures = {}
    for i in range(len(competitions)):
        print(i)
        fig = px.line(x=competitions_player_list[competitions[i]], y=competitions_vaep_rating[competitions[i]],
                      color=px.Constant(""),
                      labels=dict(x="Players", y="Vaep Rating", color=competitions[i]))
        fig.add_bar(x=competitions_player_list[competitions[i]], y=competitions_vaep_rating[competitions[i]],
                    name="Player Rating")
        fig.update_layout(layout, font_color='white')
        fig.update_traces(marker_color='#a9bdbd', selector=dict(type='bar'))
        bar_figures[competitions[i]] = fig
    return bar_figures


bar_figures = fig_bars()


# prepare data for summary boxes --- using competitions_values
def competition_summary(competitions=competitions, competitions_values=competitions_values):
    total_goals = {}
    shots_per_goal = {}
    Average_goals_per_match = {}
    Average_fouls_per_match = {}
    for i in range(len(competitions)):
        shot_goals = sum((competitions_values[competitions[i]][
                              competitions_values[competitions[i]]['type_name'] == 'shot']['result_name'].reset_index(
            drop=True) == "success").to_list())

        Penalty_goals = sum((competitions_values[competitions[i]][
                                 competitions_values[competitions[i]]['type_name'] == 'shot_penalty'][
                                 'result_name'].reset_index(drop=True) == "success").to_list())

        freekick_shot_goals = sum((competitions_values[competitions[i]][
                                       competitions_values[competitions[i]]['type_name'] == 'shot_freekick'][
                                       'result_name'].reset_index(drop=True) == "success").to_list())

        # c1
        total_goals[competitions[i]] = shot_goals + Penalty_goals + freekick_shot_goals
        shots = len(competitions_values[competitions[i]][competitions_values[competitions[i]]['type_name'] == 'shot'])
        # c2
        shots_per_goal[competitions[i]] = round(shots / total_goals[competitions[i]], 2)

        # c3
        if competitions[i] in competitions_leagues:
            if competitions[i] == 'Germany':
                Average_goals_per_match[competitions[i]] = round(total_goals[competitions[i]] / 306, 2)
                fouls = len(
                    competitions_values[competitions[i]][competitions_values[competitions[i]]['type_name'] == 'foul'])
                # c4
                Average_fouls_per_match[competitions[i]] = round(fouls / 306, 2)
            else:
                Average_goals_per_match[competitions[i]] = round(total_goals[competitions[i]] / 380, 2)
                fouls = len(
                    competitions_values[competitions[i]][competitions_values[competitions[i]]['type_name'] == 'foul'])
                # c4
                Average_fouls_per_match[competitions[i]] = round(fouls / 380, 2)
        else:
            Average_goals_per_match[competitions[i]] = round(total_goals[competitions[i]] / 64, 2)
            fouls = len(
                competitions_values[competitions[i]][competitions_values[competitions[i]]['type_name'] == 'foul'])
            # c4
            Average_fouls_per_match[competitions[i]] = round(fouls / 64, 2)

    return total_goals, shots_per_goal, Average_goals_per_match, Average_fouls_per_match


total_goals, shots_per_goal, Average_goals_per_match, Average_fouls_per_match = competition_summary()

#best 3 player radars  --- using competitions_values
top_players=[]
player_radars = {}
def fig_player_radars(competitions_player_list=competitions_player_list,competitions_values=competitions_values,top_players=top_players,radars_figures=defaultdict(list)):
    for i in range(len(competitions)) :
        top_players = competitions_player_list[competitions[i]][:3]
        for j in range(len(top_players)):
            current_player=competitions_values[competitions[i]][competitions_values[competitions[i]]['short_name']==top_players[j]]

            player_radars_fouls = len(current_player[current_player['type_name']=='foul'])
            player_radars_pass =len(current_player[current_player['type_name']=='pass'])
            player_radars_take_on =len(current_player[current_player['type_name']=='take_on'])
            player_radars_tackle =len(current_player[current_player['type_name']=='tackle'])
            player_radars_shot =len(current_player[current_player['type_name']=='shot'])

            #plot them
            if competitions[i] in competitions_leagues:
                current_player_df = pd.DataFrame(dict(
                    r=[player_radars_fouls, player_radars_pass/30, player_radars_take_on, player_radars_tackle, player_radars_shot],
                    theta=['Fouls','Passes','Take on','Tackles', 'Shots']))
                fig = px.line_polar(current_player_df, r='r', theta='theta', line_close=True,template="plotly_dark")
            else:
                current_player_df = pd.DataFrame(dict(
                    r=[player_radars_fouls, player_radars_pass/60, player_radars_take_on, player_radars_tackle, player_radars_shot],
                    theta=['Fouls','Passes','Take on','Tackles', 'Shots']))
                fig = px.line_polar(current_player_df, r='r', theta='theta', line_close=True,template="plotly_dark")
            color = "#FFD700"
            if j == 1:
                color = "#C0C0C0"
            elif j == 2:
                color = '#CD7F32'
            fig.update_traces(fill='toself',fillcolor=color,line_color=color,opacity=0.6)
            fig.update_layout(title="Rank : "+str(j+1)+' '+top_players[j],font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color=color
                ),paper_bgcolor='#073642',plot_bgcolor='#073642')
            # if not isinstance(radars_figures[competitions[i]], list):
            #     radars_figures[competitions[i]] = [radars_figures[competitions[i]]]
            radars_figures[competitions[i]].append(fig)
    return radars_figures
radars_figures = fig_player_radars()

app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR])
server=app.server
app.title = 'Player Ratings'
app.layout = html.Div(
    [
        dbc.Row(
            dbc.Col(html.H1("Player Rating Dashboard",
                            style={"color": "#839496", "fontSize": 65, "textAlign": "center", }), )),
        dbc.Row(
            [dbc.Col(html.Div(children=[
                html.H1(children='Goals', style={'font-weight': 'bold', 'color': '#839496', 'textAlign': 'Center'}),
                html.H2(id='goals_Area', style={'font-weight': 'bold', 'color': 'White', 'textAlign': 'Center'})],
                style={'backgroundColor': '#073642', 'border': '15px solid #073642', 'border-radius': '20px'}
                , className='two columns'), ),
                dbc.Col(html.Div(children=[
                    html.H1(children='Shots per Goal',
                            style={'font-weight': 'bold', 'color': '#839496', 'textAlign': 'Center'}),
                    html.H2(id='shots_pg_Area',
                            style={'font-weight': 'bold', 'color': 'White', 'textAlign': 'Center'})],
                    style={'backgroundColor': '#073642', 'border': '15px solid #073642', 'border-radius': '20px'}
                    , className='two columns'), ),
                dbc.Col(html.Div(children=[
                    html.H1(children='Goals per Match',
                            style={'font-weight': 'bold', 'color': '#839496', 'textAlign': 'Center'}),
                    html.H2(id='goals_pm_Area',
                            style={'font-weight': 'bold', 'color': 'White', 'textAlign': 'Center'})],
                    style={'backgroundColor': '#073642', 'border': '15px solid #073642', 'border-radius': '20px'}
                    , className='two columns'), ),
                dbc.Col(html.Div(children=[
                    html.H1(children='Fouls per Match',
                            style={'font-weight': 'bold', 'color': '#839496', 'textAlign': 'Center'}),
                    html.H2(id='fouls_pm_Area',
                            style={'font-weight': 'bold', 'color': 'White', 'textAlign': 'Center'})],
                    style={'backgroundColor': '#073642', 'border': '15px solid #073642', 'border-radius': '20px'}
                    , className='two columns'), ),
            ],
        ),
        dbc.Row([dbc.Col(
            dcc.Dropdown(
                id='dropdown',
                optionHeight=40,
                placeholder='Choose Tournement',
                options=[
                    {'label': 'English Premier League', 'value': 1},
                    {'label': 'French  Ligue 1', 'value': 2},
                    {'label': 'Germany Bundesliga', 'value': 3},
                    {'label': 'Italy Serie A', 'value': 4},
                    {'label': 'Spanish la liga', 'value': 5},
                    {'label': 'Euro Cup 2016', 'value': 6},
                    {'label': 'World Cup 2018', 'value': 7}
                ], value=7
            ), ),
        ]),
        dbc.Row(dbc.Col([dcc.Graph(id="Bar_fig")])),
        dbc.Row([
            dbc.Col([dcc.Graph(id="rank_1_fig")]),
            dbc.Col([dcc.Graph(id="rank_2_fig")]),
            dbc.Col([dcc.Graph(id="rank_3_fig")]),
        ]),
    ]
)


@app.callback(
    [Output('Bar_fig', 'figure'),
     Output('rank_1_fig', 'figure'),
     Output('rank_2_fig', 'figure'),
     Output('rank_3_fig', 'figure'),
     Output('goals_Area', 'children'),
     Output('shots_pg_Area', 'children'),
     Output('goals_pm_Area', 'children'),
     Output('fouls_pm_Area', 'children')],
    Input('dropdown', 'value'))
def update(value):
    rank = bar_figures[competitions[0]]
    rank_1 = radars_figures[competitions[0]][0]
    rank_2 = radars_figures[competitions[0]][1]
    rank_3 = radars_figures[competitions[0]][2]
    c1 = total_goals[competitions[0]]
    c2 = shots_per_goal[competitions[0]]
    c3 = Average_goals_per_match[competitions[0]]
    c4 = Average_fouls_per_match[competitions[0]]
    if value:
        print(value)
        value -= 1
        rank = bar_figures[competitions[value]]
        rank_1 = radars_figures[competitions[value]][0]
        rank_2 = radars_figures[competitions[value]][1]
        rank_3 = radars_figures[competitions[value]][2]
        c1 = total_goals[competitions[value]]
        c2 = shots_per_goal[competitions[value]]
        c3 = Average_goals_per_match[competitions[value]]
        c4 = Average_fouls_per_match[competitions[value]]

    return [rank, rank_1, rank_2, rank_3, c1, c2, c3, c4]


app.run_server()
