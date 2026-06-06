# import cv2 
# import matplotlib.pyplot as plt
# frozen_model = r'static\model\frozen_inference_graph.pb'

# config_file = r"static\model\ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
# model = cv2.dnn_DetectionModel(frozen_model, config_file)

# classLabels = []
# file_name = r'static\model\ssd_classes.txt'

# with open(file_name,'rt') as fpt:
#     classLabels = fpt.read().rstrip('\n').split('\n')
# print(classLabels)

# print(len(classLabels))
# model.setInputSize(320,320)
# model.setInputScale((1.0/127.5))
# model.setInputMean((127.5,127,5,127.5))
# model.setInputSwapRB(True)


# path = 0

# cap=cv2.VideoCapture(path)
# if not cap.isOpened():
#     cap=cv2.VideoCapture(0)
# if not cap.isOpened():
#     raise IOError("Can't open the video ")

# font_scale= 0.7
# font= cv2.FONT_HERSHEY_SIMPLEX
# while True:
#     ret,frame=cap.read()
#     ClassIndex, confidence, bbox= model.detect(frame,confThreshold=0.55)
#     print(ClassIndex)
#     if(len(ClassIndex)!=0): 
#         for ClassInd, conf, boxes in zip(ClassIndex.flatten(),confidence.flatten(),bbox):
#             print(ClassInd)
#             # if(ClassInd<=80):/
#             cv2.rectangle(frame, boxes,(200,0,0),2)
#             cv2.putText(frame,classLabels[ClassInd-1]+'-'+str(conf),(boxes[0]+10,boxes[1]+30),font,fontScale = font_scale,color=(0,10,0),thickness=2)

#     cv2.imshow('objdetection by simplilearn',frame)
#     if cv2.waitKey(2) & 0xff == ord('q'):
#        break

# cap.release()
# cv2.destroyAllWindows()

from ultralytics import YOLO
import cv2

# Load YOLOv8 model
model = YOLO("yolov8l.pt")

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise IOError("Cannot open webcam")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Perform detection
    results = model(frame, stream=True)

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

    # Show output
    cv2.imshow("YOLOv8 Webcam", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
