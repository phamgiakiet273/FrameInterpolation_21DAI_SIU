# FrameInterpolation_21DAI_SIU

## Description

Academic project for Computer Vision: Real-time Frame Interpolation for Videos and Applications. This project entails streaming videos and applications from local storage and interpolation methods can be applied. The interpolation method deployed is RIFE combined with Frame Deduplication and Scene Boundary Detection. RIFE models are optimized and convert to ONNX and ENGINE format using NVIDIA TensorRT pipeline, achieving near real-time performance.

## Getting Started

### Dependencies
* Windows / Linux
* Python 3.9.20
* ffmpeg
* Docker

# Installing for Windows
* Install Windows Subsystem for Linux (WSL)
* Install Docker Desktop
* Install FFMPEG and add to PATH
* Set up [VSGAN Docker](https://github.com/styler00dollar/VSGAN-tensorrt-docker?tab=readme-ov-file), but do not run yet.
*
```
git clone https://github.com/phamgiakiet273/FrameInterpolation_21DAI_SIU
```
* Replace compose.yaml with the one in this Git
* Download [FFMPEG for Linux](https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz) and unzip to docker_mount/project
* Replace the volume mount in compose.yaml with your actual directory
* 
```
git clone https://github.com/phamgiakiet273/FrameInterpolation_21DAI_SIU
```
* docker-compose run --rm vsgan_tensorrt
* Attach docker container to VSCode using Dev Container and set up FFMPEG according to instruction inside ffmpeg_setup.txt
