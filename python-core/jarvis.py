import speech_recognition as sr
import pyttsx3
import webbrowser
import pyautogui
import requests
import os
import json
import subprocess
from datetime import datetime
from groq import Groq

# =========================
# API KEYS
# =========================


GROQ_API_KEY = "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"
WEATHER_API_KEY = "c054ad25b58c49cd8c2386ded918f5ee"


client = Groq(api_key=GROQ_API_KEY)

# =========================
# FEMALE VOICE SETUP
# =========================

engine = pyttsx3.init()

voices = engine.getProperty('voices')

for voice in voices:
    if "female" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

engine.setProperty('rate', 175)
engine.setProperty('volume', 1)

# =========================
# USER MEMORY
# =========================

MEMORY_FILE = "memory.json"

if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump({"name": "Manik"}, f)

with open(MEMORY_FILE, "r") as f:
    memory = json.load(f)

USER_NAME = memory.get("name", "Manik")

# =========================
# SPEAK
# =========================

def speak(text):
    print(f"\n🤖 Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

# =========================
# LISTEN
# =========================

def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("\n🎤 Listening...")

        recognizer.adjust_for_ambient_noise(source, duration=1)

        recognizer.energy_threshold = 300
        recognizer.pause_threshold = 1

        audio = recognizer.listen(
            source,
            timeout=10,
            phrase_time_limit=8
        )

    try:
        text = recognizer.recognize_google(
            audio,
            language="hi-IN"
        )

        print(f"🧑 You: {text}")
        return text.lower()

    except:
        return ""

# =========================
# WEATHER
# =========================

def get_weather(city="Delhi"):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"

        data = requests.get(url).json()

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]

        return f"{city} me temperature {temp} degree hai aur weather {desc} hai"

    except:
        return "Weather nahi mil pa raha Boss"

# =========================
# AI CHAT
# =========================

def ask_ai(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    Tum Jarvis ho.
                    Tum ek smart female AI assistant ho.
                    User ka naam {USER_NAME} hai.
                    Hindi + English mix me natural jawab do.
                    Short aur smart jawab do.
                    """
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=200
        )

        return completion.choices[0].message.content

    except Exception as e:
        print(e)
        return "Internet ya AI issue aa raha hai Boss"

# =========================
# COMMANDS
# =========================

def execute_command(command):

    global USER_NAME

    # =====================
    # SAVE NAME
    # =====================

    if "mera naam" in command:

        new_name = command.replace("mera naam", "").replace("hai", "").strip()

        USER_NAME = new_name.capitalize()

        memory["name"] = USER_NAME

        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f)

        return f"Okay Boss, aapka naam permanently save kar liya hai {USER_NAME}"

    # =====================
    # OPEN GOOGLE
    # =====================

    elif (
        "google open" in command
        or "open google" in command
        or "गूगल ओपन" in command
    ):

        webbrowser.open("https://google.com")

        return f"Google khul gaya Boss"

    # =====================
    # OPEN YOUTUBE
    # =====================

    elif "youtube" in command:

        webbrowser.open("https://youtube.com")

        return "YouTube open kar diya Boss"

    # =====================
    # TIME
    # =====================

    elif "time" in command or "samay" in command:

        now = datetime.now().strftime("%I:%M %p")

        return f"Boss abhi time {now} hai"

    # =====================
    # SCREENSHOT
    # =====================

    elif "screenshot" in command:

        img = pyautogui.screenshot()

        img.save("screenshot.png")

        return "Screenshot save ho gaya Boss"

    # =====================
    # VOLUME UP
    # =====================

    elif (
        "volume up" in command
        or "volume bada" in command
        or "आवाज बढ़ा" in command
    ):

        pyautogui.press("volumeup")

        return "Volume badha diya Boss"

    # =====================
    # VOLUME DOWN
    # =====================

    elif (
        "volume down" in command
        or "volume kam" in command
        or "आवाज कम" in command
    ):

        pyautogui.press("volumedown")

        return "Volume kam kar diya Boss"

    # =====================
    # WEATHER
    # =====================

    elif "weather" in command:

        return get_weather()

    # =====================
    # SEARCH
    # =====================

    elif "search" in command:

        query = command.replace("search", "").strip()

        webbrowser.open(
            f"https://www.google.com/search?q={query}"
        )

        return f"{query} search kar raha hu Boss"

    # =====================
    # EXIT
    # =====================

    elif (
        "goodbye" in command
        or "bye" in command
        or "band ho ja" in command
    ):

        speak(f"Goodbye {USER_NAME}")

        exit()

    # =====================
    # AI CHAT
    # =====================

    else:
        return ask_ai(command)

# =========================
# MAIN LOOP
# =========================

def main():

    speak(f"Hello {USER_NAME}, Jarvis online")

    while True:

        command = listen()

        if command == "":
            continue

        reply = execute_command(command)

        speak(reply)

# =========================
# START
# =========================

if __name__ == "__main__":
    main()