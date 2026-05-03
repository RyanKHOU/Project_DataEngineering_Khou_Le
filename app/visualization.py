
import os, plotly.express as px, requests
from dash import dcc, html, Input, Output, dash_table, State
from values import data, fig_gains,fig_reussites_echecs,fig_avg_successes,fig_time,time_to_seconds


DATA_READY_FILE = "/shared/data_ready"

# --------------------------------Application Dash ---------------------------------------------------

app = dash.Dash(
    __name__,
    external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
    suppress_callback_exceptions=True
)

# Couleurs
couleur_principale = 'black'
couleur_secondaire = '#404040'
couleur_texte = '#ffffff'

Tab_Style = {'backgroundColor': couleur_principale, 'color': couleur_texte}
Content_Style = {
    'backgroundColor': couleur_secondaire,
    'color': couleur_texte,
    'padding': '20px',
    'height': '100%'
}
Main_Style = {
    'backgroundColor': couleur_principale,
    'width': '90%',
    'float': 'left',
    'color': couleur_texte
}

# -------------------------------- Layout --------------------------------

def main_layout():
    return html.Div([

        # Barre de navigation
        html.Div([
            dcc.Tabs(
                id="tabs",
                value='tab-start',
                vertical=True,
                children=[
                    dcc.Tab(label="Introduction", value='tab-start', style=Tab_Style),
                    dcc.Tab(label="L'équipe la plus riche", value='tab-1', style=Tab_Style),
                    dcc.Tab(label="Taux échecs et réussites", value='tab-2', style=Tab_Style),
                    dcc.Tab(label="L'équipe la plus victorieuse", value='tab-3', style=Tab_Style),
                    dcc.Tab(label="L'équipe ayant le plus de temps", value='tab-4', style=Tab_Style),
                    dcc.Tab(label="Recherche", value='tab-search', style=Tab_Style)
                ],
                style={'height': '100vh'}
            )
        ], style={'width': '10%', 'float': 'left'}),

        html.Div([
            html.H3("Projet KHOU_LE : Analyse des équipes de Fort Boyard"),
            html.Div(id='tabs-content')
        ], style=Main_Style)
    ])

app.layout = html.Div(
    [
        dcc.Interval(id="check-data", interval=2000, n_intervals=0, disabled=False),
        html.Div(id="root-content")
    ]
)


@app.callback(
     Output("root-content", "children"),
    Output("check-data", "disabled"),
    Input("check-data", "n_intervals")
)
def display_app(_):
    if not os.path.exists(DATA_READY_FILE):
        # PAGE D'ATTENTE
        return (
            html.Div(
                [
                    html.H1("Récupération des données…<br>Merci de patienter"),
                    dcc.Loading(type="circle")
                ],
                style={
                    "textAlign": "center",
                    "marginTop": "150px",
                    "color": "white",
                    "backgroundColor": "black",
                    "height": "100vh"
                }
            ), False
        )

    # DASHBOARD NORMAL
    return (main_layout(), True)



# -------------------------------- Tabs Content --------------------------------

