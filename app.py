from flask import Flask, render_template, request, jsonify, send_from_directory
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():
    try:
        url = request.form.get("url") or request.json.get("url")
        if not url:
            return jsonify({"success": False, "error": "No URL provided"}), 400

        options = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": True,
            "no_warnings": True,
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)

        # Determine mp3 filename
        if info.get("requested_downloads"):
            downloaded_filepath = info["requested_downloads"][0].get("filepath")
        else:
            downloaded_filepath = ydl.prepare_filename(info)

        mp3_path = os.path.splitext(downloaded_filepath)[0] + ".mp3"
        if not os.path.isfile(mp3_path):
            return jsonify({"success": False, "error": f"MP3 not found: {mp3_path}"}), 500

        filename = os.path.basename(mp3_path)
        return jsonify({"success": True, "filename": filename})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/files/<path:filename>")
def get_file(filename):
    return send_from_directory(
        DOWNLOAD_FOLDER,
        filename,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)
