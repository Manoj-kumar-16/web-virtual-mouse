import speech_recognition as sr
import pyttsx3
import datetime
import os
import sounddevice as sd
import numpy as np
import io
import requests
import ssl
from urllib3 import PoolManager
from requests.adapters import HTTPAdapter

# Initialize the speech recognition and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Set properties for speech (optional)
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)

# Function to talk (Text-to-Speech)
def talk(text):
    engine.say(text)
    if not engine._inLoop:
        engine.runAndWait()

# Function to listen to user input (Speech-to-Text) using sounddevice
def listen():
    print("Listening... Speak now!")
    
    # Record audio for 5 seconds using sounddevice
    audio_data = record_audio(5)
    
    # Process the recorded audio data to recognize speech
    if audio_data is not None:
        return recognize_audio(audio_data)
    return None

# Function to record audio using sounddevice for the given duration
def record_audio(duration):
    try:
        # Record audio for a specified duration (in seconds)
        print("Recording...")
        audio_data = sd.rec(int(duration * 16000), samplerate=16000, channels=1, dtype='int16')
        sd.wait()  # Wait until recording is finished
        print("Recording complete.")
        return audio_data
    except Exception as e:
        print(f"Error recording audio: {e}")
        return None

# Function to recognize speech from recorded audio
def recognize_audio(audio_data):
    try:
        # Convert the NumPy array (audio data) to a byte stream
        audio_bytes = audio_data.tobytes()
        audio_io = io.BytesIO(audio_bytes)
        
        # Use speech_recognition to recognize the speech
        audio = sr.AudioData(audio_io.read(), 16000, 2)  # 16000 Hz, 2 bytes per sample (16-bit audio)
        query = recognizer.recognize_google(audio)  # Using Google API
        print(f"You said: {query}")
        return query.lower()
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        print("Sorry, my speech service is down.")
        return None

# Function to get current location using ipinfo.io API (with SSL Version control)
def get_current_location():
    try:
        # Create an SSLContext to force a specific SSL/TLS version
        context = ssl.create_default_context()
        context.set_ciphers('DEFAULT@SECLEVEL=1')  # This can enforce an older SSL/TLS version

        # Use a custom adapter to enforce SSLContext
        adapter = HTTPAdapter(ssl_context=context)
        session = requests.Session()
        session.mount('https://', adapter)

        # Send a request to ipinfo.io to get the current location based on IP
        response = session.get('https://ipinfo.io')
        data = response.json()

        # Extract the city and country from the response
        location = data.get("city", "Unknown City") + ", " + data.get("country", "Unknown Country")
        talk(f"Your current location is {location}.")
    except Exception as e:
        talk("Sorry, I couldn't retrieve your location. Please check your network connection.")

# Process the user's query
def process_query(query):
    if 'hello jarvis' in query:
        talk("Hello Buddy, how can I assist you today?")
    elif 'your name' in query:
        talk("I am your Partner Jarvis, ready to help!")
    elif 'whats time' in query:
        now = datetime.datetime.now()
        talk(f"The current time is {now.hour}:{now.minute}")
    elif 'date' in query:
        now = datetime.datetime.now()
        talk(f"Today's date is {now.strftime('%B %d, %Y')}")
    elif 'where are we' in query or 'location' in query:
        talk("Fetching your current location...")
        get_current_location()
    elif 'search' in query:
        query = query.replace("search", "")
        talk(f"Searching for {query} on the web.")
        open_chrome_search(query)
    elif 'shutdown' in query or 'exit' in query:
        talk("Goodbye!")
        exit()

# Function to open Chrome and search the web
def open_chrome_search(query):
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
    url = f"https://www.google.com/search?q={query}"
    try:
        os.startfile(f'"{chrome_path}" {url}')
    except FileNotFoundError:
        talk("Chrome is not found on your system. Please check the path.")
    except Exception as e:
        talk(f"An error occurred: {str(e)}")

# Main loop
def main():
    talk("Hello! I am your assistant. To wake me up, say 'Password'.")
    while True:
        query = listen()  # Listen for a command
        if query and 'wake up jarvis' in query:
            talk("Hi buddy! You are back! I am awake now! How can I help you today?")
            while True:
                query = listen()  # Listen for a command after waking up
                if query:
                    process_query(query)
        elif query:
            talk("Please say 'Wake up' to activate me.")

if __name__ == "__main__":
    main()

