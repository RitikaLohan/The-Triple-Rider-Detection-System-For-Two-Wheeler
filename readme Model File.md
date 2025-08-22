# Where to get MobileNetSSD files
You can download the deploy prototxt and caffemodel from these official sources:
- prototxt: https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.prototxt
- caffemodel: https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.caffemodel

Place both into the models/ folder.

# Camera notes
- If using multiple USB webcams on a single PC, enumerate their device ids (0,1,2...) or use `v4l2-ctl --list-devices` on Linux.
- For IP cameras use rtsp URL: e.g., rtsp://username:password@camera-ip:554/stream

# Tuning
- Tune `detector.conf_threshold`, `controller.base_green` and `controller.k` tuning constant in compute_green_time.
- Add smoothing / temporal averaging of vehicle counts to avoid rapid phase variations.

# Safety & hardware
This code is for simulation and prototyping. To connect to real traffic signals, you will need a certified traffic controller and hardware interface (relay boards, safety 