# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 22:35:10 2025

@author: tehre
"""
import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import speech_recognition as sr
import core_logic

app = Flask(__name__)
CORS(app)

# Ensure responses folder exists
RESPONSE_DIR = "responses"
if not os.path.exists(RESPONSE_DIR):
    os.makedirs(RESPONSE_DIR)

@app.route("/")
def index():
    return "Mental Health Voice API is running!"

@app.route("/mental-health-voice", methods=["POST"])
def mental_health_voice():
    if "voice" not in request.files:
        return jsonify({"error": "No voice file uploaded"}), 400

    # Save uploaded .wav file directly
    uploaded_file = request.files["voice"]
    unique_id = str(uuid.uuid4())
    audio_path = f"temp_{unique_id}.wav"
    uploaded_file.save(audio_path)

    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
        urdu_text = recognizer.recognize_google(audio_data, language="ur-PK")
    except sr.UnknownValueError:
        os.remove(audio_path)
        return jsonify({"error": "Could not understand the audio"}), 400
    except sr.RequestError as e:
        os.remove(audio_path)
        return jsonify({"error": f"Speech recognition error: {e}"}), 500

    os.remove(audio_path)  # Cleanup

    print(f"Recognized Urdu text: {urdu_text}")
    english_text = core_logic.translate_urdu_to_english(urdu_text)

    # Generate response
    if core_logic.is_query_mental_health_related(english_text):
        english_response = core_logic.generate_response(english_text)
    else:
        english_response = "I'm sorry, I can only assist with mental health topics."

    # Urdu voice response
    audio_filename = core_logic.azure_tts_urdu(english_response)

    return jsonify({
        "urdu_input": urdu_text,
        "english_translation": english_text,
        "response": english_response,
        "audio_file": f"/responses/{audio_filename}" if audio_filename else None
    })

@app.route("/responses/<filename>")
def serve_audio(filename):
    return send_from_directory(RESPONSE_DIR, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)




