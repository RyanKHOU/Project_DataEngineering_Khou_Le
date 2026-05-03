#!/bin/sh
set -e

echo "Waiting for MongoDB scraping to finish..."

until python - <<EOF
from pymongo import MongoClient
import sys

try:
    client = MongoClient("mongodb", 27017, serverSelectionTimeoutMS=2000)
    db = client.scraping_db
    doc = db.job_status.find_one(
        {"_id": "scraping", "finished": True}
    )
    sys.exit(0 if doc else 1)
except Exception:
    sys.exit(1)
EOF
do
  sleep 5
done

echo "Scraping finished, starting app"
exec python main.py
