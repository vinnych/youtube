from flask import Flask, request, send_file, jsonify
from yt_dlp import YoutubeDL
from flask import Flask, request, send_file, jsonify, render_template

import os
import tempfile

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/preview', methods=['POST'])
def preview():
    url = request.form['url']
    try:
        with YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
        return jsonify({
            'title': info.get('title'),
            'thumbnail': info.get('thumbnail'),
            'uploader': info.get('uploader'),
            'duration': info.get('duration')
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    quality = request.form['quality']

    # Create a temporary directory to store the video
    with tempfile.TemporaryDirectory() as tmpdir:
        # Use yt-dlp to download the video
        ydl_opts = {
            'format': f'bestvideo[height<={quality}]+bestaudio/best',
            'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s')
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url)
                filename = ydl.prepare_filename(info)  # full path to downloaded file

            # Send the file to the user's device with original video title
            return send_file(
                filename,
                as_attachment=True,
                download_name=f"{info['title']}.mp4"
            )
        except Exception as e:
            return f"Error: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)
