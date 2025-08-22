from flask import Flask, render_template, Response, jsonify
import cv2
from detector import VehicleDetector
from controller import TrafficController
import threading
import time

app = Flask(__name__)

# configure cameras (0, 1 or rtsp URLs)
CAM_SOURCES = {
    'N': 0,  # change according to your setup
    'E': 1,
    'S': 2,
    'W': 3
}

# load detector
detector = VehicleDetector('models/MobileNetSSD_deploy.prototxt', 'models/MobileNetSSD_deploy.caffemodel')

# controller
phases = list(CAM_SOURCES.keys())
controller = TrafficController(phases)

# shared state
state = {
    'counts': {p: 0 for p in phases},
    'frames': {p: None for p in phases},
    'current_phase': phases[0],
    'phase_time_left': controller.phase_duration
}

caps = {}

def camera_thread(name, src):
    cap = cv2.VideoCapture(src)
    caps[name] = cap
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue
        state['frames'][name] = frame
        detections = detector.detect(frame)
        state['counts'][name] = len(detections)
        time.sleep(0.05)

# start camera threads
for name, src in CAM_SOURCES.items():
    t = threading.Thread(target=camera_thread, args=(name, src), daemon=True)
    t.start()

# controller thread
def controller_thread():
    while True:
        # update phase if time expired
        ph, dur, left = controller.get_current_phase()
        state['current_phase'] = ph
        state['phase_time_left'] = left
        if left <= 0:
            # compute next based on latest counts
            next_ph, next_dur = controller.next_phase(state['counts'])
            state['current_phase'] = next_ph
            state['phase_time_left'] = next_dur
        time.sleep(0.5)

t = threading.Thread(target=controller_thread, daemon=True)
t.start()

@app.route('/')
def index():
    return render_template('index.html', phases=phases)

@app.route('/counts')
def counts_api():
    return jsonify(state['counts'])

@app.route('/state')
def state_api():
    ph, dur, left = controller.get_current_phase()
    return jsonify({'current_phase': ph, 'duration': dur, 'time_left': left})

def gen_frame(name):
    while True:
        frame = state['frames'].get(name)
        if frame is None:
            time.sleep(0.1)
            continue
        # annotate frame with boxes (optional)
        detections = detector.detect(frame)
        for d in detections:
            (startX, startY, endX, endY) = d['box']
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0,255,0), 2)
            cv2.putText(frame, f"{d['label']}:{d['confidence']:.2f}", (startX, startY-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

@app.route('/video/<name>')
def video_feed(name):
    return Response(gen_frame(name), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)