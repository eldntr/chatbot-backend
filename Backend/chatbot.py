from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import uuid

chatbot_bp = Blueprint('chatbot', __name__)

# MongoDB setup
client = MongoClient('mongo', 27017)  # 'mongo' is the service name in docker-compose.yml
db = client['chat_db']
sessions_collection = db['sessions']

@chatbot_bp.route('/create_session', methods=['POST'])
def create_session():
    session_id = str(uuid.uuid4())
    session_data = {'session_id': session_id, 'conversation': ""}
    sessions_collection.insert_one(session_data)
    return jsonify({'session_id': session_id}), 201

@chatbot_bp.route('/chat/<session_id>', methods=['POST'])
def chat(session_id):
    user_input = request.json.get('message')
    
    session_data = sessions_collection.find_one({'session_id': session_id})
    if not session_data:
        return jsonify({'message': 'Session not found'}), 404
    
    session_data['conversation'] += f"User: {user_input}\n"
    bot_response = "ini response dari bot"
    session_data['conversation'] += f"Bot: {bot_response}\n"
    
    sessions_collection.update_one({'session_id': session_id}, {'$set': session_data}, upsert=True)
    
    return jsonify({'response': bot_response})

@chatbot_bp.route('/history/<session_id>', methods=['GET'])
def history(session_id):
    session_data = sessions_collection.find_one({'session_id': session_id})
    if not session_data:
        return jsonify({'conversation': ''}), 404
    
    return jsonify({'conversation': session_data['conversation']}), 200

@chatbot_bp.route('/delete/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    result = sessions_collection.delete_one({'session_id': session_id})
    if result.deleted_count == 0:
        return jsonify({'message': 'Session not found'}), 404
    return jsonify({'message': 'Session deleted'}), 200

@chatbot_bp.route('/search_sessions', methods=['GET'])
def search_sessions():
    user_id = request.args.get('user_id')
    sessions = sessions_collection.find({'conversation': {'$regex': f"User: {user_id}"}})
    session_ids = [session['session_id'] for session in sessions]
    
    if not session_ids:
        return jsonify({'message': 'No sessions found for this user'}), 404
    
    return jsonify({'session_ids': session_ids}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')