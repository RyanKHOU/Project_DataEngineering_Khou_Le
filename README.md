# DataEngineering Projet étude des performances des équipes ayant participé à Fort Boyard de 2003 à 2023
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white)
![Dash](https://img.shields.io/badge/dash-008DE4?style=for-the-badge&logo=dash&logoColor=white)


## Description
L'objectif de ce projet est d'étudier les performances des équipes participant à la mythique émission TV Fort Boyard, sous la forme d'une application complète conçue pour collecter, traiter et visualiser des données sur un format type dashboard.

Pour cela nous récupérons les informations par webScraping depuis le site [https://o.fortboyard.tv/gains.php#parsaison](https://o.fortboyard.tv/gains.php#parsaison).


## Stack technique
* Frontend: Dash, Plotly
* Backend: Python
* Base de données : MongoDB
* Web scraping: BeautifulSoup, Requests
* Utilitaires : PyMongo, GridFS
* Déploiement : Docker, Docker Compose


## Pré-requis
Ce projet nécessite l'utilisation de Docker. S'il n'est pas déjà téléchargé :

* [Pour Windows](https://docs.docker.com/desktop/install/windows-install/)

* [Pour Linux](https://docs.docker.com/desktop/install/linux-install/)

* [Pour Mac](https://docs.docker.com/desktop/install/mac-install/)


## Guide d'installation
Dans un terminal de commandes, commencez par vous déplacer vers le dossier où sera enregistré le projet avec la commande :

``
cd chemin_vers_le_dossier_de_votre_choix
``

Cloner le projet avec la commande:

``
git clone https://github.com/RyanKHOU/Project_DataEngineering_Khou_Le.git
``

Créer les containers et les images du projet avec la commande (à la racine du projet)

``
docker-compose build 
``

Lancer  l'exécution du projet avec la commande 

``
docker-compose up -d
``

Ensuite il faut attendre que le container dash_app soit actif. Quand c'est le cas il suffit de se rendre sur l'adresse IP https://127.0.0.1:8050.

## Guide d'utilisation
### Structure du projet

```markdown
app/
|---- static
        |---- images
        |---- main.css
|---- Dockerfile_dash_app
|---- main.py
|---- requirements.txt
|---- values.py
|---- visualization.py
|---- wait-for-scrape.sh
scraper/
|---- data_collecting.py
|---- Dockerfile
|---- requirements.txt
utils/
|---- delete_data.py
|---- view_data.py
docker-compose.yml
README.md
```

### Programmes python

* __scraper/data_collecting.py__ : scrape les données depuis le site [https://o.fortboyard.tv/gains.php#parsaison](https://o.fortboyard.tv/gains.php#parsaison) et génère un fichier json contenant toutes les informations récupérées.

* __app/values.py__ : récupère l'ensemble des données depuis le container dont l'image est une base de données mongodb. Ce fichier de code contient également les fonctions essentielles pour faire un premier traitement des données comme la fonction *time_to_seconds()* ou pour déclarer des histogrammes avec la variable *fig_time*.

* __app/visualization.py__ : interface permettant d'implémenter le framework de l'application via des fonctions implémentant les graphiques, les boutons, les sliders, l'affichage des images et leurs interactions.

* __app/main.py__ : permet de démarrer le dashboard en appelant la variable *app* implémentées dans **visualization.py** contenant toute l'architecture du dashboard.

#### Remarque

__wait-for-scrape.sh__ : Le dashboard ne s’affiche qu’une fois le scraping du site web terminé. Ce script sert donc à vérifier l’état d’avancement du scraping en envoyant des requêtes au service Docker chargé de l’exécuter.


### docker-compose

Le fichier docker-compose.yml créé 3 services : 

- **mongodb** : il permet de stocker les données dans une base de données. Il s'appuie sur une image mongo qui utilise par défaut le port 27017.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Pour plus d'informations :

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Dépôt docker de l'image](https://hub.docker.com/_/mongo)

- **scraper** : collecte des données et stockage dans MongoDB. Par ailleurs, le dossier avec les photos des équipes est créé en local pour que le développeur ait une trace des dernières images scrapées et pour faciliter le développement de nouvelles features liées aux images si besoin.


- **dash_app** : il permet d'afficher à l'écran le dashboard. Etant donné qu'il utilise un framework dash, le dashboard est accessible via le port 8050.

### Volumes
* mongo_data : volume dédié à la persistance des données MongoDB.
* tmp_data : volume partagé entre le scraper et l’application Dash pour que le script **wait-for-scrape.sh** puisse notifier le dashboard de la fin du scraping.

### utils
Ce répertoire contient quelques fonctions pratiques lors du développement pour voir le contenu de la base de données ou la supprimer entièrement. Pour les lancer, il suffit d'ouvrir un nouveau terminal à la racine du projet et de faire ``python [script_à_utiliser]``.


## Contribution

Pour contribuer au projet, veuillez suivre les étapes suivantes :

1. Forkez le dépôt avec `git fork`
2. Créez une nouvelle branche avec `git branch`
3. Apportez vos modifications et validez-les avec `git commit`
4. Poussez les modifications vers le dépôt distant avec `git push`
5. Créez une pull request via l’interface GitHub

## Licence

Ce projet est sous licence MIT.

## Contact

Pour toute question ou demande, veuillez nous contacter à van-minhchristophe.le@edu.esiee.fr ou à ryan.khou@edu.esiee.fr.


## Contributeurs

Ce projet a été développé par Van-Minh Christophe LE (étudiant 4e année filière DSIA) et Ryan KHOU (étudiant 4e année filière DSIA) dans le cadre de l'unité Data Engineering dispensé à l'ESIEE PARIS.
