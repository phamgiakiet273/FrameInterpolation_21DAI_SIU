import time
from flask import Flask, Response, render_template

app = Flask(__name__)

# Path to the FLV video file being recorded
VIDEO_FILE = r"C:\Users\F14_TOMCAT\Downloads\GIAO_TRINH\ComputerVision\FrameInterpolation_21DAI_SIU\FrameRender\output.flv"

def generate_video_stream():
    """Stream the FLV video file that is continuously being written."""
    with open(VIDEO_FILE, 'rb') as f:
        while True:
            chunk = f.read(1024)  # Read in 1 KB chunks
            if chunk:
                yield chunk  # Send chunk to client
            else:
                # No new data; wait for additional data
                time.sleep(0.02)  # Adjust polling interval for responsiveness

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
