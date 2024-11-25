import time
from flask import Flask, Response, render_template, request, jsonify, send_file, send_from_directory
import os
from flask_cors import CORS
# import cv2
import subprocess
import json
import threading

import sys
import vapoursynth as vs
sys.path.append("/workspace/tensorrt/")

from src.rife_trt import rife_trt
from src.scene_detect import scene_detect
core = vs.core
core.num_threads = 16

core.std.LoadPlugin(path="/usr/local/lib/libvstrt.so")

encoding_done = threading.Event()

def encode(clip: vs.VideoNode, filename: str) -> None:
    ffmpeg_args = ['ffmpeg', '-i', 'pipe:', '-c:v', 'libx264', '-preset', 'ultrafast', filename]
    enc_proc = subprocess.Popen(ffmpeg_args, stdin=subprocess.PIPE, bufsize=10**8)
    clip.output(enc_proc.stdin, y4m=bool(clip.format.color_family == vs.YUV))
    enc_proc.communicate()
    encoding_done.set()


def inference_clip_default(video_path, interpolation_scale=2):
    clip = core.bs.VideoSource(source=video_path)

    clip = core.resize.Bicubic(
        clip, format=vs.RGBH, matrix_in_s="709"
    )  # RGBS means fp32, RGBH means fp16

    # interpolation
    clip = rife_trt(
        clip,
        multi=interpolation_scale,
        scale=1.0,
        device_id=0,
        num_streams=2,
        engine_path="/workspace/projects/model.engine",  # read readme on how to build engine
    )

    clip = core.resize.Bicubic(clip, format=vs.YUV420P8, matrix_s="709")
    return clip

# calculate metrics
def metrics_func_scene(clip):
    offs1 = core.std.BlankClip(clip, length=1) + clip[:-1]
    offs1 = core.std.CopyFrameProps(offs1, clip)
    return core.vmaf.Metric(clip, offs1, 2)

# calculate metrics
def metrics_func_dedup(clip):
    offs1 = core.std.BlankClip(clip, length=1) + clip[:-1]
    offs1 = core.std.CopyFrameProps(offs1, clip)
    return core.vmaf.Metric(clip, offs1, 3)


def inference_clip_scene(video_path, interpolation_scale=2):
    clip = core.bs.VideoSource(source=video_path)

    clip = core.resize.Bicubic(
        clip, format=vs.RGBH, matrix_in_s="709"
    )  # RGBS means fp32, RGBH means fp16

    clip_orig = core.std.Interleave([clip] * interpolation_scale)  # 2 means interpolation factor here

    clip_sc = scene_detect(
        clip,
        fp16=True,
        thresh=0.5,
        model=3,
    )

    clip = rife_trt(
        clip,
        multi=interpolation_scale,
        scale=1.0,
        device_id=0,
        num_streams=2,
        engine_path="/workspace/projects/model.engine"
    )

    clip = core.akarin.Select([clip, clip_orig], clip_sc, "x._SceneChangeNext 1 0 ?")
    
    clip = core.resize.Bicubic(clip, format=vs.YUV420P8, matrix_s="709")
    return clip

def inference_clip_dedup(video_path, interpolation_scale=2):
    clip = core.bs.VideoSource(source=video_path)

    clip = core.resize.Bicubic(
        clip, format=vs.RGBH, matrix_in_s="709"
    )  # RGBS means fp32, RGBH means fp16

    # ssim
    clip_metric = vs.core.resize.Bicubic(
        clip, width=224, height=224, format=vs.YUV420P8, matrix_s="709"  # resize before ssim for speedup
    )
    clip_metric = metrics_func_dedup(clip_metric)
    clip_orig = core.std.Interleave([clip] * interpolation_scale)

    # interpolation
    clip = rife_trt(
        clip,
        multi=interpolation_scale,
        scale=1.0,
        device_id=0,
        num_streams=2,
        engine_path="/workspace/projects/model.engine",
    )

    # skip frames based on calculated metrics
    # in this case if ssim > 0.999, then copy frame
    clip = core.akarin.Select([clip, clip_orig], clip_metric, "x.float_ssim 0.999 >")
    clip = core.resize.Bicubic(clip, format=vs.YUV420P8, matrix_s="709")
    return clip

