import requests
import json
import re
import os

def extract_letters(response_content):
    return re.sub(r'[^a-zA-Z]', ' ', response_content).strip()

def upload_images_to_s3(images):
    upload_url = "https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/seanmabli/test3/dataset/upload/s3"
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

    merge_url = "https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/seanmabli/test3/dataset/upload/merge"
    merge_headers = {"upload_id": upload_id}
    return requests.get(merge_url, headers=merge_headers)

def upload_classes(classes):
    url = "https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/seanmabli/test3/dataset/classes"
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
    r = requests.get(url, headers=headers)  # Use GET to match fetch
    print(r.text)

def get_classes():
    url = "https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/seanmabli/test3"
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

def get_images():
    url = "https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/seanmabli/test3/dataset/view"
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

def get_chatgpt_response(class_name):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": f"Give me a 7-10 word highly accurate description of this object, dont use any weird words, keep the description simple: {class_name}"}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    if 'choices' in response_data and response_data['choices']:
        content = response_data["choices"][0]["message"]["content"].strip().lower()
        return extract_letters(content)
    else:
        return "No response found."

def auto_label():
    url = "https://fqk4k22rqc.execute-api.us-east-1.amazonaws.com/seanmabli/test3/dataset/autolabel"
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

    descriptions = [get_chatgpt_response(class_name) for class_name in get_classes()]

    body = {
        "images": "|".join(get_images()),
        "classes": "|".join(descriptions)
    }

    response = requests.post(url, headers=headers, json=body)
    return response.json()

def main():
    folder = "./hcaptcha"
    subfolders = [os.path.join(folder, dir) for dir in os.listdir(folder) if os.path.isdir(os.path.join(folder, dir))]
    print("Folders inside /hcaptcha:")
    for i, subfolder in enumerate(subfolders):
        print(f"{i+1}. {os.path.basename(subfolder)}")
    selected_folders = input("Enter the folders you want to upload: ")
    selected_folders = [subfolders[int(folder)-1].strip() for folder in selected_folders.split(",")]
    for folder in selected_folders:
        images = [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith(".png")]
        upload_images_to_s3(images)
    print("Images uploaded successfully.")
    
    print("Take a look at the images and define some classes for the auto-labeling.")
    classes = input("Enter the classes separated by commas: ").split(",")
    upload_classes(classes)
    
    print("Classes uploaded successfully.")
    print("Starting auto-labeling...")
    print(auto_label())

if __name__ == "__main__":
    main()
