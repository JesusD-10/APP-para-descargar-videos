from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
import os
import uuid
import yt_dlp
from yt_dlp.utils import DownloadError

app = Flask(__name__)
app.secret_key = "clave_segura"
DOWNLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_with_ytdlp(url: str, output_dir: str) -> str:
    unique_id = str(uuid.uuid4())[:8]
    outtmpl = os.path.join(output_dir, f"{unique_id}-%(title).50s.%(ext)s")

    ydl_opts = {
        'outtmpl': outtmpl,
        'format': 'bestvideo+bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if not url:
            flash("Por favor ingresa una URL válida.")
            return redirect(url_for("index"))

        try:
            filepath = download_with_ytdlp(url, DOWNLOAD_FOLDER)
            filename = os.path.basename(filepath)
            return render_template("result.html", filename=filename)

        except DownloadError as e:
            flash(f"Error al descargar: {str(e)}")
            return redirect(url_for("index"))

        except Exception as e:
            flash(f"Ocurrió un error inesperado: {str(e)}")
            return redirect(url_for("index"))

    return render_template("index.html")

@app.route("/downloads/<path:filename>")
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


