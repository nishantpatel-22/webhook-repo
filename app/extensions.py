from pymongo import MongoClient

# Use your actual connection string here
client = MongoClient("mongodb+srv://np26112003_db_user:9jgHMqtf28Kht42K@cluster0.hrjoqju.mongodb.net/?appName=Cluster0")
db = client['webhook_db']