# Performance testing
You need opencv 3 to run the programs. For camera capture on Pi, you may need pip3 install picamera. You also need to pip3 install psutil

## Camera capture test

To test camera, please specify the resolution in the format WIDTHxHEIGHT like 1280x720 and frame per second like 15, 20, 30, etc.

```bash
python3 cam.py <WIDTH>x<HEIGHT> <FPS> [web or pic to choose webcam or picamera]
```

To compare camera performance using thread or not,

For usb webcam:
```bash
python3 cam_webcam_speedup.py <WIDTH>x<HEIGHT> <FPS> [1 or 0 to turn on/off MJPG]
```
For picamera:
```bash
python3 cam_piccam_speedup.py <WIDTH>x<HEIGHT> <FPS>
```

## Tracking test

To test tracking, you can use the videos in the team drive under Test/ folder

Before testing, you need to "sudo pip3 install psutil"

Assume the video is mp4, and if you don't use default videos, you will be asked to select Region of Interest (ROI).

Note that the number means the index of the algorithm. 0:BOOSTING 1:MIL 2:KCF 3:TLD 4:MEDIANFLOW 5:GOTURN (#5 GOTURN needs NN model files)
```bash
python3 tracking.py [0-5] <FILENAME>
```

## Detection test

To test detection, you may change the object of interest by switching filepath argument in the CascadeClassifier. You can find default feature files in data/ folder.

Before testing, you need to "sudo pip3 install psutil"


```bash
python3 detection.py [face or ped to detect frontal face or pedestrian] <FILENAME>
```

# Acknowledgement
OpenCV

PiCamera

LearnOpenCV

PyImageSearch

StackOverflow

...etc