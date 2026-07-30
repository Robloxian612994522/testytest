from flask import Flask, request, jsonify
from ollama import Client
import os

app = Flask(__name__)

# Initialize Ollama Cloud Client using API key from Render Environment Variables
ollama_api_key = os.environ.get("OLLAMA_API_KEY")
ollama_client = Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {ollama_api_key}"} if ollama_api_key else {}
)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "service": "Render AI Server",
        "model": "glm-5.2:cloud"
    }), 200

@app.route('/api/generate', methods=['POST'])
def generate_ai_response():
    data = request.get_json() or {}
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({"error": "Missing 'prompt' in JSON body"}), 400

    try:
        # Call glm-5.2:cloud via Ollama's Cloud API directly from Render
        response = ollama_client.chat(
            model='glm-5.2:cloud',
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        ai_reply = response['message']['content']

        return jsonify({
            "status": "success",
            "prompt": prompt,
            "model": "glm-5.2:cloud",
            "response": ai_reply
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to query Ollama Cloud API: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
