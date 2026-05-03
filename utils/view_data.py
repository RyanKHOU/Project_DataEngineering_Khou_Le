from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["scraping_db"]
collection = db["equipes"]

for doc in collection.find():
    print(doc)

collections = db.list_collection_names()
print("Collections dans la base :", collections)
