# import the necessary packages
from threading import Thread
import cv2
import os
import psutil
import sys
process = psutil.Process(os.getpid())
# print(process.memory_info()[0] / float(2 ** 20))

# import the Queue class from Python 3
if sys.version_info >= (3, 0):
    from queue import Queue

# otherwise, import the Queue class for Python 2.7
else:
    from Queue import Queue


class WebcamVideoStream:
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)

        if mjpg_flag: self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_in[0])
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_in[1])

        # (self.grabbed, self.frame) = self.stream.read()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
        self.fps_array = []
        self.Q = Queue(maxsize=128)

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream

            if not self.Q.full():
                start = cv2.getTickCount()
                # (self.grabbed, self.frame) = self.stream.read()
                # read the next frame from the file
                (grabbed, frame) = self.stream.read()
                self.fps_array.append(cv2.getTickFrequency()/(cv2.getTickCount()-start))
                # if the `grabbed` boolean is `False`, then we have
                # reached the end of the video file
                if not grabbed:
                    self.stop()
                    return
                # add the frame to the Queue
                self.Q.put(frame)


    def read(self):
        # return the frame most recently read
        # return self.frame

        # return next frame in the queue
        return self.Q.get()

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
display_flag = False
num_seconds = 5
mjpg_flag = False

def webcam():
    # grab a pointer to the video stream and initialize the FPS counter
    print("[INFO] sampling frames from webcam...")
    stream = cv2.VideoCapture(0)

    if mjpg_flag: stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
    stream.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_in[0])
    stream.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_in[1])

    cv2.namedWindow('Frame',cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Frame', 800,600)
    fps = FPSCLOCK().start()

    fps_array = []
    mem_usage = []
    cpu_usage = []
    # loop over some frames
    while fps.elapsed() < num_seconds:

        # grab the frame from the stream and resize it to have a maximum
        # width of 400 pixels
        start = cv2.getTickCount()
        (grabbed, frame) = stream.read()
        # frame = imutils.resize(frame, width=400)
        fps_array.append(cv2.getTickFrequency()/(cv2.getTickCount()-start))
        mem_usage.append(process.memory_info()[0] / float(2 ** 20))
        cpu_usage.append(process.cpu_percent())

        # check to see if the frame should be displayed to our screen
        if display_flag:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27: break

        # update the FPS counter
        fps.update()

    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    print("[INFO] capture FPS: {:.2f}".format(sum(fps_array)/len(fps_array)))
    print("[INFO] MEM usage: {:.2f}MiB".format(sum(mem_usage)/len(mem_usage)))
    print("[INFO] CPU usage: {:.2f}%".format(sum(cpu_usage)/len(cpu_usage)))

    # do a bit of cleanup
    stream.release()
    cv2.destroyAllWindows()


    # created a *threaded* video stream, allow the camera sensor to warmup,
    # and start the FPS counter
    print("\n\n[INFO] sampling THREADED frames from webcam...")
    vs = WebcamVideoStream(src=0).start()
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
        if display_flag:
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break

        # update the FPS counter
        fps.update()

    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))


    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()
    print("[INFO] capture FPS: {:.2f}".format(vs.capture_fps()))
    print("[INFO] MEM usage: {:.2f}MiB".format(sum(mem_usage)/len(mem_usage)))
    print("[INFO] CPU usage: {:.2f}%".format(sum(cpu_usage)/len(cpu_usage)))


if __name__ == '__main__' :
    resolution_in = tuple(int(i) for i in sys.argv[1].split("x")) if len(sys.argv) >= 2 else resolution_in
    fps_in = int(sys.argv[2]) if len(sys.argv) >= 3 else 30
    mjpg_flag = True if len(sys.argv) >= 4 and sys.argv[3] == "1" else False
    webcam()