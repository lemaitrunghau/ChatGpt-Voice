import os
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import pygame
import time
import threading

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Khởi tạo pygame mixer cho audio playback
pygame.mixer.init()

def initialize_model(model_name="gemini-1.5-flash"):
    """Initialize the Gemini model."""
    model = genai.GenerativeModel(model_name)
    return model

def get_response_from_ai(model, model_behavior, user_input, image=None):
    if image is None:
        response = model.generate_content([model_behavior, user_input])
    else:
        response = model.generate_content([model_behavior, image, user_input])
    return response.text

def recognize_speech(language="vi-VN"):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Hãy nói chuyện...")
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)

    try:
        user_input = recognizer.recognize_google(audio, language=language)
        print(f"User: {user_input}")
        return user_input
    except Exception as e:
        print(f"Lỗi nhận dạng giọng nói: {e}")
        return None

def speak_response(response):
    tts = gTTS(text=response, lang="vi", tld='com')
    mp3_file = BytesIO()
    tts.write_to_fp(mp3_file)
    mp3_file.seek(0)
    sound = pygame.mixer.Sound(mp3_file)
    pygame.mixer.Sound.play(sound)
    while pygame.mixer.get_busy():
        time.sleep(0.1)