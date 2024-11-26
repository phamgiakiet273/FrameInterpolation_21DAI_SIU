# Capture and record a chosen Windows app

## Overview

This module captures frames from a Windows application selected by the user and saves the output as an FLV video file. The project also includes an optional API (`api.py`) and web-based viewer (`index.html`) for displaying the recorded video in real time.

- *Input:* A target Windows application's name chosen from a list of open windows.

- *Output:* A real-time FLV video file capturing the app's content.

## Features

- Captures frames at the application's native FPS or a user-defined rate.
- Dynamically adjusts the capture rate to match the app's performance (e.g., avoids sped up / slowed down recorded video).
- Writes frames directly to FFmpeg for real-time encoding, minimizing latency and resource usage.
- Optional API support for streaming the FLV file to a web interface.
- Web interface (`index.html`) supports playback via `FLV.js`.

## Requirements

To set up and run the project, install the following Python libraries using `pip`:

```bash
pip install -r requirements.txt
```

## How to use this module
Change path as need for variable in api.py (VIDEO_FILE) and record.py (OUTPUT_FILE). Open terminal and run
```python
record.py
 ```
If you want to observe streaming recorded video on web, open second terminal and run
```python
api.py
 ```
then access localhost:5000 (ex: http://127.0.0.1:5000) to observe
