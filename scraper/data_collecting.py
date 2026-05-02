import requests, re, unidecode, os, gridfs
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pymongo import MongoClient

# ------------------------------
# Configuration
# ------------------------------
BASE_URL = "https://o.fortboyard.tv/gains.php"
SAVE_FOLDER = "/app/images"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# ------------------------------
# Connexion MongoDB
# ------------------------------
client = MongoClient(MONGO_URI)
db = client["scraping_db"]
collection = db["equipes"]

# ------------------------------
# Fonctions utilitaires
# ------------------------------

def isFiveLastYears(equipe_year):
    """Filtrer les équipes des 20 dernières années"""
    match = re.search(r'\((\d{4})\)', equipe_year)
    annee_actuelle = datetime.now().year
    return match and int(match.group(1)) > annee_actuelle - 5


def get_soup(url):
    """Télécharge une page et renvoie un objet BeautifulSoup"""
    res = requests.get(url)
    res.raise_for_status()
    return BeautifulSoup(res.text, 'html.parser')


def scrape_images(style_str, equipe_name):
    """Récupère et sauvegarde une image à partir de l'attribut style"""
    if not os.path.exists(SAVE_FOLDER):
        os.makedirs(SAVE_FOLDER)

    match = re.search(r"url\('(.*?)'\)", style_str)
    if not match:
        return None
    img_url = match.group(1)

    try:
        img_binary_data = requests.get(img_url)
        img_path = os.path.join(SAVE_FOLDER, f"{unidecode.unidecode(equipe_name)}.jpg")
        with open(img_path, "wb") as f:
            f.write(img_binary_data.content)
    except Exception as e:
        print(f"⚠️ Erreur téléchargement image pour {equipe_name}: {e}")
        return None

    return img_binary_data


# ------------------------------
# Scraping des sous-pages
# ------------------------------

def scrape_subpage(url, equipe):
    """Scrape les infos d'une équipe"""
    soup = get_soup(url)
    fs = gridfs.GridFS(db)
    
    # ---- Image ----
    img_div = soup.select_one('.imgEquipe')
    img_binary_data = scrape_images(img_div['style'], equipe)
    image_data = fs.put(
    img_binary_data.content,
    filename="image.jpg",
    content_type="image/jpeg"
)

    # ---- Membres ----
    membres = [unidecode.unidecode(a.text.strip()) for a in soup.select('td[style="text-align: center;"] a')]

    # ---- Epreuves ----
    def extract_epreuves(section_title, bloc_classes):
        epreuves = []
        # Trouver le <h2> correspondant
        for h2 in soup.find_all("h2", class_="titrePartie"):
            if h2.get_text(strip=True) == section_title:
                # Trouver les <div> qui suivent (siblings)
                next_divs = h2.find_next_siblings("div")
                for bloc in next_divs:
                    for class_name in bloc_classes:
                        resumes = bloc.find_all("div", class_=class_name)
                        for resume in resumes:
                            nom = resume.find("div", class_="nomEpreuve")
                            if nom and nom.a:
                                epreuves.append(nom.a.get_text(strip=True))
                break  # On sort après la première correspondance
        return epreuves

    epreuves = {
        "Quête des clés": extract_epreuves("Quête des clés", ["resumeBloc2 type_epreuves"]),
        "Salle du Jugement": extract_epreuves("Salle du Jugement", ["resumeBloc2 type_cage", "resumeBloc2 type_jeux_blanche"]),
        "Quête des indices": extract_epreuves("Quête des indices", ["resumeBloc2 type_aventures"]),
        "Salle du Conseil": extract_epreuves("Salle du Conseil",  ["resumeBloc2 type_defis"]),
    }

    # ---- Réussites ----
    reussites = [unidecode.unidecode(span.text.strip()) for span in soup.select('.statut span')]

    # ---- Gains ----
    gains = ""
    gains_h2 = soup.find('h2', style="font-size: 2.8em;")
    if gains_h2:
        gains = gains_h2.text.strip()
    else:
        li_elements = soup.select('.blocSDTGain2 ul li')
        gains = "".join(li.text if li.text != "O" else "0" for li in li_elements)
    gains = gains.replace(" €", "").replace("\u0080", "")

    # ---- Temps ----
    temps = []
    for t in soup.find('div', class_='sdt_temps'):
        try:
            temps.append(int(t.text.strip()))
        except:
            pass

    # ---- Résultat final ----
    return {
        "Equipe": unidecode.unidecode(equipe),
        "Image": image_data,
        "Membres": membres,
        "Epreuves_part": epreuves,
        "Reussites": reussites,
        "Gains": gains,
        "Temps": temps,
    }


# ------------------------------
# Scraping principal
# ------------------------------

def scrape_main():
    """Scrape la page principale puis les sous-pages d’équipes"""
    soup = get_soup(BASE_URL)

    # Trouver le lien vers la liste des équipes
    link_el = soup.select_one('#corps_index_gauche div:nth-of-type(2) ul li:nth-of-type(2) a')
    if not link_el:
        print("❌ Lien vers la liste des équipes introuvable.")
        return

    link_url = urljoin(BASE_URL, link_el['href'])
    soup_equipes = get_soup(link_url)

    # Trouver les liens d’équipes
    equipe_links = soup_equipes.select('.TableGains tr td:nth-of-type(2) a')
    equipes = [(a.text.strip(), urljoin(link_url, a['href'])) for a in equipe_links if a.text.strip()]

    # Filtrer les années
    equipes = [(e, l) for e, l in equipes if isFiveLastYears(e)]

    print(f"🔎 {len(equipes)} équipes trouvées pour les 5 dernières années.\n")

    for equipe, lien in equipes:
        print(f"➡️  Scraping de {equipe}...")
        data = scrape_subpage(lien + "#Resume", equipe)

        # --- Vérifier si déjà présent ---
        if collection.find_one({"Equipe": data["Equipe"]}):
            print(f"⚙️  Équipe {data['Equipe']} déjà présente en base, sautée.")
            continue

        # --- Insérer dans MongoDB ---
        collection.insert_one(data)
        print(f"✅  {data['Equipe']} ajoutée avec succès.\n")

    print("🎉 Scraping complet terminé.")
    open("/shared/data_ready", "w").close()


# ------------------------------
# Point d’entrée
# ------------------------------

if __name__ == "__main__":
    scrape_main()
