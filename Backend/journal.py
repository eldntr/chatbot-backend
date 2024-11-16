from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId  # Add this import for ObjectId usage

journal_bp = Blueprint('journal', __name__)

# Koneksi ke MongoDB
client = MongoClient('mongo', 27017)  # 'mongo' adalah nama layanan di docker-compose.yml
db = client['chat_db']
journal_collection = db['journal']

@journal_bp.route('/', methods=['POST'])
def create_journal_entry():
    data = request.json
    username = data.get('username')
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Check if an entry already exists for today
    existing_entry = journal_collection.find_one({
        'username': username,
        'date': {'$regex': f'^{today}'}
    })
    
    if existing_entry:
        return jsonify({'status': 'Journal entry already exists for today'}), 400
    
    entry = {
        'username': username,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'content': data.get('content')
    }
    result = journal_collection.insert_one(entry)
    entry['_id'] = str(result.inserted_id)  # Add the _id to the entry
    return jsonify(entry), 201

@journal_bp.route('/<username>', methods=['GET'])
def get_journal_entries(username):
    entries = list(journal_collection.find({'username': username}, {'_id': 1, 'username': 1, 'date': 1, 'content': 1}))  # Include _id in the projection
    for entry in entries:
        entry['_id'] = str(entry['_id'])  # Convert ObjectId to string
    return jsonify(entries), 200

@journal_bp.route('/<username>/<entry_id>', methods=['PUT'])
def update_journal_entry(username, entry_id):
    data = request.json
    journal_collection.update_one(
        {'username': username, '_id': ObjectId(entry_id)},  # Ensure ObjectId is used
        {'$set': {'content': data.get('content'), 'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}
    )
    return jsonify({'status': 'Journal entry updated'}), 200

@journal_bp.route('/<username>/<entry_id>', methods=['DELETE'])
def delete_journal_entry(username, entry_id):
    journal_collection.delete_one({'username': username, '_id': ObjectId(entry_id)})  # Ensure ObjectId is used
    return jsonify({'status': 'Journal entry deleted'}), 200