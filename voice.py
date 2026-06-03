import asyncio
import edge_tts
import pygame
import os
import sr  # Assuming 'sr' is a module for speech recognition, you may need to install it using pip install SpeechRecognition
from datetime import datetime
import webbrowser

pygame.mixer.init()

MALE = "en-US-GuyNeural"
FEMALE = "en-US-AriaNeural"

current_voice = FEMALE
memory = {}
MEMORY_FILE = "memory.json"


async def _speak_async(text):

    if not text:
        print("No text to speak")
        return

    file = "temp_voice.mp3"

    communicate = edge_tts.Communicate(
        text=text,
        voice=current_voice
    )

    await communicate.save(file)

    pygame.mixer.music.load(file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

    pygame.mixer.music.unload()

    if os.path.exists(file):
        os.remove(file)


def speak(text):

    print(f"\nJarvis: {text}\n")

    asyncio.run(
        _speak_async(text)
    )

# =========================
# LISTEN
# =========================

recognizer = sr.Recognizer()

def listen():
    try:
        with sr.Microphone() as source:

            print("Listening...")

            recognizer.adjust_for_ambient_noise(source, duration=0.5)

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=7
            )

            query = recognizer.recognize_google(audio)

            print(f"You: {query}")

            return query.lower()

    except sr.WaitTimeoutError:
        return ""

    except Exception as e:
        print(f"Error listening: {e}")
        return ""

# =========================
# MEMORY SAVE
# =========================

def save_memory(key, value):
    memory[key] = value

    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

# =========================
# MAIN AI
# =========================

def jarvis(query):

    global current_voice

    # STOP
    if "stop" in query or "shutdown" in query or "bye" in query:
        speak("Goodbye master.")
        exit()

    # NAME SAVE
    elif "my name is" in query:

        name = query.replace("my name is", "").strip()

        save_memory("name", name)

        speak(f"Nice to meet you {name}. I will remember your name permanently.")

    # YOUR NAME
    elif "what is my name" in query:

        if "name" in memory:
            speak(f"Your name is {memory['name']}")
        else:
            speak("I don't know your name yet.")

    # REMEMBER
    elif "remember that" in query:

        fact = query.replace("remember that", "").strip()

        save_memory("fact", fact)

        speak("Done. I will remember that permanently.")

    # WHAT REMEMBER
    elif "what do you remember about me" in query:

        responses = []

        if "name" in memory:
            responses.append(f"Your name is {memory['name']}")

        if "fact" in memory:
            responses.append(f"You told me that {memory['fact']}")

        if responses:
            speak(". ".join(responses))
        else:
            speak("I do not remember anything yet.")

    # TIME
    elif "time" in query:

        time = datetime.datetime.now().strftime("%I:%M %p")

        speak(f"The current time is {time}")

    # SEARCH
    elif "search" in query or "latest ai" in query:

        search = query.replace("search", "").strip()

        if search == "":
            search = "latest AI news"

        speak(f"Searching for {search}")

        webbrowser.open(f"https://www.google.com/search?q={search}")

    # CHANGE VOICE
    elif (
        "change voice" in query
        or "female voice" in query
        or "male voice" in query
    ):

        if "female" in query:

            current_voice = FEMALE

            engine.setProperty('voice', FEMALE)

            speak("Voice changed to female")

        elif "male" in query or "mail" in query:

            current_voice = MALE

            engine.setProperty('voice', MALE)

            speak("Voice changed to male")

        else:

            speak("Please say male or female")

            choice = listen()

            print("Voice Choice:", choice)

            if (
                "female" in choice
                or "girl" in choice
            ):

                current_voice = FEMALE

                engine.setProperty('voice', FEMALE)

                speak("Voice changed to female")

            elif (
                "male" in choice
                or "mail" in choice
                or "boy" in choice
            ):

                current_voice = MALE

                engine.setProperty('voice', MALE)

                speak("Voice changed to male")

            else:
                speak("I could not understand the voice selection")

    # WHO ARE YOU
    elif "who are you" in query:

        speak("I am Jarvis. Your personal AI assistant.")

    # HOW ARE YOU
    elif "how are you" in query:

        speak("I am doing great master.")

    # DEFAULT
    else:

        speak(f"You said: {query}")

# =========================
# START
# =========================

speak("Good day, master! Jarvis at your service.")

while True:

    query = listen()

    if query != "":
        jarvis(query)
