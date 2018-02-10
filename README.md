# Performance testing
You need opencv 3 to run the programs. For camera capture on Pi, you may need pip3 install picamera.

To test camera, please specify the resolution in the format WIDTHxHEIGHT like 1280x720 and frame per second like 15, 20, 30, etc.

```bash
python3 cam.py <WIDTH>x<HEIGHT> <FPS>
```

Before running fast capture, you need to pip3 install psutil
For usb webcam:
```bash
python3 cam_webcam_speedup.py <WIDTH>x<HEIGHT> <FPS> <1 or 0 for MJPG>
```
For pi:
```bash
python3 cam_piccam_speedup.py <WIDTH>x<HEIGHT> <FPS>
```

To test tracking, you can use the videos in the team drive under Test/ folder

Assume the video is mp4, and if you don't use default videos, you will be asked to select Region of Interest (ROI).

Note that the number means the index of the algorithm. 0:BOOSTING 1:MIL 2:KCF 3:TLD 4:MEDIANFLOW 5:GOTURN (#5 GOTURN This needs model files)
```bash
python3 tracking.py [0-5] <FILENAME W/O EXTENSION>
```

To test detection,
Change the feature filepath argument in the CascadeClassifier to detect different object of interest. You can find feature files in data/ folder.

```bash
python3 detection.py <FILENAME W/ EXTENSION>
```

# Acknowledgement
OpenCV

PiCamera

LearnOpenCV

PyImageSearch

...etc