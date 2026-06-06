# Object Detection Project

This repository contains scripts for running object detection using YOLO models and other utilities for processing images, video files, and webcam streams.

## Project structure

- `app.py` - (main) Flask or app entrypoint (if present).
- `images.py` - image-processing helper scripts.
- `video.py`, `YOLO_Video.py` - video processing / detection pipelines.
- `webcam.py`, `YOLOv8_Webcam.py` - run detection on webcam streams.
- `YOLO_test.py` - test/experiment scripts.
- `model/` - contains model files and class labels (e.g., `yolov8l.pt`, `frozen_inference_graph.pb`).
- `static/`, `templates/` - web UI assets and templates.
- `uploads/`, `detections/` - input uploads and output detections.

## Prerequisites

- Python 3.8 or newer
- A virtual environment is recommended

Install common dependencies (example):

```bash
python -m venv venv
venv\Scripts\activate    # Windows
pip install --upgrade pip
pip install -r requirements.txt  # if available
# Example packages you may need:
pip install ultralytics opencv-python flask torch torchvision
```

If there is no `requirements.txt`, install the packages shown above as needed.

## Usage

- Run the web app (if `app.py` is the Flask app):

```bash
python app.py
```

- Run webcam detection:

```bash
python webcam.py
# or
python YOLOv8_Webcam.py
```

- Run video detection:

```bash
python YOLO_Video.py
python video.py
```

Model files (for example `yolov8l.pt`) are provided in the project root and in `model/`. Ensure the code points to the correct model path before running.

## Notes

- This project appears to use YOLO-based models. Adjust device (CPU/GPU) and model paths in the scripts if necessary.
- If you want, I can generate a `requirements.txt` by scanning the code for imports.

## License

Add a license as appropriate for your project.
# Object-Detection
New Repo
