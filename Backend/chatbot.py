from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import uuid
from datetime import datetime
from recommendation import recommendations
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

chatbot_bp = Blueprint('chatbot', __name__)

# MongoDB setup
client = MongoClient('mongo', 27017)  # 'mongo' is the service name in docker-compose.yml
db = client['chat_db']
sessions_collection = db['sessions']

OPENROUTER_API_KEY = 'OPEN-ROUTER-KEY'
YOUR_SITE_URL = 'http://example.com'
YOUR_APP_NAME = 'ChatbotApp'

def get_bot_response(user_input, conversation_history, language="en"):
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for message in conversation_history:
        role = message['role'].lower()
        if role == 'bot':
            role = 'assistant'
        messages.append({"role": role, "content": message['message']})
    messages.append({"role": "user", "content": user_input})
    
    logging.debug(f"Sending messages to API: {messages}")
    
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": f"{YOUR_SITE_URL}",
            "X-Title": f"{YOUR_APP_NAME}",
        },
        data=json.dumps({
            "model": "openai/gpt-3.5-turbo",
            "messages": messages,
            "language": language
        })
    )
    response_data = response.json()
    logging.debug(f"API response: {response_data}")
    if 'choices' in response_data and response_data['choices']:
        return response_data['choices'][0]['message']['content']
    else:
        return "Maaf, saya tidak bisa memproses permintaan Anda."

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
        'timestamp': datetime.utcnow().isoformat(),
    })
    
    bot_response = get_bot_response(user_input, session_data['conversation'])
    
    session_data['conversation'].append({
        'role': 'Bot',
        'message': bot_response,
        'timestamp': datetime.utcnow().isoformat()
    })
    
    # Generate a conclusion based on the conversation in Indonesian
    conclusion = get_bot_response("Ringkas percakapan ini", session_data['conversation'], language="id")
    session_data['conclusion'] = conclusion
    
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
    
    return jsonify({'response': bot_response, 'conclusion': conclusion})

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

@chatbot_bp.route('/edit_conclusion/<session_id>', methods=['PUT'])
def edit_conclusion(session_id):
    new_conclusion = request.json.get('conclusion')
    
    result = sessions_collection.update_one(
        {'session_id': session_id},
        {'$set': {'conclusion': new_conclusion}}
    )
    
    if result.matched_count == 0:
        return jsonify({'message': 'Session not found'}), 404
    
    return jsonify({'message': 'Conclusion updated successfully'}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
