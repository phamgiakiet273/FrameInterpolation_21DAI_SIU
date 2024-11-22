import time
from flask import Flask, Response, render_template, request, jsonify, send_file, send_from_directory
import os
import cv2

app = Flask(__name__)

def get_video_metadata(video_path):
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        return {"error": "Không thể mở file video!"}
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video.release()
    return {
        "fps": fps,
        "frame_count": frame_count,
        "duration": duration,
        "resolution": f"{width}x{height}"
    }

@app.route('/metadata', methods=['GET'])
def video_metadata():
    """Endpoint trả về thông tin metadata của video."""
    # Nhận tham số từ query string
    video_type = request.args.get('type', 'input')  # Mặc định là "input"
    
    # Xác định đường dẫn tệp dựa trên loại video
    if video_type == 'input':
        file_path = 'E:\\School\\CV\\Project\\API\\input\\inp.mp4'
    elif video_type == 'output':
        file_path = 'E:\\School\\CV\\Project\\API\\output\\out.flv'
    else:
        return jsonify({"error": "Loại video không hợp lệ! Chỉ chấp nhận 'input' hoặc 'output'."}), 400

    # Kiểm tra tệp có tồn tại không
    if not os.path.exists(file_path):
        return jsonify({"error": f"File {video_type} không tồn tại!"}), 404

    # Lấy metadata từ video
    metadata = get_video_metadata(file_path)
    if "error" in metadata:
        return jsonify({"error": metadata["error"]}), 500

    return jsonify(metadata)


@app.route('/')
def index():
    """Render the HTML page with both FLV and MP4 players."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 200

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 200

    # Tạo tên file mới là inp.<đuôi>
    new_filename = 'inp.mp4'
    file_path = os.path.join('E:\\School\\CV\\Project\\API\\input', new_filename)

    # Lưu file
    file.save(file_path)

    return jsonify({"message": "File uploaded successfully!", "saved_as": new_filename})
    
@app.route('/process')
def process():
    fps = request.args.get('fps', 'x2')  # Default là x2
    mode = request.args.get('mode', 'default')  # Default là default

    # Đường dẫn tệp
    input_file = 'E:\\School\\CV\\Project\\API\\input\\inp.mp4'

    # Kiểm tra sự tồn tại của file đầu vào
    if not os.path.exists(input_file):
        return jsonify({"error": "File đầu vào không tồn tại!"}), 400

    # Logic xử lý video sẽ được triển khai tại đây
    # Hiện chỉ trả về thông báo xử lý thành công
    return jsonify({
        "message": "Xử lý video thành công!",
        "fps": fps,
        "mode": mode
    })



def generate_video_stream():
    """Stream the FLV video file that is continuously being written."""
    with open('E:\\School\\CV\\Project\\API\\output\\output.flv', 'rb') as f:
        while True:
            chunk = f.read(1024)
            if chunk:
                yield chunk 
            else:
                time.sleep(0.1)  

@app.route('/stream_video')
def stream_video():
    """Endpoint that streams the FLV video."""
    return Response(generate_video_stream(), mimetype='video/x-flv')

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
