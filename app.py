# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 22:35:10 2025

@author: tehre
"""
import os
import uuid
import openai
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import core_logic

# Initialize Flask
app = Flask(__name__)
CORS(app)

# OpenAI API Key (set it via Railway env variable)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create folder for audio responses
if not os.path.exists("responses"):
    os.makedirs("responses")

@app.route("/")
def index():
    return "Mental Health Chatbot is running."

@app.route("/mental-health-voice", methods=["POST"])
def mental_health_voice():
    if "voice" not in request.files:
        return jsonify({"error": "No voice file uploaded"}), 400

    # Save uploaded audio
    audio_file = request.files["voice"]
    temp_filename = f"temp_{uuid.uuid4()}.{audio_file.filename.split('.')[-1]}"
    audio_path = os.path.join(temp_filename)
    audio_file.save(audio_path)

    # Transcribe using OpenAI Whisper API
    try:
        with open(audio_path, "rb") as f:
            transcript = openai.Audio.transcribe("whisper-1", f, language="ur")
            urdu_text = transcript["text"]
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500
    finally:
        os.remove(audio_path)  # Clean up temp file

    print(f"Recognized Urdu: {urdu_text}")

    # Process the text
    english_text = core_logic.translate_urdu_to_english(urdu_text)

    if core_logic.is_query_mental_health_related(english_text):
        english_response = core_logic.generate_response(english_text)
    else:
        english_response = "I'm sorry, I can only assist with mental health topics."

    # Convert response to Urdu speech
    audio_filename = core_logic.azure_tts_urdu(english_response)

    return jsonify({
        "urdu_input": urdu_text,
        "english_translation": english_text,
        "response": english_response,
        "audio_file": f"/responses/{audio_filename}" if audio_filename else None
    })

@app.route("/responses/<filename>")
def serve_audio(filename):
    return send_from_directory("responses", filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Default port for Railway
    app.run(host="0.0.0.0", port=port)





