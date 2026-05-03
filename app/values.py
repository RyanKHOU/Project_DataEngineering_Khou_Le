import os, pymongo, json, pandas as pd
from bson import json_util
import plotly.express as px
import plotly.graph_objs as go

# Connexion à MongoDB (ajustez l'URI si nécessaire)
client = pymongo.MongoClient("mongodb://mongodb:27017/")

# Sélectionner la base de données
db_name = "scraping_db"
db = client[db_name]

# Récupérer toutes les collections de la base de données
collection = db["equipes"]

# Créer un dictionnaire pour stocker toutes les données
data = json.loads(json_util.dumps((collection.find())))

# Initialisation des variables pour les graphiques
equipes = [team['Equipe'] for team in data]
gains = [int(team['Gains'].replace(" ", "")) for team in data]

# Création du graphique des gains
equipes_gains_sorted, gains_sorted = zip(*sorted(zip(equipes, gains), key=lambda x: x[1]))

# Création du DataFrame
df_gains = pd.DataFrame({
    "Equipe": equipes_gains_sorted,
    "Gains": gains_sorted
})

# Création du graphique
fig_gains = px.bar(
    df_gains,
    x="Equipe",
    y="Gains",
    labels={
        "Equipe": "Équipes",
        "Gains": "Gains"
    },
    title="Histogramme des Gains par Équipe"
)
# Calcul des réussites et échecs 
reussites = []
echecs = []
for team in data:
    if 'Reussites' in team: 
        toutes_reussites = team['Reussites'].count("Reussite")
        tous_echecs = team['Reussites'].count("Echec")
    else:
        toutes_reussites = 0
        tous_echecs = 0
    reussites.append(toutes_reussites)
    echecs.append(tous_echecs)

# Création Histogramme
fig_reussites_echecs = go.Figure(data=[
    go.Bar(name='Réussites', x=equipes, y=reussites),
    go.Bar(name='Échecs', x=equipes, y=echecs)
])
fig_reussites_echecs.update_layout(barmode='group', title='Réussites et Échecs par Équipe')

# Graph Moy Réussite ---------------------------------------------------
data_triage = data.copy()

# Triez la nouvelle variable par ordre croissant de réussite moyenne
data_triage.sort(key=lambda team: team['Reussites'].count("Reussite") / len(team['Reussites']) if team['Reussites'] else 0)


# Création Histogramme
# Supposons que chaque élément dans 'Reussites' est une chaîne de caractères ("Reussite" ou "Echec")
fig_avg_successes = px.bar(
    x=[team['Equipe'] for team in data_triage],
    y=[team['Reussites'].count("Reussite") / len(team['Reussites']) if team['Reussites'] else 0 for team in data_triage],
    labels={'x': 'Équipe', 'y': 'Nombre Moyen de Réussites'},
    title='Nombre Moyen de Réussites par Équipe'
)


# Graph Temps ---------------------------------------------------
# Fonction minute en seconde
def time_to_seconds(time_value):
    if isinstance(time_value, str):
        # Si c'est une chaîne, la diviser et convertir en secondes
        parts = time_value.split(':')
        return int(parts[0]) * 60 + int(parts[1])
    elif isinstance(time_value, list) and len(time_value) == 2:
        # Si c'est une liste avec deux éléments, les convertir en entiers et calculer les secondes
        return int(time_value[0]) * 60 + int(time_value[1])
    else:
        # Gérer autrement les cas non prévus
        return 0

times = [time_to_seconds(team['Temps']) for team in data]

# Tri ordre décroissant
equipe_time_sorted, times_sorted = zip(*sorted(zip(equipes, times), key=lambda x: x[1]))

# Création Histogramme
fig_time = px.bar(x=equipe_time_sorted, y=times_sorted, labels={'x': 'Équipes', 'y': 'Temps Total (seconde)'},
                  title="Temps Total (en seconde) par Équipe dans l'épreuve final")



