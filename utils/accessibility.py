import pyttsx3
import speech_recognition as sr

def speak_text(text: str):
    """
    Convert the provided text to speech and play it aloud.
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_voice_input(prompt: str = "Please speak now...") -> str:
    """
    Capture voice input from the microphone (using PyAudio) and return the recognized text.
    If recognition fails, returns an error message.
    """
    recognizer = sr.Recognizer()
    # This uses PyAudio internally:
    microphone = sr.Microphone()

    # Optionally, speak the prompt aloud
    # speak_text(prompt)
    print(prompt)  # Display prompt in terminal for debugging

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        # Using Google's speech recognition API (requires internet)
        voice_text = recognizer.recognize_google(audio)
        return voice_text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "Request error: check your network connection"
