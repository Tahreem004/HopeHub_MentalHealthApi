# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 22:35:10 2025

@author: tehre
"""from flask import Flask, request, jsonify, send_file
from core_logic import (
    translate_urdu_to_english,
    is_query_mental_health_related,
    generate_response,
    azure_tts_urdu
)
from faster_whisper import WhisperModel
import os
import tempfile

app = Flask(__name__)

# Load Whisper model once at startup
model_size = os.getenv("WHISPER_MODEL_SIZE", "base")  # default to "base"
model = WhisperModel(model_size, compute_type="int8")

@app.route("/voice", methods=["POST"])
def voice():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files["audio"]

    # Save to temporary file (preserve extension for ffmpeg compatibility)
    extension = os.path.splitext(audio_file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp:
        temp_path = tmp.name
        audio_file.save(temp_path)

    try:
        # Transcribe Urdu speech
        segments, _ = model.transcribe(temp_path, language="ur")
        transcribed_text = " ".join([segment.text for segment in segments])

        # Translate + process
        english_text = translate_urdu_to_english(transcribed_text)
        if is_query_mental_health_related(english_text):
            response = generate_response(english_text)
        else:
            response = "میں معذرت کرتا ہوں! میں صرف آپ کی ذہنی صحت سے متعلق مشورے دے سکتا ہوں۔"

        # Convert to Urdu TTS
        audio_response = azure_tts_urdu(response)
        if audio_response:
            return send_file(audio_response, mimetype="audio/mpeg", as_attachment=True)
        else:
            return jsonify({"error": "Failed to generate audio"}), 500

    except Exception as e:
        print(f"Error handling voice input: {e}")
        return jsonify({"error": "Internal server error"}), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route("/")
def index():
    return "👋 Mental Health Voice Bot (Urdu) is live!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Railway will auto-set this
    app.run(host="0.0.0.0", port=port)







