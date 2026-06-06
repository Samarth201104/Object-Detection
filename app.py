from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import os
import cv2
import base64
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load YOLOv8 model
model = YOLO('../Yolo-Weights/yolov8l.pt')

# ---------------------------
# Home page
# ---------------------------
@app.route('/')
def index():
    return render_template('index.html')

# ---------------------------
# Detection API
# ---------------------------
@app.route('/detect', methods=['POST'])
def detect():
    mode = request.form.get('mode')  # "image", "video", "webcam"
    file = request.files.get('file')

    if mode == 'image' and file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Run YOLO inference on image
        results = model(filepath)[0]
        detections = []
        for box, cls, score in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
            detections.append({
                "bbox": box.tolist(),
                "class": model.names[int(cls)],
                "score": float(score)
            })

        # Encode image with boxes for frontend preview
        img = cv2.imread(filepath)
        for d in detections:
            x1, y1, x2, y2 = map(int, d["bbox"])
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f'{d["class"]} {d["score"]:.2f}', (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        _, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify(detections=detections, image=f"data:image/jpeg;base64,{img_base64}")

    elif mode == 'video' and file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Here, you can handle video frame-by-frame inference and save as output video
        # For simplicity, we just return a success message
        return jsonify({"message": "Video uploaded. YOLO inference can be run frame-by-frame."})

    elif mode == 'webcam':
        # Receive webcam frame in base64
        frame_data = request.form.get('frame')
        if frame_data:
            # Decode base64
            frame_data = frame_data.split(',')[1]
            img_bytes = base64.b64decode(frame_data)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # YOLO inference
            results = model(img)[0]
            detections = []
            for box, cls, score in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
                detections.append({
                    "bbox": box.tolist(),
                    "class": model.names[int(cls)],
                    "score": float(score)
                })

            # Draw boxes
            for d in detections:
                x1, y1, x2, y2 = map(int, d["bbox"])
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, f'{d["class"]} {d["score"]:.2f}', (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

            _, buffer = cv2.imencode('.jpg', img)
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            return jsonify(detections=detections, image=f"data:image/jpeg;base64,{img_base64}")

    return jsonify({"error": "No file or invalid mode"}), 400

# ---------------------------
# Run app
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
