import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# We pull the URI from the .env file for security
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client['webhook_db']