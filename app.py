import os
import requests

from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

WIKIMEDIA_URL = "https://commons.wikimedia.org/w/api.php"


# =========================
# HOME PAGE
# =========================

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


# =========================
# GROQ AI
# =========================

@app.route("/api/groq", methods=["POST"])
def groq_proxy():

    if not GROQ_API_KEY:
        return jsonify({
            "error": {
                "message": "Server is missing GROQ_API_KEY."
            }
        }), 500

    data = request.get_json(force=True, silent=True) or {}

    messages = data.get("messages", [])
    temperature = data.get("temperature", 0.4)
    json_mode = bool(data.get("jsonMode", False))

    if not messages:
        return jsonify({
            "error": {
                "message": "No messages provided."
            }
        }), 400

    body = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature
    }

    if json_mode:
        body["response_format"] = {
            "type": "json_object"
        }

    try:

        resp = requests.post(
            GROQ_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            },
            json=body,
            timeout=60
        )

    except requests.RequestException as exc:

        return jsonify({
            "error": {
                "message": f"Could not reach Groq: {exc}"
            }
        }), 502

    return (
        resp.content,
        resp.status_code,
        {"Content-Type": "application/json"}
    )


# =========================
# IMAGE SEARCH
# =========================

@app.route("/api/images", methods=["POST"])
def image_search():

    data = request.get_json(force=True, silent=True) or {}

    query = str(data.get("query", "")).strip()

    if not query:
        return jsonify({
            "images": []
        })

    try:

        params = {
            "action": "query",
            "format": "json",
            "generator": "search",

            "gsrsearch": query,
            "gsrnamespace": 6,
            "gsrlimit": 5,

            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": 800
        }

        response = requests.get(
            WIKIMEDIA_URL,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        result = response.json()

        images = []

        pages = result.get(
            "query",
            {}
        ).get(
            "pages",
            {}
        )

        for page in pages.values():

            image_info = page.get(
                "imageinfo",
                [{}]
            )[0]

            thumbnail = image_info.get("thumburl")

            if not thumbnail:
                continue

            metadata = image_info.get(
                "extmetadata",
                {}
            )

            artist = metadata.get(
                "Artist",
                {}
            ).get(
                "value",
                ""
            )

            license_name = metadata.get(
                "LicenseShortName",
                {}
            ).get(
                "value",
                ""
            )

            images.append({
                "title": page.get(
                    "title",
                    ""
                ).replace(
                    "File:",
                    ""
                ),

                "url": thumbnail,

                "source": image_info.get(
                    "descriptionurl",
                    ""
                ),

                "artist": artist,

                "license": license_name
            })

        return jsonify({
            "images": images
        })

    except requests.RequestException as exc:

        return jsonify({
            "error": f"Image search failed: {exc}"
        }), 502


# =========================
# START SERVER
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        )
    )
