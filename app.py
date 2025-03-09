import os
import yt_dlp
from flask import Flask, render_template, request, jsonify, send_from_directory
from google.generativeai import GenerativeModel, configure

# Initialize Flask app
app = Flask(__name__)

# Set up Google Generative AI
API_KEY = "AIzaSyBXOwvBdob80p0huFB15ggLsLtEwp_z2rM"  # Replace with your actual API key
configure(api_key=API_KEY)
model = GenerativeModel("gemini-1.5-pro")

# Ensure download directory exists
DOWNLOAD_FOLDER = "static/downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
app.config["DOWNLOAD_FOLDER"] = DOWNLOAD_FOLDER

# YouTube Bot Instructions for AI-Powered Recommendations
YOUTUBE_BOT_PROMPT ='''You are an AI assistant that recommends the best YouTube videos based on user queries.
Your responses must be structured, concise, and include clickable links.

### Response Format:
1. List 3-5 videoswith:
   - Title
   - Brief description (1-2 sentences)
   - Clickable YouTube links

2.Structured Output Example: 📌 Video Title 🔗 Watch Here
3. Learning Path (if applicable): Suggest progression from beginner to advanced.

Always provide hyperlinks only in the YouTube links.'''


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recommend", methods=["POST"])
def recommend_videos():
    user_query = request.json.get("query")
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        response = model.generate_content(f"{YOUTUBE_BOT_PROMPT}\n\nUser Query: {user_query}")
        return jsonify({"recommendations": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["POST"])
def download_video():
    video_url = request.json.get("url")
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        ydl_opts = {
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
            "format": "best",
            "cookiefile": "cookies.txt"  # Use cookies to bypass restrictions
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            file_path = os.path.basename(filename)

        return jsonify({
            "message": "Download successful!",
            "file_url": f"/downloaded/{file_path}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/downloaded/<filename>")
def downloaded_file(filename):
    return send_from_directory(app.config["DOWNLOAD_FOLDER"], filename, as_attachment=True)

@app.route("/generate_highlights", methods=["POST"])
def generate_highlights():
    video_url = request.json.get("url")
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Extract video transcript using yt_dlp
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en"],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            subtitles = info.get("subtitles", {}).get("en", [])
            auto_subtitles = info.get("automatic_captions", {}).get("en", [])

            transcript_url = None
            if subtitles:
                transcript_url = subtitles[0].get("url")
            elif auto_subtitles:
                transcript_url = auto_subtitles[0].get("url")

        if not transcript_url:
            return jsonify({"error": "No transcript available for this video."}), 400

        # Send the transcript URL to Gemini AI
        prompt = f"""
        You are an AI assistant that extracts **key highlights** from YouTube videos.

        **Video URL:** {video_url}  
        **Transcript URL:** {transcript_url}  

        Based on the transcript, summarize the **top 5 key moments** from this video.
        Format the response in **bullet points**.
        """

        response = model.generate_content(prompt)

        return jsonify({
            "message": "Highlights generated!",
            "highlights": response.text.strip()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
