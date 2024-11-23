import time
import os
from flask import Flask, Response, render_template

app = Flask(__name__)

# Path to the FLV video file being recorded
VIDEO_FILE = r"C:\Users\F14_TOMCAT\Downloads\GIAO_TRINH\ComputerVision\FrameInterpolation_21DAI_SIU\FrameRender\output.flv"

def generate_video_stream():
    """Stream the FLV video file that is continuously being written."""
    with open(VIDEO_FILE, 'rb') as f:
        # Read and send the FLV header first
        header = f.read(9)  # FLV header is typically 9 bytes
        yield header

        last_position = f.tell()
        last_check = time.time()
        current_size = os.stat(VIDEO_FILE).st_size

        while True:
            # Get the current file size
            if time.time() - last_check > 0.1:  # Check every 100ms
                current_size = os.stat(VIDEO_FILE).st_size
                last_check = time.time()

            if last_position < current_size:
                # Read new data from the current position
                f.seek(last_position)
                chunk = f.read(4096)  # Read in KB chunks
                if chunk:
                    yield chunk
                    last_position = f.tell()
            else:
                # No new data; wait briefly before checking again
                time.sleep(0.01)  # Shorter polling interval for better responsiveness

@app.route('/stream_video')
def stream_video():
    """Endpoint that streams the FLV video."""
    return Response(generate_video_stream(), mimetype='video/x-flv')

@app.route('/')
def index():
    """Render the HTML page with the FLV player."""
    return render_template('index.html')  # Ensure this file has a player for FLV

if __name__ == "__main__":
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)
