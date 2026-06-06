from ultralytics import YOLO
import cv2



model=YOLO('../Yolo-Weights/yolov8l.pt')
results=model(r"C:\Users\Samarth\Downloads\photo.jpeg",show=False)


for result in results:


    img = result.orig_img
    names = result.names
    results_prediction = result.boxes
    cls = results_prediction.cls
    conf = results_prediction.conf
    xyxy = results_prediction.xyxy


    for i in range(len(cls)):

        classname = names[int(cls[i])]+' ' + str(round(float(conf[i]), 2))
        xyxys = xyxy[i]
        st = (int(xyxys[0]), int(xyxys[1]))
        end = (int(xyxys[2]), int(xyxys[3]))

        img = cv2.putText(img, classname, st, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 10, 0), 2, cv2.LINE_AA)
        img = cv2.rectangle(img, st, end, (200, 0, 0), 2)


print(img.shape)
cv2.imshow('img', img)
cv2.waitKey(0)
