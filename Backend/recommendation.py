from flask import Blueprint, request, jsonify
from uuid import uuid4
from datetime import datetime

recommendation_bp = Blueprint('recommendation', __name__)

# Simpan data rekomendasi (sementara dalam memori)
recommendations = []

def validate_recommendation(data):
    """Validasi data rekomendasi."""
    required_fields = ['username', 'chat_session', 'activity', 'duration', 'date']
    for field in required_fields:
        if field not in data or not data[field]:
            return f"Field '{field}' is required and cannot be empty."
    try:
        datetime.strptime(data['date'], '%Y-%m-%d')  # Validasi format tanggal
    except ValueError:
        return "Field 'date' must be in format YYYY-MM-DD."
    return None

@recommendation_bp.route('/recommendation', methods=['POST'])
def add_recommendation():
    data = request.json
    # Validasi input
    error = validate_recommendation(data)
    if error:
        return jsonify({"error": error}), 400

    new_recommendation = {
        "id": str(uuid4()),  # Gunakan UUID untuk ID unik
        "username": data['username'],
        "chat_session": data['chat_session'],
        "activity": data['activity'],
        "duration": data['duration'],
        "date": data['date'],
        "approval": data.get('approval', 'no')  # Default 'no' jika tidak ada
    }
    recommendations.append(new_recommendation)
    return jsonify(new_recommendation), 201

@recommendation_bp.route('/recommendation/<string:rec_id>', methods=['PUT'])
def edit_approval(rec_id):
    data = request.json
    username = data.get('username')
    approval = data.get('approval')

    # Validasi input
    if not username or approval not in ['yes', 'no']:
        return jsonify({"error": "Invalid input. 'username' and valid 'approval' are required."}), 400

    for rec in recommendations:
        if rec['id'] == rec_id and rec['username'] == username:
            rec['approval'] = approval
            return jsonify(rec), 200

    return jsonify({"error": "Recommendation not found or username mismatch."}), 404

@recommendation_bp.route('/recommendations/<username>', methods=['GET'])
def get_user_recommendations(username):
    user_recommendations = [rec for rec in recommendations if rec['username'] == username]
    if not user_recommendations:
        return jsonify({"message": "No recommendations found for this user."}), 404
    return jsonify(user_recommendations), 200
