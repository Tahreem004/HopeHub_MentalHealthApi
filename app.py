# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 22:35:10 2025

@author: tehre
"""

from flask import Flask, request, jsonify, send_file
from core_logic import translate_urdu_to_english, is_query_mental_health_related, generate_response, azure_tts_urdu
import os

app = Flask(__name__)

@app.route("/classify", methods=["POST"])
def classify():
    data = request.json
    text = data.get("text", "")
    english = translate_urdu_to_english(text)
    result = is_query_mental_health_related(english)
    return jsonify({"mental_health_related": result})

@app.route("/respond", methods=["POST"])
@app.route("/")
def index():
    return "Hello, world!"

def respond():
    data = request.json
    urdu_text = data.get("text", "")
    english_text = translate_urdu_to_english(urdu_text)
    
    if is_query_mental_health_related(english_text):
        response = generate_response(english_text)
    else:
        response = "میں معذرت کرتا ہوں! میں صرف آپ کی ذہنی صحت سے متعلق مشورے دے سکتا ہوں۔"
    
    audio_file = azure_tts_urdu(response)
    if audio_file:
        return send_file(audio_file, mimetype="audio/mpeg", as_attachment=True)
    else:
        return jsonify({"error": "Failed to generate audio"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

