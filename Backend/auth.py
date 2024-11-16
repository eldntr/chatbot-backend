
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

# Koneksi ke MongoDB
client = MongoClient('mongo', 27017)  # 'mongo' adalah nama layanan di docker-compose.yml
db = client['chat_db']
users_collection = db['users']

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if users_collection.find_one({'username': username}):
        return jsonify({'status': 'User already exists'}), 400
    
    hashed_password = generate_password_hash(password)
    users_collection.insert_one({'username': username, 'password': hashed_password})
    return jsonify({'status': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = users_collection.find_one({'username': username})
    if user and check_password_hash(user['password'], password):
        return jsonify({'status': 'Login successful'}), 200
    return jsonify({'status': 'Invalid username or password'}), 401