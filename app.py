from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import pytz

app = Flask(__name__)

# My MongoDB Connection string
MONGO_URI = "mongodb+srv://np26112003_db_user:9jgHMqtf28Kht42K@cluster0.hrjoqju.mongodb.net/?appName=Cluster0"

# Setting up the DB
client = MongoClient(MONGO_URI)
db = client['webhook_db']
collection = db['events']

@app.route('/')
def home():
    print("Someone just visited my website!")
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def receive_github_data():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    
    # Custom timestamp for the assignment
    now = datetime.now(pytz.utc)
    # Formatting it exactly: 1st April 2021 - 9:30 PM UTC
    timestamp = now.strftime("%d %B %Y - %I:%M %p UTC")
    
    # Printing for my own testing
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
            print("Action was a Merge!")
        else:
            payload["action"] = "PULL_REQUEST"
            print("Action was a Pull Request!")
            
        payload["author"] = data['pull_request']['user']['login']
        payload["from_branch"] = data['pull_request']['head']['ref']
        payload["to_branch"] = data['pull_request']['base']['ref']
        payload["request_id"] = str(data['pull_request']['id'])

    # Saving to my Atlas DB
    collection.insert_one(payload)
    print("Successfully saved to MongoDB!")
    
    return "OK", 200

@app.route('/api/events')
def send_data_to_ui():
    # Fetching all events from DB
    all_events = list(collection.find({}, {'_id': 0}).sort('_id', -1))
    return jsonify(all_events)

if __name__ == '__main__':
    print("Starting my Flask server on port 5000...")
    app.run(port=5000, debug=True)