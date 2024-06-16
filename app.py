from flask import Flask, render_template, request, render_template_string, session
from hcaptcha_image_scraper import HcaptchaImagesDownloader
from auto_train import DataUploader
import json
import os
import random
import requests
import time
import math

app = Flask(__name__)


def upload_classes(classes, repository):
    url = f"https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/alfred/{repository.replace(' ', '_')}/dataset/classes"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "classes": json.dumps({str(i): class_name for i, class_name in enumerate(classes)}),
        "priority": "u=1,i",
        "sec-ch-ua": "\"Google Chrome\";v=\"125\",\"Chromium\";v=\"125\",\"Not.A/Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sec-gpc": "1"
    }
    return requests.get(url, headers=headers)

def get_classes(repository):
    url = f"https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/alfred/{repository}"
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

    response = requests.get(url, headers=headers)
    response_json = response.json()

    if isinstance(response_json, list) and len(response_json) > 0:
        data = response_json[0]
        if "classes" in data and isinstance(data["classes"], dict):
            classes = data["classes"].get("M", {})
            sorted_keys = sorted(classes.keys(), key=int)
            return [classes[key]["S"] for key in sorted_keys]
        else:
            raise ValueError("Unexpected JSON structure in 'classes' key")
    else:
        raise ValueError("Unexpected JSON structure: not a list or empty list")

def get_images(repository):
    url = f"https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/alfred/{repository}/dataset/view"
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
        "sec-gpc": "1",
        "start": "0",
        "end": "50"
    }
    response = requests.get(url, headers=headers)
    return response.json()["files_names"]

def auto_label():
    for repository in [os.path.basename(os.path.join("./hcaptcha", dir)) for dir in os.listdir("./hcaptcha") if os.path.isdir(os.path.join("./hcaptcha", dir))]:
        url = f"https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/alfred/{repository.replace(' ', '_')}/dataset/autolabel"
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "priority": "u=1, i",
            "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "sec-gpc": "1"
        }

        body = {
            "images": "|".join(get_images(repository.replace(' ', '_'))),
            "classes": "|".join([class_name for class_name in get_classes(repository.replace(' ', '_'))])
        }

        response_autolabel = requests.post(url, headers=headers, json=body)

        return response_autolabel.json()

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
    response = requests.options(url, headers=headers)
    response.raise_for_status()

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "description": "",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sec-gpc": "1"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return repository_name

def get_images_from_repository(repository):
    response = requests.get(f"https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/alfred/{repository}/dataset/view", headers={
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "end": "50",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "sec-gpc": "1",
    "start": "0"
    })

    return response.json()

def check_if_done(repository):
    response = requests.get(f"https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/alfred/{repository.replace(' ', '_')}/dataset/view", headers={
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "end": "50",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sec-gpc": "1",
        "start": "0"
    })
    return len(response.json()["annotations"][0].split("\n")) - 1 == len(response.json()["files_names"])

def auto_train(repository):
    url = f"https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/alfred/{repository.replace(' ', '_')}/models/train" 
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "epochs": "10",
        "model": "yolov8s",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sec-gpc": "1",
        "test_percent": "20",
        "train_percent": "70",
        "valid_percent": "10"
        }

    response = requests.get(url, headers=headers)
    return response.json()

@app.route('/')
def index():
    return render_template('index.html', alert="")

@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    try:
        username = "alfred"
        folder = "./hcaptcha"
        capdl = HcaptchaImagesDownloader()
        amount = int(request.form.get("number_of_captchas"))
        amount = int(math.ceil(amount / 2))
        for _ in range(amount):
            capdl.download_images()
        
    
        repository_name = [os.path.basename(os.path.join(folder, dir)).replace(" ", "_") for dir in os.listdir(folder) if os.path.isdir(os.path.join(folder, dir)) and dir.isalpha()]
        print(repository_name)
        
        subfolders = [os.path.join(folder, dir) for dir in os.listdir(folder) if os.path.isdir(os.path.join(folder, dir))]
        
        for folder in subfolders:
            repository = create_repository(repository_name[subfolders.index(folder)].replace(" ", "_"))
            images = [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith(".png")]
            uploader = DataUploader(username, repository)
            uploader.upload_images_to_s3(images)
        
        image_dict = {}
        for repository in repository_name:
            print(repository.replace(" ", "_"))
            images = get_images_from_repository(repository.replace(" ", "_"))
            if "presigned_urls" in images and isinstance(images["presigned_urls"], list):
                if len(images["presigned_urls"]) < 3:
                    random_img = images["presigned_urls"]
                else:
                    random_img = random.sample(images["presigned_urls"], 3)
            else:
                print("Error: 'presigned_urls' is not a valid key in 'images' or it's not a list.")
        
        return render_template('index.html', alert="Scraping and uploading completed successfully", repositories=repository_name, images=image_dict)
    except Exception as e:
        print(f"An error occurred during the process: {e}")
        return render_template('index.html', alert=f"An error occurred during the process: {e}")

@app.route('/train_model', methods=['GET', 'POST'])
def train_model():
    if request.method == 'POST':
        for key, value in request.form.items():
            classes = value.split(",")
            print(classes)
            upload_classes(classes, key)
        auto_label()
        for repository in [os.path.basename(os.path.join("./hcaptcha", dir)) for dir in os.listdir("./hcaptcha") if os.path.isdir(os.path.join("./hcaptcha", dir))]:
            while not check_if_done(repository):
                time.sleep(5)
            auto_train(repository)

        return render_template('index.html', alert="Model training completed successfully")
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)