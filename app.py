from flask import Flask, render_template, request, redirect, url_for, flash
import os
import yt_dlp
import instaloader
import requests

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a random secure string

# Ensure the output folder exists
OUTPUT_FOLDER = "downloads"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    try:
        platform = request.form.get("platform")
        url = request.form.get("url")
        quality = request.form.get("quality", "720")  # Default quality is 720p

        if not url:
            flash("URL is required!", "error")
            return redirect(url_for("home"))

        if platform == "youtube":
            download_youtube_video(url, OUTPUT_FOLDER, quality)
            flash("YouTube video downloaded successfully!", "success")
        elif platform == "instagram":
            download_instagram_post(url, OUTPUT_FOLDER)
            flash("Instagram post downloaded successfully!", "success")
        elif platform == "facebook":
            download_facebook_video(url, OUTPUT_FOLDER)
            flash("Facebook video downloaded successfully!", "success")
        else:
            flash("Invalid platform selected!", "error")
    except Exception as e:
        flash(f"Error: {e}", "error")
    
    return redirect(url_for("home"))

def download_youtube_video(url, output_folder, quality):
    ydl_opts = {
        "format": f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]",
        "outtmpl": f"{output_folder}/%(title)s.%(ext)s",
        "merge_output_format": "mp4",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_instagram_post(url, output_folder):
    loader = instaloader.Instaloader(download_videos=True, save_metadata=False, post_metadata_txt_pattern="")
    post = instaloader.Post.from_shortcode(loader.context, url.split("/")[-2])
    loader.download_post(post, target=output_folder)

def download_facebook_video(url, output_folder):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers, stream=True)
    if response.status_code == 200:
        video_name = os.path.join(output_folder, "facebook_video.mp4")
        with open(video_name, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
    else:
        raise Exception("Failed to fetch the video. Ensure the URL is valid and public.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
