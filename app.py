from flask import Flask, render_template, request, send_file
from serpapi import GoogleSearch
import urllib.request
import os
import zipfile
from datetime import datetime
import shutil

app = Flask(__name__)

API_KEY = "3087d64f86ebe69180b0cf749d16ad4fc3dfbccd28edbbbf18c78ca676385d4a"

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    thumbnails = []
    zip_path = None

    if request.method == "POST":
        person_name = request.form.get("keyword")
        if person_name:
            # create folders
            folder_name = person_name.replace(" ", "_")
            out_dir = os.path.join("static", folder_name)
            os.makedirs(out_dir, exist_ok=True)

            # search images
            params = {
                "engine": "google_images",
                "q": person_name,
                "ijn": "0",
                "api_key": API_KEY
            }

            search = GoogleSearch(params)
            results = search.get_dict()
            images = results.get("images_results", [])

            for i, img in enumerate(images):
                url = img.get("original") or img.get("thumbnail")
                if not url:
                    continue
                ext = os.path.splitext(url)[1].split("?")[0] or ".jpg"
                filename = os.path.join(out_dir, f"{i}{ext}")
                try:
                    urllib.request.urlretrieve(url, filename)
                    thumbnails.append(f"{folder_name}/{i}{ext}")
                except:
                    continue

            # create ZIP for download
            zip_filename = f"{folder_name}.zip"
            zip_path = os.path.join("static", "downloads", zip_filename)
            os.makedirs(os.path.dirname(zip_path), exist_ok=True)
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, _, files in os.walk(out_dir):
                    for file in files:
                        zipf.write(os.path.join(root, file),
                                   arcname=file)

            message = f"✅ Downloaded {len(thumbnails)} images for {person_name}"

        else:
            message = "⚠️ Please enter a name"

    return render_template("index.html", message=message, thumbnails=thumbnails, zip_path=zip_path, current_year=datetime.now().year)

@app.route("/download/<path:filename>")
def download(filename):
    return send_file(os.path.join("static", "downloads", filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
