import time
import os
import platform

"""def announce(message):
    engine = pyttsx3.init()
    engine.say(message)
    engine.runAndWait()"""

#This part is optional: use text-to-speech for voice output
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
except ImportError:
    tts_engine = None

def speak_message(message):
    if tts_engine:
        tts_engine.say(message)
        tts_engine.runAndWait()
    else:
        print(message)
        if platform.system == "Windows":
            import winsound
            winsound.Beep(1500,1000)
        else:
            os.system('printf"\\a"')

def stopwatch():
    minutes_passed = 0
    print("Stopwatch started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(60)  # Wait for 1 minute
            minutes_passed += 1
            message = "A minute has passed"
            print(message)
            speak_message(message)
            #announce(message)
    except KeyboardInterrupt:
        print("\nStopwatch stopped.")

if __name__ == "__main__":
    stopwatch()
################################