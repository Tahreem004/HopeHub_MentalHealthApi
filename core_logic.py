# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 16:28:08 2025

@author: tehre
"""

import os
import uuid
import requests
import azure.cognitiveservices.speech as speechsdk
from deep_translator import GoogleTranslator

# Load API keys from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
AZURE_TTS_KEY_1 = os.getenv("AZURE_TTS_KEY_1")
AZURE_TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY")
AZURE_REGION = os.getenv("AZURE_REGION")
AZURE_TRANSLATOR_REGION = os.getenv("AZURE_TRANSLATOR_REGION")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
translator_endpoint = "https://api.cognitive.microsofttranslator.com"

def translate_urdu_to_english(text):
    try:
        return GoogleTranslator(source="ur", target="en").translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return ""

def translate_english_to_urdu(text):
    url = f"{translator_endpoint}/translate?api-version=3.0&from=en&to=ur"
    headers = {
        'Ocp-Apim-Subscription-Key': AZURE_TRANSLATOR_KEY,
        'Ocp-Apim-Subscription-Region': AZURE_TRANSLATOR_REGION,
        'Content-type': 'application/json'
    }
    body = [{'text': text}]
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    result = response.json()
    return result[0]['translations'][0]['text']

def is_query_mental_health_related(text):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = (
        "You are a classifier. Respond only with 'Yes' or 'No'.\n"
        "Is the following text related to mental health, physical health, emotions, depression, anxiety, or therapy?\n\n"
        f"Text: \"{text}\"\nAnswer:"
    )
    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        result = response.json()
        answer = result["choices"][0]["message"]["content"].strip().lower()
        return "yes" in answer
    except Exception as e:
        print(f"Classifier Exception: {e}")
        return False

def generate_response(english_text):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "MentalHealthBot"
    }
    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [
            {
                "role": "user",
                "content": f"A patient says: \"{english_text}\". Respond as a kind and helpful mental health therapist."
            }
        ]
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Response generation failed: {e}")
        return "Error generating response."

def azure_tts_urdu(text):
    try:
        urdu_text = translate_english_to_urdu(text)
        ssml = f"""
        <speak version='1.0' xml:lang='ur-PK'>
            <voice xml:lang='ur-PK' xml:gender='Male' name='ur-PK-AsadNeural'>
                {urdu_text}
            </voice>
        </speak>
        """
        tts_url = f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_TTS_KEY_1,
            "Content-Type": "application/ssml+xml",
            "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
            "User-Agent": "UrduMentalHealthBot"
        }
        response = requests.post(tts_url, headers=headers, data=ssml.encode("utf-8"))

        if response.status_code == 200:
            filename = f"response_{uuid.uuid4().hex}.mp3"
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
        else:
            print("Azure TTS Error:", response.status_code, response.text)
            return None
    except Exception as e:
        print(f"TTS Exception: {e}")
        return None
