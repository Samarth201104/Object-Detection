# from ultralytics import YOLO
# import cv2

# model = YOLO('../Yolo-Weights/yolov8l.pt')

# # Open video capture
# cap = cv2.VideoCapture('WhatsApp Video 2025-08-10 at 22.08.15.mp4')  # Replace 'your_video.mp4' with your video file

# while True:
#     ret, frame = cap.read()  # Read frame from video capture
#     if not ret:
#         break  # If no frame, break the loop
    
#     results = model(frame, show=False)  # Perform object detection on the frame

#     for result in results:
#         img = result.orig_img
#         names = result.names
#         results_prediction = result.boxes
#         cls = results_prediction.cls
#         conf = results_prediction.conf
#         xyxy = results_prediction.xyxy

#         for i in range(len(cls)):
#             classname = names[int(cls[i])] + ' ' + str(round(float(conf[i]), 2))
#             xyxys = xyxy[i]
#             st = (int(xyxys[0]), int(xyxys[1]))
#             end = (int(xyxys[2]), int(xyxys[3]))

#             img = cv2.putText(img, classname, st, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 10, 0), 2, cv2.LINE_AA)
#             img = cv2.rectangle(img, st, end, (200, 0, 0), 2)

#     cv2.imshow('Video', img)  # Display the frame with detections

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break  # Break the loop if 'q' key is pressed

# # Release the video capture and close all windows
# cap.release()
# cv2.destroyAllWindows()


# video.py (works for both video and image)
from ultralytics import YOLO
import cv2
import os

# Load YOLOv8 model
model = YOLO("yolov8l.pt")

def draw_boxes(frame, results):
    """Draw bounding boxes with black background and blue text"""
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            label = f"{model.names[cls]} {conf:.2f}"

            # Bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Blue box

            # Text background
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(frame, (x1, y1 - th - 5), (x1 + tw, y1), (0, 0, 0), -1)  # Black rectangle
            cv2.putText(frame, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)  # Blue text
    return frame


def process_image(image_path):
    frame = cv2.imread(image_path)
    results = model(frame, stream=True)
    frame = draw_boxes(frame, results)
    cv2.imshow("YOLOv8 Image", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, stream=True)
        frame = draw_boxes(frame, results)

        cv2.imshow("YOLOv8 Video", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    path = r"D:\object detection2\static\uploads\WhatsApp Video 2025-08-10 at 22.08.15.mp4"  # Change to your file (image or video)

    if not os.path.exists(path):
        print("File not found:", path)
    else:
        # Check if it's image or video
        ext = os.path.splitext(path)[-1].lower()
        if ext in [".jpg", ".jpeg", ".png", ".bmp"]:
            process_image(path)
        else:
            process_video(path)
