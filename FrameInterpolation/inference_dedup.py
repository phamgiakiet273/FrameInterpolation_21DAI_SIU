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

# calculate metrics
def metrics_func(clip):
    offs1 = core.std.BlankClip(clip, length=1) + clip[:-1]
    offs1 = core.std.CopyFrameProps(offs1, clip)
    return core.vmaf.Metric(clip, offs1, 3)

def inference_clip(video_path):
    interp_scale = 2
    clip = core.bs.VideoSource(source=video_path)

    clip = core.resize.Bicubic(
        clip, format=vs.RGBH, matrix_in_s="709"
    )  # RGBS means fp32, RGBH means fp16

    # ssim
    clip_metric = vs.core.resize.Bicubic(
        clip, width=224, height=224, format=vs.YUV420P8, matrix_s="709"  # resize before ssim for speedup
    )
    clip_metric = metrics_func(clip_metric)
    clip_orig = core.std.Interleave([clip] * interp_scale)

    # interpolation
    clip = rife_trt(
        clip,
        multi=interp_scale,
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

encode(inference_clip('test.mp4'),'output.flv')