@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs', 'value')
)
def render_content(tab):

    if tab == 'tab-start':
        return html.Div([
            html.H3("Introduction "),
            html.Img(src='https://fs-prod-cdn.nintendo-europe.com/media/images/10_share_images/games_15/nintendo_switch_4/H2x1_NSwitch_FortBoyard_image1600w.jpg', style={'max-width': '75%', 'height': 'auto'}),
            html.P("Ce projet propose une analyse détaillée des performances des équipes ayant participé à Fort Boyard entre 2019 et 2023. En exploitant des données issues directement du jeu, nous explorerons différents aspects des défis rencontrés par les participants, mettant en lumière les stratégies gagnantes, les taux de réussite et d'échec, ainsi que l'efficacité des équipes dans la gestion du temps lors de l'épreuve finale.", style={'padding': '20px'}),
        ],style=Content_Style )

    if tab == 'tab-1':
        return html.Div([
            dcc.Graph(id='graph-gains', figure=fig_gains),
            dcc.Dropdown(
                id='dropdown-gains',
                options=[
                    {'label': 'Top 5', 'value': 5},
                    {'label': 'Top 10', 'value': 10},
                    {'label': 'Toutes les équipes', 'value': len(data)}
                ],
                value=len(data),
                style={'color': 'black'}
            ),
            html.P("Le gain final d'une équipe dans Fort Boyard est déterminé lors de l'épreuve finale, où les participants recueillent des pièces d'or dans une cage. Cette visualisation met en évidence les équipes qui ont excellé dans cette épreuve, capturant ainsi les plus grandes richesses. Les données révèlent non seulement les montants accumulés mais aussi la performance exceptionnelle de certaines équipes sous pression.", style={'padding': '20px'})

        ], style=Content_Style)

    if tab == 'tab-2':
        return html.Div([
            dcc.Graph(figure=fig_reussites_echecs),
            html.P("Cette section offre une comparaison approfondie entre les succès et les revers rencontrés par chaque équipe. En examinant le nombre d'épreuves réussies contre les échecs, nous pouvons identifier les stratégies qui ont conduit à la victoire ou à la défaite. Cette analyse fournit un aperçu précieux des dynamiques d'équipe et de l'importance de la préparation et de l'adaptabilité.", style={'padding': '20px'}),
        ], style=Content_Style)

    if tab == 'tab-3':
        return html.Div([
            dcc.Graph(figure=fig_avg_successes),
            html.P("L'analyse des performances globales révèle que les équipes ayant le plus de victoire ont souvent des membres qui ont déja participé à l'émission télévisée.", style={'padding': '20px'}),
        ], style=Content_Style)

    if tab == 'tab-4':
        return html.Div([
            html.H3("Quelle équipe a eu le plus de temps dans l'épreuve final?"),
            dcc.Graph(id='graph-time', figure=fig_time),
            dcc.Slider(
                id='slider-time',
                min=0,
                max=225,
                step=1,
                value=225,
                marks={i: str(i) for i in range(0, 226, 25)}
            ),
            html.P("L'épreuve finale de Fort Boyard est un défi contre la montre, où le temps alloué varie en fonction des performances antérieures de l'équipe. Cette section explore comment le temps accordé lors de cette épreuve finale influence le gain final et souligne l'importance de maximiser chaque seconde pour augmenter les chances de victoire.", style={'padding': '20px'}),
        ], style=Content_Style)

    if tab == 'tab-search':
        return html.Div([

            html.H3("Recherche par équipe"),

            dcc.Dropdown(
                id='search-dropdown',
                placeholder='Tapez le nom de l’équipe...',
                options=[
                    {'label': team['Equipe'], 'value': team['Equipe']}
                    for team in data
                ],
                style={'color': 'black'}
            ),

            dash_table.DataTable(
                id='team-info-table',
                columns=[
                    {'name': 'Membres', 'id': 'Membres'},
                    {'name': 'Quête des clés', 'id': 'QueteCles'},
                    {'name': 'Salle du Jugement', 'id': 'Jugement'},
                    {'name': 'Quête des indices', 'id': 'Indices'},
                    {'name': 'Salle du Conseil', 'id': 'Conseil'},
                    {'name': 'Réussites', 'id': 'Reussites'},
                    {'name': 'Échecs', 'id': 'Echecs'},
                    {'name': 'Gains', 'id': 'Gains'},
                    {'name': 'Temps', 'id': 'Temps'}
                ],
                style_cell={
                    'backgroundColor': 'black',
                    'color': 'white',
                    'textAlign': 'left',
                    'whiteSpace': 'normal'
                }
            ),

            html.Img(id='team-image', style={'marginTop': '20px', 'maxWidth': '60%'})

        ], style=Content_Style)

# -------------------------------- Callbacks --------------------------------

@app.callback(
    Output('graph-gains', 'figure'),
    Input('dropdown-gains', 'value')
)
def update_gains_graph(n):
    sorted_data = sorted(
        data,
        key=lambda x: int(x['Gains'].replace(" ", "")),
        reverse=True
    )[:n]

    return px.bar(
        x=[t['Equipe'] for t in sorted_data],
        y=[int(t['Gains'].replace(" ", "")) for t in sorted_data],
        labels={'x': 'Équipe', 'y': 'Gains'}
    )

@app.callback(
    Output('graph-time', 'figure'),
    Input('slider-time', 'value')
)
def update_time_graph(limit):
    filtered = [
        team for team in data if time_to_seconds(team['Temps']) <= limit
    ]

    if not filtered :
        return px.bar()

    return px.bar(
        x=[team['Equipe'] for team in filtered],
        y=[time_to_seconds(team['Temps']) for team in filtered],
        labels={'x': 'Équipe', 'y': 'Temps (s)'}
    )

@app.callback(
    Output('team-info-table', 'data'),
    Input('search-dropdown', 'value')
)
def update_table(team_name):
    if not team_name:
        return []

    team = next(t for t in data if t['Equipe'] == team_name)

    epreuves = team['Epreuves_part']

    return [{
        'Membres': ", ".join(team['Membres']),
        'QueteCles': ", ".join(epreuves.get('Quête des clés', [])),
        'Jugement': ", ".join(epreuves.get('Salle du Jugement', [])),
        'Indices': ", ".join(epreuves.get('Quête des indices', [])),
        'Conseil': ", ".join(epreuves.get('Salle du Conseil', [])),
        'Reussites': team['Reussites'].count('Reussite'),
        'Echecs': team['Reussites'].count('Echec'),
        'Gains': team['Gains'],
        'Temps': team['Temps']
    }]

@app.callback(
    Output('team-image', 'src'),
    Input('search-dropdown', 'value')
)
def update_image(team_name):
    print(team_name)
    if not team_name:
        return None
    return f"/static/images/{team_name}.jpg"

# -------------------------------- Run --------------------------------

def create_dashboard():
    return app