app = Flask(__name__)
CORS(app)

def get_video_metadata(video_path):
    try:
        # Run ffprobe to extract video metadata in JSON format
        command = [
            "ffprobe", 
            "-v", "error", 
            "-select_streams", "v:0", 
            "-show_entries", "stream=width,height,avg_frame_rate,r_frame_rate,duration,nb_frames", 
            "-of", "json", 
            video_path
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Parse the output
        metadata = json.loads(result.stdout)
        
        # Extract relevant fields
        stream = metadata.get("streams", [{}])[0]
        width = stream.get("width", 0)
        height = stream.get("height", 0)
        avg_frame_rate = stream.get("avg_frame_rate", "0/0")
        nb_frames = int(stream.get("nb_frames", 0))
        duration = float(stream.get("duration", 0))
        
        # Calculate FPS
        num, den = map(int, avg_frame_rate.split('/')) if '/' in avg_frame_rate else (0, 1)
        fps = num / den if den != 0 else 0
        
        return {
            "fps": fps,
            "frame_count": nb_frames,
            "duration": duration,
            "resolution": f"{width}x{height}"
        }
    except Exception as e:
        return {"error": str(e)}

@app.route('/metadata', methods=['GET'])
def video_metadata():
    """Endpoint trả về thông tin metadata của video."""
    # Nhận tham số từ query string
    video_type = request.args.get('type', 'input')  # Mặc định là "input"
    
    # Xác định đường dẫn tệp dựa trên loại video
    if video_type == 'input':
        file_path = 'process/input.mp4'
    elif video_type == 'output':
        time.sleep(1)
        file_path = 'process/output.flv'
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


    # Define the paths to the input and output files
    input_file_path = os.path.join('process', 'input.mp4')
    output_file_path = os.path.join('process', 'output.flv')

    # Delete existing input and output files if they exist
    if os.path.exists(input_file_path):
        os.remove(input_file_path)
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    # Tạo tên file mới là inp.<đuôi>
    new_filename = 'input.mp4'
    file_path = os.path.join('process/', new_filename)

    # Lưu file
    file.save(file_path)

    return jsonify({"message": "File uploaded successfully!", "saved_as": new_filename})
    


@app.route('/process')
def process():
    fps = request.args.get('fps', 'x2')  # Default là x2
    mode = request.args.get('mode', 'default')  # Default là default


    print(fps)
    print(mode)

    # Đường dẫn tệp
    input_file = 'process/input.mp4'

    # Kiểm tra sự tồn tại của file đầu vào
    if not os.path.exists(input_file):
        return jsonify({"error": "File đầu vào không tồn tại!"}), 400

    # Logic xử lý video sẽ được triển khai tại đây

    interpolation_scale = int(fps[-1])

    clip_result = None

    if mode=='default':
        clip_result = inference_clip_default(input_file, interpolation_scale)
    elif mode=='frame':
        clip_result = inference_clip_dedup(input_file, interpolation_scale)
    elif mode=='scene':
        clip_result = inference_clip_scene(input_file, interpolation_scale)

    global encoding_done
    encoding_done.clear()

    thread = threading.Thread(target=encode, args=(clip_result,'process/output.flv'))
    thread.start()
    
    time.sleep(1)

    # Hiện chỉ trả về thông báo xử lý thành công
    return jsonify({
        "message": "Xử lý video thành công!",
        "fps": fps,
        "mode": mode
    })



def generate_video_stream():
    """Stream the FLV video file that is continuously being written."""
    global encoding_done
    with open('process/output.flv', 'rb') as f:
        while not encoding_done.is_set():  # Check if encoding is done
            chunk = f.read(32)
            if chunk:
                yield chunk
            else:
                time.sleep(0.1)
        
        # Stream remaining data after encoding is done
        while True:
            chunk = f.read(32)
            if chunk:
                yield chunk
            else:
                break  # Exit loop when no more data is available


@app.route('/stream_video')
def stream_video():
    """Endpoint that streams the FLV video."""
    response = Response(generate_video_stream(), content_type='video/x-flv')
    return response

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)