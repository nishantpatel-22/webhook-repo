from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import pytz

def create_app():
    app = Flask(__name__)

    # My MongoDB Connection string
    MONGO_URI = "mongodb+srv://np26112003_db_user:9jgHMqtf28Kht42K@cluster0.hrjoqju.mongodb.net/?appName=Cluster0"

    # Setting up the DB
    client = MongoClient(MONGO_URI)
    db = client['webhook_db']
    collection = db['events']

    @app.route('/')
    def home():
        return render_template('index.html')

    # IMPORTANT: Company reference says use /webhook/receiver
    @app.route('/webhook/receiver', methods=['POST'])
    def receive_github_data():
        data = request.json
        event_type = request.headers.get('X-GitHub-Event')
        
        now = datetime.now(pytz.utc)
        timestamp = now.strftime("%d %B %Y - %I:%M %p UTC")
        
        print(f"--- Received a {event_type} event! ---")

        payload = {
            "author": "Guest",
            "from_branch": "none",
            "to_branch": "none",
            "timestamp": timestamp,
            "action": "",
            "request_id": ""
        }

        if event_type == 'push':
            payload["action"] = "PUSH"
            payload["author"] = data['pusher']['name']
            payload["to_branch"] = data['ref'].split('/')[-1]
            payload["request_id"] = data['head_commit']['id']
            print(f"User {payload['author']} just pushed to {payload['to_branch']}")

        elif event_type == 'pull_request':
            if data['action'] == 'closed' and data['pull_request']['merged']:
                payload["action"] = "MERGE"
            else:
                payload["action"] = "PULL_REQUEST"
                
            payload["author"] = data['pull_request']['user']['login']
            payload["from_branch"] = data['pull_request']['head']['ref']
            payload["to_branch"] = data['pull_request']['base']['ref']
            payload["request_id"] = str(data['pull_request']['id'])

        # Saving to MongoDB
        collection.insert_one(payload)
        print("Successfully saved to MongoDB!")
        
        return jsonify({"status": "received"}), 200

    @app.route('/api/events')
    def send_data_to_ui():
        all_events = list(collection.find({}, {'_id': 0}).sort('_id', -1))
        return jsonify(all_events)

    return app