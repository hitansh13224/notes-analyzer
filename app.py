import os

import requests
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder=".", static_url_path="")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/api/groq", methods=["POST"])
def groq_proxy():
    if not GROQ_API_KEY:
        return (
            jsonify({"error": {"message": "Server is missing GROQ_API_KEY. Set it as an environment variable and restart."}}),
            500,
        )

    data = request.get_json(force=True, silent=True) or {}
    messages = data.get("messages", [])
    temperature = data.get("temperature", 0.4)
    json_mode = bool(data.get("jsonMode", False))

    if not messages:
        return jsonify({"error": {"message": "No messages provided."}}), 400

    body = {"model": GROQ_MODEL, "messages": messages, "temperature": temperature}
    if json_mode:
        body["response_format"] = {"type": "json_object"}

    try:
        resp = requests.post(
            GROQ_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}",
            },
            json=body,
            timeout=60,
        )
    except requests.RequestException as exc:
        return jsonify({"error": {"message": f"Could not reach Groq: {exc}"}}), 502

    return (resp.content, resp.status_code, {"Content-Type": "application/json"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
