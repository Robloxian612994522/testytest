import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from ollama import Client

app = Flask(__name__)

# Read Ollama API Key from Render Environment Variables
ollama_api_key = os.environ.get("OLLAMA_API_KEY")

# Initialize Ollama Cloud Client
ollama_client = Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {ollama_api_key}"} if ollama_api_key else {}
)

# Store incoming payloads in memory (keeps last 50 requests)
REQUEST_LOGS = []

# Dark mode web interface HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Render AI Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 10px; }
        .card { background-color: #1e293b; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .log-item { background-color: #0f172a; border-left: 4px solid #38bdf8; margin-bottom: 15px; padding: 12px; border-radius: 4px; }
        .timestamp { font-size: 0.8em; color: #94a3b8; }
        pre { background: #020617; padding: 10px; border-radius: 4px; overflow-x: auto; color: #a5f3fc; }
        input[type="text"] { width: 75%; padding: 10px; border-radius: 4px; border: 1px solid #334155; background: #0f172a; color: white; }
        button { padding: 10px 20px; background-color: #0284c7; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0369a1; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Render AI Payload Dashboard</h1>
        
        <div class="card">
            <h3>Send Test Request</h3>
            <form action="/api/generate" method="POST" onsubmit="sendPrompt(event)">
                <input type="text" id="promptInput" placeholder="Type a prompt to send..." required>
                <button type="submit">Submit</button>
            </form>
        </div>

        <div class="card">
            <h3>Recent Request Payloads (<span id="count">{{ logs|length }}</span>)</h3>
            <div id="logsContainer">
                {% for log in logs %}
                <div class="log-item">
                    <div class="timestamp">[{{ log.time }}] - IP: {{ log.ip }} - Endpoint: {{ log.endpoint }}</div>
                    <p><strong>Payload:</strong></p>
                    <pre>{{ log.payload }}</pre>
                    {% if log.response %}
                    <p><strong>AI Response:</strong></p>
                    <pre>{{ log.response }}</pre>
                    {% endif %}
                </div>
                {% else %}
                <p style="color: #94a3b8;">No requests logged yet. Send a payload from your PC or use the form above!</p>
                {% endfor %}
            </div>
        </div>
    </div>

    <script>
        async function sendPrompt(e) {
            e.preventDefault();
            const prompt = document.getElementById('promptInput').value;
            await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt })
            });
            window.location.reload();
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def home():
    # Render the web interface showing all stored request logs
    return render_template_string(HTML_TEMPLATE, logs=reversed(REQUEST_LOGS))

@app.route('/api/generate', methods=['POST'])
def generate_ai_response():
    data = request.get_json(silent=True) or {}
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({"error": "Missing 'prompt' in JSON body"}), 400

    ai_reply = ""
    try:
        # Query Ollama Cloud API
        response = ollama_client.chat(
            model='glm-5.2:cloud',
            messages=[{'role': 'user', 'content': prompt}]
        )
        ai_reply = response['message']['content']
    except Exception as e:
        ai_reply = f"Error calling Ollama API: {str(e)}"

    # Record payload and response details to show on the web interface
    log_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip": request.remote_addr,
        "endpoint": request.path,
        "payload": data,
        "response": ai_reply
    }
    REQUEST_LOGS.append(log_entry)
    
    # Keep log history capped at 50 items
    if len(REQUEST_LOGS) > 50:
        REQUEST_LOGS.pop(0)

    return jsonify({
        "status": "success",
        "prompt": prompt,
        "model": "glm-5.2:cloud",
        "response": ai_reply
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
