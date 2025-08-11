import time
import platform
import os
from threading import Thread

# --- Optional TTS ---
try:
    import pyttsx3
    TTS_INSTALLED = True
except Exception:
    TTS_INSTALLED = False

def _speak_thread(message):
    """Run TTS (or fallback beep) in a thread to avoid blocking the main loop."""
    # Print a newline first so the MM:SS line doesn't get garbled
    print("\n" + message)
    if TTS_INSTALLED:
        try:
            # Initialize engine inside thread to avoid cross-thread engine issues
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(message)
            engine.runAndWait()
            # engine.stop()  # optional
        except Exception:
            _fallback_beep_once()
    else:
        _fallback_beep_once()

def speak_async(message):
    Thread(target=_speak_thread, args=(message,), daemon=True).start()

def _fallback_beep_once():
    """Platform-specific audible fallback (single beep)."""
    if platform.system() == "Windows":
        try:
            import winsound
            winsound.Beep(1000, 1500)  # frequency 1000Hz, duration 450ms
        except Exception:
            # fallback to terminal bell
            print('\a', end='', flush=True)
    else:
        # terminal bell for Unix-like systems
        print('\a', end='', flush=True)


def stopwatch_minute_announcer():
    """Start stopwatch referenced from script start; announce every full minute."""
    start_time = time.time()
    minutes_announced = 0                # how many minute announcements we've already made
    next_announce_time = start_time + 60 # first announce at +60s

    print("Stopwatch started (reference = script start). Press Ctrl+C to stop.")

    try:
        while True:
            now = time.time()
            elapsed = now - start_time
            mins, secs = divmod(int(elapsed), 60)

            # Live MM:SS display (overwrites same line)
            print(f"\rElapsed Time: {mins:02d}:{secs:02d}", end='', flush=True)

            # If we've reached or passed the next announce time, handle announcements.
            if now >= next_announce_time:
                # Determine how many whole minutes have passed since start
                whole_minutes = int((now - start_time) // 60)

                # Announce each minute we haven't yet announced (handles missed minutes)
                for m in range(minutes_announced + 1, whole_minutes + 1):
                    speak_async("Switch")

                # Update trackers
                minutes_announced = whole_minutes
                next_announce_time = start_time + (minutes_announced + 1) * 60

            time.sleep(0.15)  # short sleep for responsive display
    except KeyboardInterrupt:
        print("\nStopwatch stopped.")


if __name__ == "__main__":
    stopwatch_minute_announcer()