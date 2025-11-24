from flask import Flask, jsonify, request
import os
import requests

app = Flask(__name__)

# Simple in-memory orders DB
ORDERS = {}
NEXT_ID = 1

USER_SERVICE_HOST = os.environ.get('USER_SERVICE_HOST', 'user-service')
USER_SERVICE_PORT = int(os.environ.get('USER_SERVICE_PORT', 5000))

def user_exists(user_id: int) -> bool:
    url = f'http://{USER_SERVICE_HOST}:{USER_SERVICE_PORT}/users/{user_id}'
    try:
        r = requests.get(url, timeout=2)
        return r.status_code == 200
    except requests.RequestException:
        return False

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/orders', methods=['POST'])
def create_order():
    global NEXT_ID
    payload = request.json or {}
    user_id = payload.get('user_id')
    items = payload.get('items', [])
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    if not user_exists(user_id):
        return jsonify({"error": "user not found"}), 404
    order = {"id": NEXT_ID, "user_id": user_id, "items": items}
    ORDERS[NEXT_ID] = order
    NEXT_ID += 1
    return jsonify(order), 201

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = ORDERS.get(order_id)
    if not order:
        return jsonify({"error": "order not found"}), 404
    return jsonify(order)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)