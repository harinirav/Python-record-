import tkinter as tk
import threading
import serial
import time
import os
from gtts import gTTS
from playsound import playsound

# === CONFIGURATION ===
SERIAL_PORT = 'COM6'
BAUD_RATE = 9600
HAND_RAISE_TIMEOUT = 5  # seconds

# === GLOBALS ===
arduino = None
running = False
hand_raised_time = None
last_message = ""

# === SPEAK FUNCTION ===
def speak(message):
    print(f"🔊 Speaking: {message}")
    try:
        tts = gTTS(text=message, lang='en')
        filename = "temp.mp3"
        tts.save(filename)
        playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"❌ Error in speak: {e}")

# === GUI SETUP ===
root = tk.Tk()
root.title("Hand Gesture Voice Feedback")
root.geometry("400x250")

status_label = tk.Label(root, text="Status: Not connected", font=("Arial", 12))
status_label.pack(pady=10)

message_label = tk.Label(root, text="Message: ", font=("Arial", 16), fg="blue")
message_label.pack(pady=10)

def update_message(text):
    message_label.config(text=f"Message: {text}")

# === BACKGROUND READER ===
def read_serial():
    global running, arduino, hand_raised_time, last_message

    try:
        arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        status_label.config(text=f"✅ Connected to {SERIAL_PORT}")
    except Exception as e:
        status_label.config(text=f"❌ Error: {e}")
        return

    speak("Raise your hand")

    while running:
        try:
            if arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8').strip()
                print(f"📩 Received: {line}")
                update_message(line)

                if line != last_message:
                    if "Raise your hand" in line:
                        speak("Raise your hand")
                        hand_raised_time = None
                    elif "Hand raised" in line:
                        speak("Hand raised")
                        speak("Good job")
                        hand_raised_time = time.time()
                    elif "Lower your hand" in line:
                        speak("Lower your hand")
                        speak("Raise your hand")
                        hand_raised_time = None

                    last_message = line
                else:
                    if hand_raised_time and (time.time() - hand_raised_time) > HAND_RAISE_TIMEOUT:
                        speak("Lower your hand")
                        speak("Raise your hand")
                        hand_raised_time = None

            time.sleep(0.1)
        except Exception as e:
            print(f"❌ Runtime error: {e}")
            break

    if arduino:
        arduino.close()
        status_label.config(text="🔌 Disconnected from Arduino")

# === BUTTON FUNCTIONS ===
def start_monitoring():
    global running
    if not running:
        running = True
        threading.Thread(target=read_serial, daemon=True).start()
        status_label.config(text="▶️ Monitoring started")

def stop_monitoring():
    global running
    running = False
    status_label.config(text="⏹️ Monitoring stopped")
    update_message("")

# === BUTTONS ===
btn_frame = tk.Frame(root)
btn_frame.pack(pady=20)

start_btn = tk.Button(btn_frame, text="Start", font=("Arial", 14), command=start_monitoring, bg="green", fg="white")
start_btn.grid(row=0, column=0, padx=20)

stop_btn = tk.Button(btn_frame, text="Stop", font=("Arial", 14), command=stop_monitoring, bg="red", fg="white")
stop_btn.grid(row=0, column=1, padx=20)

# === MAIN LOOP ===
root.mainloop()
