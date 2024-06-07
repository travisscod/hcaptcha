from flask import Flask, render_template, request, render_template_string
from hcaptcha_image_scraper import HcaptchaImagesDownloader
from auto_train import DataUploader
import time
import os
import requests

app = Flask(__name__)

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

@app.route('/')
def index():
    folders = get_hcaptcha_folders()
    return render_template('index.html', alert="", folders=folders)

@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    try:
        username = "alfred"
        folder = "./hcaptcha"
        capdl = HcaptchaImagesDownloader()

        for _ in range(50):
            capdl.download_images()

        time.sleep(3)

        subfolders = [os.path.join(folder, dir) for dir in os.listdir(folder) if os.path.isdir(os.path.join(folder, dir))]
        for i, subfolder in enumerate(subfolders):
            print(f"{i+1}. {os.path.basename(subfolder)}")
        selected_folders = [os.path.basename(subfolder) for subfolder in subfolders]
        for folder in selected_folders:
            repository = create_repository(folder.replace(" ", "_"))
            images = [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith(".png")]
            uploader = DataUploader()
            uploader.upload_images_to_s3(images, username, repository)
            time.sleep(3)
            print("Images uploaded successfully.")

        return render_template('index.html', alert="Scraping and uploading completed successfully", folders=get_hcaptcha_folders())
    except Exception as e:
        print(f"An error occurred during the process: {e}")
        return render_template('index.html', alert=f"An error occurred during the process: {e}", folders=get_hcaptcha_folders())


def get_hcaptcha_folders():
    folder = "./hcaptcha"
    subfolders = [os.path.join(folder, dir) for dir in os.listdir(folder) if os.path.isdir(os.path.join(folder, dir))]
    return [os.path.basename(subfolder) for subfolder in subfolders]

if __name__ == "__main__":
    app.run(debug=True)
