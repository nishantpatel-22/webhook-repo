from flask import Flask, request, jsonify, render_template
from .extensions import db 
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
        if not data:
            return jsonify({"status": "no data"}), 400

        event_type = request.headers.get('X-GitHub-Event')
        
        # Current time in UTC as per requirements
        timestamp = datetime.now(timezone.utc).strftime("%d %B %Y - %I:%M %p UTC")
        action_data = None

        # 1. Handle PUSH
        if event_type == "push":
            action_data = {
                "request_id": data.get('after'), 
                "author": data.get('pusher', {}).get('name'),
                "action": "PUSH",
                "from_branch": data.get('ref', '').split('/')[-1],
                "to_branch": data.get('ref', '').split('/')[-1],
                "timestamp": timestamp
            }

        # 2. Handle PULL_REQUEST & MERGE (Brownie Points logic)
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

        # Store to MongoDB if valid action found
        if action_data:
            collection.insert_one(action_data)
            return jsonify({"status": "stored"}), 200

        return jsonify({"status": "ignored"}), 200

    @app.route('/api/actions', methods=['GET'])
    def get_actions():
        # Retrieves the 10 most recent actions
        actions = list(collection.find({}, {'_id': 0}).sort('_id', -1).limit(10))
        return jsonify(actions)

    return app