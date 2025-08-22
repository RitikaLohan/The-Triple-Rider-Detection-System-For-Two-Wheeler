import cv2
import numpy as np

class VehicleDetector:
    def __init__(self, prototxt_path, model_path, conf_threshold=0.4):
        self.net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
        self.conf_threshold = conf_threshold
        # COCO/MobileNet SSD class ids for vehicles
        self.VEHICLE_CLASSES = {2: 'car', 3: 'motorbike', 5: 'bus', 7: 'truck'}

    def detect(self, frame):
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()

        results = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > self.conf_threshold:
                idx = int(detections[0, 0, i, 1])
                if idx in self.VEHICLE_CLASSES:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype('int')
                    results.append({
                        'class_id': idx,
                        'label': self.VEHICLE_CLASSES[idx],
                        'confidence': float(confidence),
                        'box': (startX, startY, endX, endY)
                    })
        return results