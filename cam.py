import cv2
import sys

def webcam(resolution, fps_set):
    video = cv2.VideoCapture(0)

    # Exit if video not opened.
    if not video.isOpened():
        print ("Could not open video")
        sys.exit()

    video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
    video.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
    # video.set(cv2.CAP_PROP_FPS, fps_set)

    # Read first frame.
    ok, frame = video.read()
    if not ok:
        print ('Cannot read video file')
        sys.exit()

    width = video.get(3)   # float
    height = video.get(4) # float
    print ("%dx%d"%(width, height))

    times = []
    start = cv2.getTickCount()
    try:
        while True:
            # Start timer
            timer = cv2.getTickCount()

            # Read a new frame
            ok, frame = video.read()
            if not ok:
                break

            # Calculate Frames per second (FPS)
            freq = cv2.getTickFrequency()
            count = (cv2.getTickCount() - timer)
            # fps = freq / count
            times.append(count/freq)
            if ((timer-start)/freq > 5.0): break
    except KeyboardInterrupt:
        pass

    print("elapsed %.4f seconds" % (sum(times)/len(times)))
    print("fps", len(times)/sum(times))


def picam(resolution, fps_set):
    import picamera
    import time

    from picamera.array import PiRGBArray
    from picamera import PiCamera

    camera = PiCamera()
    camera.resolution = resolution
    camera.framerate = fps_set
    time.sleep(2)
    rawCapture = PiRGBArray(camera, size=resolution)

    times = []
    print("ready")
    timer = cv2.getTickCount()
    start = timer
    try:
        for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            # Calculate Frames per second (FPS)
            freq = cv2.getTickFrequency()
            count = (cv2.getTickCount() - timer)
            # fps = freq / count
            times.append(count/freq)

            rawCapture.truncate(0)
            # k = cv2.waitKey(1) & 0xff
            # if k == 113 : break

            timer = cv2.getTickCount()
            if ((timer-start)/freq > 5.0): break
        camera.close()
    except KeyboardInterrupt:
        print(times, sum(times)/len(times))
        camera.close()
        sys.exit()
    except picamera.exc.PiCameraValueError:
        print(times, sum(times)/len(times))
        camera.close()
        sys.exit()

    print("elapsed %.4f seconds" % (sum(times)/len(times)))
    print("fps", len(times)/sum(times))

if __name__ == '__main__' :
    resolution = tuple(int(i) for i in sys.argv[1].split("x"))
    fps = int(sys.argv[2])
    # webcam(resolution, fps)
    picam(resolution, fps)