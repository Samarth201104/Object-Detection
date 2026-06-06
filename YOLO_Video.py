from ultralytics import YOLO
import cv2
import math

def video_detection(path_x):
    path = path_x
    config_file = r'static\model\ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
    frozen_model = r'static\model\frozen_inference_graph.pb'
    model = cv2.dnn_DetectionModel(frozen_model,config_file)
    classLabels = []
    file_name = r'static\model\ssd_classes.txt'
    with open(file_name,'rt') as fpt:
        classLabels = fpt.read().rstrip('\n').split('\n')
    print(classLabels)

    print(len(classLabels))
    model.setInputSize(320,320)
    model.setInputScale((1.0/127.5))
    model.setInputMean((127.5,127,5,127.5))
    model.setInputSwapRB(True)
    # print('path', path)
    cap=cv2.VideoCapture(path)

    font_scale= 0.7
    font= cv2.FONT_HERSHEY_SIMPLEX
    while True:
        ret,frame=cap.read()
        ClassIndex, confidence, bbox= model.detect(frame,confThreshold=0.55)
        print(ClassIndex)
        if(len(ClassIndex)!=0):
            for ClassInd, conf, boxes in zip(ClassIndex.flatten(),confidence.flatten(),bbox):
                print(ClassInd)
                # if(ClassInd<=80):/
                cv2.rectangle(frame, boxes,(200,0,0),2)
                cv2.putText(frame,classLabels[ClassInd-1]+'-'+str(conf),(boxes[0]+10,boxes[1]+30),font,fontScale = font_scale,color=(0,10,0),thickness=2)

        yield frame

    # cap.release()
cv2.destroyAllWindows()



# def video_detection(path_x):
#     video_capture = path_x
    
#     cap=cv2.VideoCapture(video_capture)
#     frame_width=int(cap.get(3))
#     frame_height=int(cap.get(4))
   

#     model=YOLO("../YOLO-Weights/yolov8n.pt")
#     classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
#                   "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
#                   "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
#                   "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
#                   "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
#                   "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
#                   "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
#                   "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
#                   "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
#                   "teddy bear", "hair drier", "toothbrush"
#                   ]
#     while True:
#         success, img = cap.read()
#         results=model(img,stream=True)
#         for r in results:
#             boxes=r.boxes
#             for box in boxes:
#                 x1,y1,x2,y2=box.xyxy[0]
#                 x1,y1,x2,y2=int(x1), int(y1), int(x2), int(y2)
#                 print(x1,y1,x2,y2)
#                 cv2.rectangle(img, (x1,y1), (x2,y2), (255,0,255),3)
#                 conf=math.ceil((box.conf[0]*100))/100
#                 cls=int(box.cls[0])
#                 class_name=classNames[cls]
#                 label=f'{class_name}{conf}'
#                 t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
#                 print(t_size)
#                 c2 = x1 + t_size[0], y1 - t_size[1] - 3
#                 cv2.rectangle(img, (x1,y1), c2, [255,0,255], -1, cv2.LINE_AA)  # filled
#                 cv2.putText(img, label, (x1,y1-2),0, 1,[255,255,255], thickness=1,lineType=cv2.LINE_AA)

#         yield img
        
# cv2.destroyAllWindows()