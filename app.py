import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# Basic landing route to test if the server is running
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "message": "Flask server is live on Render!"
    }), 200

# Endpoint to receive data sent from your local PC
@app.route('/api/connect', methods=['POST'])
def receive_from_pc():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "No message provided")
    
    print(f"Received message from PC: {user_message}")
    
    return jsonify({
        "status": "success",
        "received": user_message,
        "reply": f"Server processed: '{user_message}'"
    }), 200

if __name__ == '__main__':
    # Use the PORT environment variable assigned by Render, defaulting to 5000 locally
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
