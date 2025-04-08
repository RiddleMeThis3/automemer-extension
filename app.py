from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import json
import firebase_admin
import requests
from firebase_admin import credentials, storage
from flask_cors import CORS

# --- Load Firebase Credentials from Environment ---
FIREBASE_CREDS_JSON = os.getenv("FIREBASE_CREDENTIALS_JSON")
BUCKET_NAME = "automemer-1e892"

if not FIREBASE_CREDS_JSON:
    raise Exception("❌ FIREBASE_CREDENTIALS_JSON environment variable not set!")

if not firebase_admin._apps:
    creds_dict = json.loads(FIREBASE_CREDS_JSON)
    cred = credentials.Certificate(creds_dict)
    firebase_admin.initialize_app(cred, {
        'storageBucket': BUCKET_NAME
    })

bucket = storage.bucket()

def upload_to_firebase(local_path: str, remote_path: str) -> str:
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(local_path)
    blob.make_public()
    return blob.public_url

# --- Flask App ---
app = Flask(__name__)
CORS(app, origins=["chrome-extension://piahfocncoagnafmgkijmniimnjfaddi"])

@app.route("/upload-url", methods=["POST"])
def upload_image_from_url():
    data = request.get_json()
    image_url = data.get("url")
    if not image_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        response = requests.get(image_url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to download image"}), 400

        filename = f"{uuid.uuid4()}.jpg"
        temp_path = os.path.join("temp", filename)
        with open(temp_path, "wb") as f:
            f.write(response.content)

        firebase_path = f"memes/{filename}"
        public_url = upload_to_firebase(temp_path, firebase_path)
        os.remove(temp_path)

        return jsonify({"url": public_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    filename = secure_filename(image.filename)
    unique_filename = f"memes/{uuid.uuid4()}_{filename}"

    # Save temporarily
    os.makedirs("temp", exist_ok=True)
    temp_path = os.path.join("temp", filename)
    image.save(temp_path)

    # Upload to Firebase
    try:
        public_url = upload_to_firebase(temp_path, unique_filename)
    finally:
        os.remove(temp_path)

    return jsonify({"url": public_url}), 200

if __name__ == "__main__":
    app.run(debug=True)
