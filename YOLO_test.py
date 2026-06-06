from ultralytics import YOLO
import cv2

model=YOLO('../YOLO-Weights/yolov8l.pt')
results=model("", show=True)

cv2.waitKey(0)