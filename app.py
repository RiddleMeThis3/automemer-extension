from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import firebase_admin
from firebase_admin import credentials, storage

# --- Firebase Setup ---
FIREBASE_KEY_PATH = "secrets/automemer.json"
BUCKET_NAME = "automemer-1e892"

# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_KEY_PATH)
    firebase_admin.initialize_app(cred, {
        'storageBucket': BUCKET_NAME
    })

bucket = storage.bucket()

def upload_to_firebase(local_path: str, remote_path: str) -> str:
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(local_path)
    blob.make_public()
    return blob.public_url

# --- Flask App Setup ---
app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    filename = secure_filename(image.filename)
    unique_filename = f"memes/{uuid.uuid4()}_{filename}"

    # Save temporarily to disk
    os.makedirs("temp", exist_ok=True)
    temp_path = os.path.join("temp", filename)
    image.save(temp_path)

    # Upload to Firebase
    public_url = upload_to_firebase(temp_path, unique_filename)

    # Remove the temporary file
    os.remove(temp_path)

    return jsonify({"url": public_url}), 200

if __name__ == "__main__":
    app.run(debug=True)
