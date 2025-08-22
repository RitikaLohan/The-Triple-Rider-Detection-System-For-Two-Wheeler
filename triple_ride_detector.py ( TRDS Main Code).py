# triple_ride_detector.py
import cv2
import numpy as np
import serial
import time

# --- CONFIG ---
PROTOTXT = "models/MobileNetSSD_deploy.prototxt"
MODEL = "models/MobileNetSSD_deploy.caffemodel"
CONF_THRESH = 0.4

VIDEO_SRC = 0  # 0 for webcam or replace with video file / RTSP
ARDUINO_PORT = "COM3"  # e.g. "COM3" on Windows or "/dev/ttyACM0" on Linux
ARDUINO_BAUD = 115200
ALERT_COOLDOWN = 8  # seconds between alerts per motorbike (prevent spamming)

# MobileNet-SSD class IDs mapping (from the common MobileNet-SSD)
CLASSES = {0: 'background', 1: 'aeroplane', 2: 'bicycle', 3: 'bird', 4: 'boat',
           5: 'bottle', 6: 'bus', 7: 'car', 8: 'cat', 9: 'chair',
           10: 'cow', 11: 'diningtable', 12: 'dog', 13: 'horse',
           14: 'motorbike', 15: 'person', 16: 'pottedplant', 17: 'sheep',
           18: 'sofa', 19: 'train', 20: 'tvmonitor'}

VEHICLE_CLASS_ID = 14  # motorbike
PERSON_CLASS_ID = 15

# --- load net ---
net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)

# optional: set preferable backend / target if you have OpenCV built for CUDA
# net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
# net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# --- serial to Arduino ---
ser = None
try:
    ser = serial.Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=1)
    time.sleep(2)  # wait for Arduino to reset
    print(f"Connected to Arduino on {ARDUINO_PORT}")
except Exception as e:
    print("Warning: could not open serial port:", e)
    ser = None

# store last alert time per detected motorbike (approx by center position)
last_alert_times = []

def box_center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2) // 2, (y1 + y2) // 2)

def iou(a, b):
    # simple IoU for two boxes a,b = (x1,y1,x2,y2)
    xA = max(a[0], b[0])
    yA = max(a[1], b[1])
    xB = min(a[2], b[2])
    yB = min(a[3], b[3])
    interW = max(0, xB - xA)
    interH = max(0, yB - yA)
    interArea = interW * interH
    boxAArea = (a[2] - a[0]) * (a[3] - a[1])
    boxBArea = (b[2] - b[0]) * (b[3] - b[1])
    denom = float(boxAArea + boxBArea - interArea)
    if denom == 0.0:
        return 0.0
    return interArea / denom

cap = cv2.VideoCapture(VIDEO_SRC)
if not cap.isOpened():
    raise RuntimeError("Could not open video source")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    motorbikes = []
    persons = []

    # parse detections
    for i in range(detections.shape[2]):
        confidence = float(detections[0, 0, i, 2])
        if confidence < CONF_THRESH:
            continue
        cls = int(detections[0, 0, i, 1])
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (startX, startY, endX, endY) = box.astype("int")
        # clamp
        startX = max(0, startX); startY = max(0, startY)
        endX = min(w - 1, endX); endY = min(h - 1, endY)
        bbox = (startX, startY, endX, endY)

        if cls == VEHICLE_CLASS_ID:
            motorbikes.append({'box': bbox, 'conf': confidence})
        elif cls == PERSON_CLASS_ID:
            persons.append({'box': bbox, 'conf': confidence})

    # For each motorbike, count persons that overlap (or are close)
    now = time.time()
    updated_alert_times = []

    for mb in motorbikes:
        mb_box = mb['box']
        count = 0
        for p in persons:
            p_box = p['box']
            # Two ways to decide association:
            # 1) IoU overlap > small threshold
            # 2) person center within expanded motorbike bbox
            if iou(mb_box, p_box) > 0.02:  # very small IOU threshold
                count += 1
            else:
                # expanded box test
                x1, y1, x2, y2 = mb_box
                pad_x = int((x2 - x1) * 0.6)
                pad_y = int((y2 - y1) * 1.2)
                ex = (x1 - pad_x, y1 - pad_y, x2 + pad_x, y2 + pad_y)
                px1, py1, px2, py2 = p_box
                cx = (px1 + px2) // 2
                cy = (py1 + py2) // 2
                if cx >= ex[0] and cx <= ex[2] and cy >= ex[1] and cy <= ex[3]:
                    count += 1

        # Draw motorbike bbox; color red if triple
        if count >= 3:
            color = (0, 0, 255)
            label = f"TRIPLE ({count})"
            # check cooldown to avoid repeated alerts for same motorbike
            recent = False
            for t_center, t_time in last_alert_times:
                # if this motorbike is near that previous alert center and within cooldown, skip
                c = box_center(mb_box)
                d = (c[0] - t_center[0])**2 + (c[1] - t_center[1])**2
                if d < (100**2) and (now - t_time) < ALERT_COOLDOWN:
                    recent = True
                    break
            if not recent:
                # send alert to arduino
                if ser and ser.is_open:
                    try:
                        ser.write(b"ALERT\n")
                        print("Sent ALERT to Arduino")
                    except Exception as e:
                        print("Serial write failed:", e)
                # record alert center + time
                last_alert_times.append((box_center(mb_box), now))
            # keep this motorbike's last alert time in updated list so old ones expire later
            updated_alert_times.append((box_center(mb_box), now))
        else:
            color = (0, 255, 0)
            label = f"motorbike ({count})"

        cv2.rectangle(frame, (mb_box[0], mb_box[1]), (mb_box[2], mb_box[3]), color, 2)
        cv2.putText(frame, label, (mb_box[0], mb_box[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Draw person boxes (optional)
    for p in persons:
        pb = p['box']
        cv2.rectangle(frame, (pb[0], pb[1]), (pb[2], pb[3]), (255, 200, 0), 1)
    # Clean last_alert_times older than cooldown
    last_alert_times = [x for x in last_alert_times if now - x[1] < (ALERT_COOLDOWN * 2)]

    cv2.imshow("Triple Ride Detector", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if ser:
    ser.close()