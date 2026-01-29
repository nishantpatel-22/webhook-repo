from flask import Blueprint, request, jsonify, render_template
from app.extensions import db
from datetime import datetime
import pytz

# The url_prefix='/webhook' means the receiver is at /webhook/receiver
webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=['POST'])
def receiver():
    collection = db['events']
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    
    now = datetime.now(pytz.utc)
    timestamp = now.strftime("%d %B %Y - %I:%M %p UTC")

    payload = {
        "author": "Guest",
        "from_branch": "",
        "to_branch": "",
        "timestamp": timestamp,
        "action": "",
        "request_id": ""
    }

    if event_type == 'push':
        payload["action"] = "PUSH"
        payload["author"] = data['pusher']['name']
        payload["to_branch"] = data['ref'].split('/')[-1]
        payload["request_id"] = data['head_commit']['id']

    elif event_type == 'pull_request':
        # Check if it's a merge or just a PR
        if data.get('action') == 'closed' and data['pull_request'].get('merged'):
            payload["action"] = "MERGE"
        else:
            payload["action"] = "PULL_REQUEST"
            
        payload["author"] = data['pull_request']['user']['login']
        payload["from_branch"] = data['pull_request']['head']['ref']
        payload["to_branch"] = data['pull_request']['base']['ref']
        payload["request_id"] = str(data['pull_request']['id'])

    collection.insert_one(payload)
    return jsonify({"status": "success"}), 200

# Route to serve the HTML dashboard
@webhook.route('/')
def index():
    return render_template('index.html')

# Route to provide data to the dashboard
@webhook.route('/events', methods=['GET'])
def get_events():
    collection = db['events']
    # Fetch latest 10 events
    events = list(collection.find({}, {'_id': 0}).sort('_id', -1).limit(10))
    return jsonify(events)