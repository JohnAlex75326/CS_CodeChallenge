#libraries
import time
import os
import platform

#This part is optional: use text-to-speech for voice output
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
except ImportError:
    tts_engine = None

def speak_message(message):
    