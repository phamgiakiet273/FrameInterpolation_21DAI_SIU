import os
import time
from flask import Flask, Response, render_template, send_from_directory

app = Flask(__name__)

VIDEO_FILE = '/workspace/projects/output.flv'  # Path to the ongoing FLV file
MP4_FILE = '/workspace/projects/test_anime.mp4'      # Path to the static MP4 file

def generate_video_stream():
    """Stream the FLV video file that is continuously being written."""
    with open(VIDEO_FILE, 'rb') as f:
        while True:
            chunk = f.read(1024)  # Read in chunks (adjust the size if needed)
            if chunk:
                yield chunk  # Yield the chunk to the client
            else:
                # No data available, so wait for new data
                time.sleep(0.1)  # Adjust to control the polling interval

@app.route('/stream_video')
def stream_video():
    """Endpoint that streams the FLV video."""
    return Response(generate_video_stream(), mimetype='video/x-flv')

@app.route('/test_video')
def test_video():
    """Serve the static MP4 video."""
    return send_from_directory(os.path.dirname(MP4_FILE), 'test_conveyor_15.mp4')

@app.route('/')
def index():
    """Render the HTML page with both FLV and MP4 players."""
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)
