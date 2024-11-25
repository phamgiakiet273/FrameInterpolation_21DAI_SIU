import sys
import vapoursynth as vs
sys.path.append("/workspace/tensorrt/")

from src.rife_trt import rife_trt
core = vs.core
core.num_threads = 16

core.std.LoadPlugin(path="/usr/local/lib/libvstrt.so")


import subprocess
def encode(clip: vs.VideoNode, filename: str) -> None:
    ffmpeg_args = ['ffmpeg', '-i', 'pipe:', '-c:v', 'h264_nvenc', '-preset', 'fast', filename]
    enc_proc = subprocess.Popen(ffmpeg_args, stdin=subprocess.PIPE, bufsize=10**8)
    clip.output(enc_proc.stdin, y4m=bool(clip.format.color_family == vs.YUV))
    enc_proc.communicate()

def inference_clip(video_path):
    clip = core.bs.VideoSource(source=video_path)

    clip = core.resize.Bicubic(
        clip, format=vs.RGBH, matrix_in_s="709"
    )  # RGBS means fp32, RGBH means fp16

    # interpolation
    clip = rife_trt(
        clip,
        multi=2,
    scale=1.0,
    device_id=0,
    num_streams=2,
    engine_path="/workspace/projects/model.engine",  # read readme on how to build engine
    )

    clip = core.resize.Bicubic(clip, format=vs.YUV420P8, matrix_s="709")
    return clip

encode(inference_clip('test_default_15.mp4'),'output.flv')