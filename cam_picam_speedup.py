# import the necessary packages
import picamera
from picamera.array import PiRGBArray
from picamera import PiCamera

from threading import Thread
import cv2
import time
import os, sys
import psutil
process = psutil.Process(os.getpid())
# import the Queue class from Python 3
if sys.version_info >= (3, 0):
    from queue import Queue

# otherwise, import the Queue class for Python 2.7
else:
    from Queue import Queue

class PiVideoStream:

    def __init__(self, resolution=(320, 240), framerate=30):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
            format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False
        self.fps_array = []
        self.Q = Queue(maxsize=40)

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped

        start = cv2.getTickCount()
        for f in self.stream:
            self.fps_array.append(cv2.getTickFrequency()/(cv2.getTickCount()-start))
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame

            self.frame = f.array
            # self.Q.put_nowait(f.array)

            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

            start = cv2.getTickCount()

    def read(self):
        # return the frame most recently read
        return self.frame
        # try:
        #     frame = self.Q.get_nowait()
        # except:
        #     frame = None
        # return frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

    def capture_fps(self):
        return sum(self.fps_array)/len(self.fps_array)

# import the necessary packages
import datetime

class FPSCLOCK:
    def __init__(self):
        # store the start time, end time, and total number of frames
        # that were examined between the start and end intervals
        self._start = None
        self._end = None
        self._numFrames = 0

    def start(self):
        # start the timer
        self._start = datetime.datetime.now()
        return self

    def stop(self):
        # stop the timer
        self._end = datetime.datetime.now()

    def update(self):
        # increment the total number of frames examined during the
        # start and end intervals
        self._numFrames += 1

    def elapsed(self):
        # return the total number of seconds between the start and
        # end interval
        if self._end is not None:
            return (self._end - self._start).total_seconds()
        else:
            return (datetime.datetime.now() - self._start).total_seconds()


    def fps(self):
        # compute the (approximate) frames per second
        return self._numFrames / self.elapsed()



resolution_in = (1280, 720)
fps_in = 30
display_flag = 0
num_seconds = 10

def picam():
    import picamera
    from picamera.array import PiRGBArray
    from picamera import PiCamera
    cv2.namedWindow('Frame',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Frame', 800,600)

    #  initialize the camera and stream
    camera = PiCamera()
    camera.resolution = resolution_in
    camera.framerate = fps_in
    rawCapture = PiRGBArray(camera, size=resolution_in)
    stream = camera.capture_continuous(rawCapture, format="bgr",
        use_video_port=True)

    # allow the camera to warmup and start the FPSCLOCK counter
    print("[INFO] sampling frames from `picamera` module...")
    time.sleep(2.0)
    fps = FPSCLOCK().start()

    fps_array = []
    mem_usage = []
    cpu_usage = []

    start = cv2.getTickCount()
    # loop over some frames
    for (i, f) in enumerate(stream):
        fps_array.append(cv2.getTickFrequency()/(cv2.getTickCount()-start))
        mem_usage.append(process.memory_info()[0] / float(2 ** 20))
        cpu_usage.append(process.cpu_percent())
        # grab the frame from the stream and resize it to have a maximum
        # width of 400 pixels
        frame = f.array
        # frame = imutils.resize(frame, width=400)

        # check to see if the frame should be displayed to our screen
        if display_flag > 0:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

        # clear the stream in preparation for the next frame and update
        # the FPSCLOCK counter
        rawCapture.truncate(0)
        fps.update()

        # check to see if the desired number of frames have been reached
        if fps.elapsed() > num_seconds:
            break

        start = cv2.getTickCount()

    # stop the timer and display FPSCLOCK information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    print("[INFO] capture FPS: {:.2f}".format(sum(fps_array)/len(fps_array)))
    print("[INFO] MEM usage: {:.2f}MiB".format(sum(mem_usage)/len(mem_usage)))
    print("[INFO] CPU usage: {:.2f}%".format(sum(cpu_usage)/len(cpu_usage)))

    # do a bit of cleanup
    cv2.destroyAllWindows()
    stream.close()
    rawCapture.close()
    camera.close()

    # created a *threaded *video stream, allow the camera sensor to warmup,
    # and start the FPSCLOCK counter
    print("\n\n[INFO] sampling THREADED frames from `picamera` module...")
    vs = PiVideoStream(resolution=resolution_in, framerate=fps_in).start()
    time.sleep(2.0)
    fps = FPSCLOCK().start()

    mem_usage = []
    cpu_usage = []
    # loop over some frames...this time using the threaded stream
    while fps.elapsed() < num_seconds:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        frame = vs.read()
        # frame = imutils.resize(frame, width=400)
        mem_usage.append(process.memory_info()[0] / float(2 ** 20))
        cpu_usage.append(process.cpu_percent())

        # check to see if the frame should be displayed to our screen
        if display_flag> 0:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

        # update the FPSCLOCK counter
        fps.update()

    # stop the timer and display FPSCLOCK information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()
    print("[INFO] capture FPS: {:.2f}".format(vs.capture_fps()))
    print("[INFO] MEM usage: {:.2f}MiB".format(sum(mem_usage)/len(mem_usage)))
    print("[INFO] CPU usage: {:.2f}%".format(sum(cpu_usage)/len(cpu_usage)))

if __name__ == '__main__' :
    resolution_in = tuple(int(i) for i in sys.argv[1].split("x")) if len(sys.argv) >= 2 else resolution_in
    fps_in = int(sys.argv[2]) if len(sys.argv) >= 3 else fps_in
    picam()