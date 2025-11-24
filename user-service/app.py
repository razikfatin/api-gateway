from flask import Flask, jsonify, request, abort
import os

app = Flask(__name__)

USERS = {
    1: {"id": 1, "name": "Razik"},
    2: {"id": 2, "name": "Tushar"}
}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/users', methods=['GET'])
def list_users():
    return jsonify(list(USERS.values()))

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = USERS.get(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify(user)

@app.route('/users', methods=['POST'])
def create_user():
    payload = request.json or {}
    name = payload.get('name')
    if not name:
        return jsonify({"error": "name required"}), 400
    new_id = max(USERS.keys()) + 1 if USERS else 1
    user = {"id": new_id, "name": name}
    USERS[new_id] = user
    return jsonify(user), 201

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)