from flask import Flask, render_template, request, render_template_string, session
from hcaptcha_image_scraper import HcaptchaImagesDownloader
from auto_train import DataUploader
import json
import os
import requests

app = Flask(__name__)
app.secret_key = "superhackerkey1234"

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
    return render_template('index.html', alert="")

@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    try:
        username = "alfred"
        folder = "./hcaptcha"
        """
        capdl = HcaptchaImagesDownloader()

        #for _ in range(1):
        #    capdl.download_images()
        
        """
        repository_name = [os.path.basename(os.path.join(folder, dir)) for dir in os.listdir(folder) if os.path.isdir(os.path.join(folder, dir))]
        """
        subfolders = [os.path.join(folder, dir) for dir in os.listdir(folder) if os.path.isdir(os.path.join(folder, dir))]
        
        for folder in subfolders:
            repository = create_repository(repository_name[subfolders.index(folder)].replace(" ", "_"))
            images = [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith(".png")]
            uploader = DataUploader(username, repository)
            uploader.upload_images_to_s3(images)
        """
        return render_template('index.html', alert="Scraping and uploading completed successfully", options=repository_name)
    except Exception as e:
        print(f"An error occurred during the process: {e}")
        return render_template('index.html', alert=f"An error occurred during the process: {e}")

@app.route('/train_model', methods=['POST'])
def train_model():
    options = session.get('options')
    print("Original options:", options)
    def handle_data(option):
        options = session.get('options')
        print("Original options:", options)
        if option in options:
            options.remove(option)
        session['options'] = options
        print("Updated options:", options)
        return options

    def upload_classes(classes, selected_option):
        classes = classes.split(",")
        url = f"https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/alfred/{selected_option.replace(' ', '_')}/dataset/classes"
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
    
    selected_option = request.form.get('options')
    classes = request.form.get('classes')
    
    print("Selected Option:", selected_option)
    print("Classes:", classes)
    
    upload_classes(classes, selected_option)
    
    remaining_options = handle_data(selected_option)
    
    print("Remaining Options:", remaining_options)

    if not remaining_options:
        auto_label()
    return render_template('index.html', options=remaining_options, alert="Model training completed successfully")

if __name__ == "__main__":
    app.run(debug=True)