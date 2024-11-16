from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import uuid
from datetime import datetime
from recommendation import recommendations

chatbot_bp = Blueprint('chatbot', __name__)

# MongoDB setup
client = MongoClient('mongo', 27017)  # 'mongo' is the service name in docker-compose.yml
db = client['chat_db']
sessions_collection = db['sessions']

@chatbot_bp.route('/create_session', methods=['POST'])
def create_session():
    session_id = str(uuid.uuid4())
    session_data = {'session_id': session_id, 'conversation': [], 'conclusion': None}
    sessions_collection.insert_one(session_data)
    return jsonify({'session_id': session_id}), 201

@chatbot_bp.route('/chat/<session_id>', methods=['POST'])
def chat(session_id):
    user_input = request.json.get('message')
    username = request.json.get('username')
    
    session_data = sessions_collection.find_one({'session_id': session_id})
    if not session_data:
        return jsonify({'message': 'Session not found'}), 404
    
    session_data['conversation'].append({
        'role': 'User',
        'message': user_input,
        'timestamp': datetime.utcnow().isoformat()
    })
    bot_response = "ini response dari bot"
    session_data['conversation'].append({
        'role': 'Bot',
        'message': bot_response,
        'timestamp': datetime.utcnow().isoformat()
    })
    
    # Include recommendations at the end of the chat session
    if user_input.lower() == "end":
        session_data['conversation'].append({
            'role': 'Bot',
            'message': 'Here are some recommendations:',
            'timestamp': datetime.utcnow().isoformat()
        })
        for rec in recommendations:
            if rec['username'] == username and rec['chat_session'] == session_id:
                session_data['conversation'].append({
                    'role': 'Bot',
                    'message': f"Activity: {rec['activity']}, Duration: {rec['duration']}, Date: {rec['date']}, Approval: {rec['approval']}",
                    'timestamp': datetime.utcnow().isoformat()
                })
    
    sessions_collection.update_one({'session_id': session_id}, {'$set': session_data}, upsert=True)
    
    return jsonify({'response': bot_response})

@chatbot_bp.route('/history/<session_id>', methods=['GET'])
def history(session_id):
    session_data = sessions_collection.find_one({'session_id': session_id})
    if not session_data:
        return jsonify({'conversation': ''}), 404
    
    return jsonify({'conversation': session_data['conversation'], 'conclusion': session_data['conclusion']}), 200

@chatbot_bp.route('/delete/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    result = sessions_collection.delete_one({'session_id': session_id})
    if result.deleted_count == 0:
        return jsonify({'message': 'Session not found'}), 404
    return jsonify({'message': 'Session deleted'}), 200

@chatbot_bp.route('/search_sessions', methods=['GET'])
def search_sessions():
    user_id = request.args.get('user_id')
    sessions = sessions_collection.find({'conversation.role': 'User', 'conversation.message': {'$regex': user_id}})
    session_ids = [session['session_id'] for session in sessions]
    
    if not session_ids:
        return jsonify({'message': 'No sessions found for this user'}), 404
    
    return jsonify({'session_ids': session_ids}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')