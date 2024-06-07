from hcaptcha_image_scraper import HcaptchaImagesDownloader
from auto_train import DataUploader
import time
import os
import time

def main(username, repository):
    folder = "./hcaptcha"
    capdl = HcaptchaImagesDownloader()

    for _ in range(1000):
        capdl.download_images()

    time.sleep(3)

    subfolders = [os.path.join(folder, dir) for dir in os.listdir(folder) if os.path.isdir(os.path.join(folder, dir))]
    print("Folders inside /hcaptcha:")
    for i, subfolder in enumerate(subfolders):
        print(f"{i+1}. {os.path.basename(subfolder)}")
    selected_folders = input("Enter the folders you want to upload: ")
    selected_folders = [subfolders[int(folder)-1].strip() for folder in selected_folders.split(",")]
    for folder in selected_folders:
        images = [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith(".png")]
        uploader = DataUploader()
        uploader.upload_images_to_s3(images, username, repository)
        time.sleep(3)
        print("Images uploaded successfully.")

        time.sleep(3)
        
        print("Take a look at the images and define some classes for the auto-labeling.")
        classes = input("Enter the classes separated by commas:").split(",")
        classes = [c.replace(" ", "") for c in classes]

        uploader.upload_classes(classes, username, repository)
        
        time.sleep(3)

        print("Classes uploaded successfully.")
        print("Starting auto-labeling...")
        print(uploader.auto_label(username, repository))

    # At some point we should check if the auto-labeling is done but idk how
    
if __name__ == "__main__":
    username = input("Enter your username: ")
    repository = input("Enter your repository: ")
    main(username, repository)