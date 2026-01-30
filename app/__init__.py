from flask import Flask, request, jsonify, render_template
from .extensions import db  # Matches your filename 'extensions.py'
from datetime import datetime, timezone

def create_app():
    app = Flask(__name__)
    collection = db.actions

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/webhook', methods=['POST'])
    def webhook():
        data = request.json
        event_type = request.headers.get('X-GitHub-Event')
        
        # Format: 1st April 2021 - 9:30 PM UTC [cite: 9, 27]
        timestamp = datetime.now(timezone.utc).strftime("%d %B %Y - %I:%M %p UTC")
        action_data = None

        # 1. Handle PUSH [cite: 7, 8]
        if event_type == "push":
            action_data = {
                "request_id": data.get('after'), 
                "author": data.get('pusher', {}).get('name'),
                "action": "PUSH",
                "from_branch": data.get('ref', '').split('/')[-1],
                "to_branch": data.get('ref', '').split('/')[-1],
                "timestamp": timestamp
            }

        # 2. Handle PULL_REQUEST [cite: 10, 11] & MERGE [cite: 13, 14]
        elif event_type == "pull_request":
            pr_info = data.get('pull_request', {})
            is_merged = pr_info.get('merged', False)
            action_type = "MERGE" if is_merged else "PULL_REQUEST"
            
            action_data = {
                "request_id": str(pr_info.get('number')), 
                "author": pr_info.get('user', {}).get('login'),
                "action": action_type,
                "from_branch": pr_info.get('head', {}).get('ref'),
                "to_branch": pr_info.get('base', {}).get('ref'),
                "timestamp": timestamp
            }

        if action_data:
            collection.insert_one(action_data) [cite: 5, 24]
            return jsonify({"status": "stored"}), 200

        return jsonify({"status": "ignored"}), 200

    # API for the UI to poll every 15 seconds [cite: 6, 39]
    @app.route('/api/actions', methods=['GET'])
    def get_actions():
        actions = list(collection.find({}, {'_id': 0}).sort('_id', -1).limit(10))
        return jsonify(actions)

    return app