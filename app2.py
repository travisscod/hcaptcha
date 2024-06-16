from flask import Flask, render_template, jsonify
from hcaptcha_image_scraper import HcaptchaImagesDownloader
from auto_train import DataUploader
import requests
import os
import shutil
import time
import threading
import requests

app = Flask(__name__)

amount = 0

def delete_repository(repository_name):
    url = f"https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/alfred/{repository_name}/delete"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sec-gpc": "1"
    }
    return requests.get(url, headers=headers)

def create_repository(repository_name):
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "priority": "u=1, i",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sec-gpc": "1"
    }
    url = f"https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/alfred/{repository_name}/init"
    req = requests.get(url, headers=headers)
    print(req)
    return req

def clear_hcaptcha_folder():
    folder_path = './hcaptcha'
    if os.path.exists(folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))
    else:
        os.makedirs(folder_path)
    print("Folder cleared at:", time.strftime("%Y-%m-%d %H:%M:%S"))

def scrape_images():
    global amount
    capdl = HcaptchaImagesDownloader()
    amount = 0
    subfolders = [os.path.join("./hcaptcha", dir) for dir in os.listdir("./hcaptcha") if os.path.isdir(os.path.join("./hcaptcha", dir))]

    for _ in range(40):
        time.sleep(1)
        capdl.download_images()
        amount += 1

    for index, folder in enumerate(subfolders):
        repository = create_repository(f"folder_{index}")
        images = [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith(".png")]
        uploader = DataUploader("alfred", repository)
        uploader.upload_images_to_s3(images)

    print("Scraped 1000 images at:", time.strftime("%Y-%m-%d %H:%M:%S"))

def time_based_execution():
    folder_cleared = False
    images_scraped = False
    while True:
        current_time = time.strftime("%H:%M")
        if current_time == "03:42" and not folder_cleared:
            print("Clearing folder")
            for i in range(len(os.listdir("./hcaptcha"))):
                delete_repository(f"folder {i}")
            clear_hcaptcha_folder()
            folder_cleared = True
            images_scraped = False
        elif current_time == "03:44" and not images_scraped:
            print("Scraping images")
            scrape_images()
            images_scraped = True
            folder_cleared = False
        elif current_time != "03:13" and current_time != "22:39":
            folder_cleared = False 
            images_scraped = False
        time.sleep(45)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/count')
def count():
    global amount
    return jsonify({"count": amount})

if __name__ == "__main__":
    threading.Thread(target=time_based_execution).start()
    app.run(host='0.0.0.0', port=5000, debug=True)