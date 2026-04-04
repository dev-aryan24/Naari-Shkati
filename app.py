import tkinter as tk
from tkinter import messagebox
import threading
import time
import webbrowser
import pygame
import geocoder
import speech_recognition as sr
from datetime import datetime
from pynput.keyboard import Key, Controller
import urllib.parse

# --- Setup ---
pygame.mixer.init()
alert_sound = pygame.mixer.Sound("beep.mp3")
keyboard = Controller()

EMERGENCY_KEYWORDS = ["bachaao", "h elp me","help" ,  "help mi", "help ","emergency", "save me", "danger","bachao"]
WHATSAPP_NUMBER = "+919118516300"

DEFAULT_LOCATION = {
    "city": "Lucknow",
    "state": "Uttar Pradesh",
    "country": "India",
    "lat": 26.8467,
    "lng": 80.9462
}

WHATSAPP_MESSAGE_TEMPLATE = """🚨 EMERGENCY ALERT! 🚨

I need immediate help!

📍 My Location: {city}, {state}, {country}
🗺 Google Maps: https://maps.google.com/?q={lat},{lng}
📅 Time: {time}

Sent via VoiceGuard Emergency System"""

# --- Utility Functions ---
def get_current_location():
    try:
        g = geocoder.ip('me')
        if g.ok:
            return {
                "city": g.city or "Unknown",
                "state": g.state or "Unknown",
                "country": g.country or "Unknown",
                "lat": g.lat,
                "lng": g.lng
            }
    except:
        pass
    return DEFAULT_LOCATION

def send_whatsapp_alert(location):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = WHATSAPP_MESSAGE_TEMPLATE.format(
            city=location["city"],
            state=location["state"],
            country=location["country"],
            lat=location["lat"],
            lng=location["lng"],
            time=current_time
        )
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://web.whatsapp.com/send?phone={WHATSAPP_NUMBER}&text={encoded_message}"
        webbrowser.open(whatsapp_url)
        time.sleep(10)
        keyboard.press(Key.enter)
        print("done")
        keyboard.release(Key.enter)
        print("Done2")
        return True
    except Exception as e:
        print(f"❌ WhatsApp alert failed: {e}")
        return False

def play_alert_sound():
    for _ in range(3):
        alert_sound.play()
        time.sleep(2)

# --- Voice Recognition Thread ---
stop_listening = False

def listen_for_voice(ui_label, status_label, mic_icon):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    ui_label.config(text="⏳ Calibrating microphone...")
    mic_icon.config(text="🎤 Calibrating...")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)

    status_label.config(text="🟢 Listening for emergency...")
    mic_icon.config(text="🎙")

    try:
        while not stop_listening:
            with mic as source:
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                try:
                    text = recognizer.recognize_google(audio).lower()
                    print("🗣 Heard:", text)
                    ui_label.config(text=f"🗣 Heard: {text}")

                    if any(keyword in text for keyword in EMERGENCY_KEYWORDS):
                        location = get_current_location()
                        threading.Thread(target=play_alert_sound, daemon=True).start()
                        send_whatsapp_alert(location)
                        status_label.config(text="🚨 Emergency Detected!")
                        mic_icon.config(text="⚠")
                        time.sleep(5)
                    else:
                        status_label.config(text="🟢 Listening...")
                        mic_icon.config(text="🎙")
                except:
                    status_label.config(text="🔁 Waiting...")
    except:
        status_label.config(text="🛑 Stopped")
        mic_icon.config(text="🔇")

# --- GUI Setup ---
def start_listening():
    global stop_listening
    stop_listening = False
    status_label.config(text="🟢 Activating...")
    threading.Thread(target=listen_for_voice, args=(output_label, status_label, mic_icon), daemon=True).start()

def stop_listening_func():
    global stop_listening
    stop_listening = True
    status_label.config(text="🔴 System Stopped")
    output_label.config(text="")
    mic_icon.config(text="🔇")

# --- Window ---
root = tk.Tk()
root.title("VoiceGuard Emergency System")
root.geometry("600x400")
root.config(bg="#121212")
root.resizable(False, False)

# Title
tk.Label(root, text="🛡 VoiceGuard Emergency System", font=("Helvetica", 20, "bold"),
         bg="#121212", fg="#00e0ff").pack(pady=15)

# Microphone Icon
mic_icon = tk.Label(root, text="🔴", font=("Arial", 30), bg="#121212", fg="white")
mic_icon.pack()

# Status
status_label = tk.Label(root, text="🔴 Not Listening", font=("Arial", 14, "bold"), fg="white", bg="#121212")
status_label.pack(pady=5)

# Output
output_label = tk.Label(root, text="", font=("Arial", 13), fg="#ffc107", bg="#121212", wraplength=520)
output_label.pack(pady=10)

# Buttons Frame
btn_frame = tk.Frame(root, bg="#121212")
btn_frame.pack(pady=20)

style = {"font": ("Arial", 13, "bold"), "padx": 20, "pady": 8, "bd": 0}

start_btn = tk.Button(btn_frame, text="▶ Start", command=start_listening, **style, bg="#28a745", fg="white", activebackground="#218838")
start_btn.grid(row=0, column=0, padx=10)

stop_btn = tk.Button(btn_frame, text="⏹ Stop", command=stop_listening_func, **style, bg="#dc3545", fg="white", activebackground="#c82333")
stop_btn.grid(row=0, column=1, padx=10)

# Footer
tk.Label(root, text="Naari Shakti", font=("Arial", 10), fg="#888", bg="#121212").pack(side="bottom", pady=10)

root.mainloop()