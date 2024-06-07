import requests
import json
import os

class DataUploader:
    def __init__(self, username, repository):
        self.username = username
        self.repository = repository
        self.base_url = f"https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/{self.username}/{self.repository}"

    def upload_images_to_s3(self, images):
        upload_url = f"{self.base_url}/dataset/upload/s3"
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

        files = [os.path.basename(image) for image in images]
        body = json.dumps({"files": files })

        response = requests.post(upload_url, headers=headers, data=body)
        response_json = response.json()

        s3_urls = response_json["presigned_urls"]
        upload_id = response_json["upload_id"]

        upload_headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "image/png",
            "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "sec-gpc": "1"
        }

        for s3_url_index in range(len(s3_urls)):
            with open(images[s3_url_index], 'rb') as file:
                file_content = file.read()
            requests.put(s3_urls[s3_url_index], headers=upload_headers, data=file_content)

        merge_url = f"{self.base_url}/dataset/upload/merge"
        merge_headers = {"upload_id": upload_id}
        return requests.get(merge_url, headers=merge_headers)

    def upload_classes(self, classes):
        url = f"{self.base_url}/dataset/classes"
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
        r = requests.get(url, headers=headers)
        print(r.text)

    def get_classes(self):
        url = f"{self.base_url}"
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

    def get_images(self):
        url = f"{self.base_url}/dataset/view"
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

    def auto_label(self):
        url = f"{self.base_url}/dataset/autolabel"
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
            "images": "|".join(self.get_images()),
            "classes": "|".join([class_name for class_name in self.get_classes()])
        }

        response_autolabel = requests.post(url, headers=headers, json=body)

        return response_autolabel.json()
            
    def auto_train(self):
        url = f"{self.base_url}/models/train" 
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
