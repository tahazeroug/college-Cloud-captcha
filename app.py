"""
Captcha Python Web Service
Cloud Lab 2, 2026 | Dr. Hakim Mitiche
"""

from flask import Flask, jsonify, request
from flask import send_file, render_template, send_from_directory
from flask_cors import CORS
from captcha.image import ImageCaptcha
import random
import string
import os
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")


app = Flask(__name__)
CORS(app)  # 2. Enable it for all routes

# Ensure the 'static' folder exists for our images
if not os.path.exists('static'):
    os.makedirs('static')

# Configuration
CAPTCHA_TEXT_LENGTH = 6
# Global variable to store the current answer 
# (Note: In real cloud apps, we'd use a database/session)
#current_captcha_answer = ""

"""Generates a random string of uppercase letters and digits."""
def generate_random_text():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=CAPTCHA_TEXT_LENGTH))

# make cloud serve the frontend as well (templates/index.html)
@app.route("/")
def index():
    # Serves templates/index.html automatically
    return render_template("index.html")


@app.route("/captcha", methods=["GET"])
def get_captcha():
    """
    Endpoint: GET /captcha
    Generates a text challenge and saves the fuzzy image to disk.
    """
    global current_captcha_answer
    current_captcha_answer = generate_random_text()

    # Create the visual challenge and save to disk
    image = ImageCaptcha(width=280, height=90)

    # Save directly into the static folder
    image.write(current_captcha_answer, 'static/captcha.png')
    
    #with open("captcha.png", "wb") as f:
    #    f.write(image_data.read())

    return jsonify({
        "status": "generated",
        "message": "New captcha image created as 'captcha.png'",
        "debug_text": current_captcha_answer  # Hidden in production, used for lab testing
    }), 200
    #return jsonify({"status": "generated"}), 200

@app.route("/static/<path:filename>")
def serve_static(filename):
    # Helps the browser find the image inside the static folder
    return send_from_directory('static', filename)

@app.route("/verify", methods=["POST"])
def verify_captcha():
    """
    Endpoint: POST /verify
    Checks if the user's JSON input matches the stored captcha.
    """
    # Get JSON data from the request body
    data = request.get_json()
    
    if not data or "captcha" not in data:
        return jsonify({"error": "Missing 'captcha' key in JSON"}), 400

    user_input = data.get("captcha").strip().upper()

    # Case-insensitive comparison for better user experience
    if user_input == current_captcha_answer:
        # success
        return jsonify({"status": "verified", "code": 200})
    # captcha challenge failure
    return jsonify({"status": "failed", "reason": "Incorrect text"}), 401

@app.route("/view-image")
def view_image():
    """Serves the generated captcha image to the browser."""
    if os.path.exists("captcha.png"):
        return send_file("captcha.png", mimetype='image/png')
    return jsonify({"error": "No image generated yet"}), 404

if __name__ == "__main__":
    # Get port number from environment variable 
    # default to 5000 for local testing
    # Render will assign a value to PORT on the server side
    port = int(os.environ.get("PORT", 5000))
    # Start the Flask web server on port 5000
    print("🚀 Captcha Service Running...")
    app.run(host="0.0.0.0", port=port)
    # host="0.0.0.0" is REQUIRED for cloud deployment
