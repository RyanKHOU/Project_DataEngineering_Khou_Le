from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["scraping_db"]
collection = db["equipes"]


# Vider la collection (supprime tous les documents)
collection.delete_many({})