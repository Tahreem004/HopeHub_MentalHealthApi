# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 22:35:10 2025

@author: tehre
"""
import speech_recognition as sr
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import core_logic
import uuid

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "Hello, world!"

# Folder for saving audio files
if not os.path.exists("responses"):
    os.makedirs("responses")

@app.route("/mental-health-voice", methods=["POST"])
def mental_health_voice():
    if "voice" not in request.files:
        return jsonify({"error": "No voice file uploaded"}), 400

    audio_file = request.files["voice"]
    audio_path = os.path.join("temp_audio.wav")
    audio_file.save(audio_path)

    # Speech Recognition
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        urdu_text = recognizer.recognize_google(audio, language="ur-PK")
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand the audio"}), 400
    except sr.RequestError as e:
        return jsonify({"error": f"Speech recognition error: {e}"}), 500

    print(f"Recognized Urdu text: {urdu_text}")

    english_text = core_logic.translate_urdu_to_english(urdu_text)

    if core_logic.is_query_mental_health_related(english_text):
        english_response = core_logic.generate_response(english_text)
        audio_filename = core_logic.azure_tts_urdu(english_response)
    else:
        english_response = "I'm sorry, I can only assist with mental health topics."
        audio_filename = core_logic.azure_tts_urdu(english_response)

    # Respond with audio file path
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
    port = int(os.environ.get("PORT", 8080))  # default to 8080 for Railway
    app.run(host="0.0.0.0", port=port)
