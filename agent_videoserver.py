# import the necessary packages
from threading import Thread
try:
    import picamera
    from picamera.array import PiRGBArray
    from picamera import PiCamera
except:
    pass

import cv2
import sys
import math
import base64

# from socket import *
from queue import Queue
# import socketserver
import struct
import time
import traceback
import json

# times = {'imencode':[0.0, 0], 'send':[0.0, 0]}
class WebcamVideoStream:
    def __init__(self, src=0, resolution_in=(640,480)):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)

        # if mjpg_flag: self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, resolution_in[0])
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution_in[1])

        self.frame_pack = self._read()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
        output("INFO","webcam up")

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                break
            try:
                self.frame_pack = self._read()


            except KeyboardInterrupt:
                graceful_shutdown()
                break

            except Exception as e:
                msg = traceback.format_exc()
                output("ERROR", msg)
                break

    def _read(self):
        grabbed, frame = self.stream.read()
        frame_id = math.trunc(time.time()*1000)
        frame = cv2.flip(frame, -1)
        if not grabbed:
            output("ERROR", "webcam not grabbed")
            self.stop()
            return (None, None)

        return (frame_id, frame)


    def read(self):
        # return the frame most recently read
        return self.frame_pack

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        self.stream.release()


class PiVideoStream:

    def __init__(self, resolution_in=(640, 480), framerate=30):
        # initialize the camera and stream
        self.camera = PiCamera()
        self.camera.resolution = resolution_in
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution_in)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)

        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame_pack = (None, None)
        self.stopped = False
        output("INFO","picam up")


    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        time.sleep(2.0)
        try:
            for f in self.stream:
                frame_id = math.trunc(time.time()*1000)
                self.frame_pack = (frame_id, f.array)

                self.rawCapture.truncate(0)

                # if the thread indicator variable is set, stop the thread
                # and resource camera resources
                if self.stopped:
                    break

        except KeyboardInterrupt:
            output("ERROR", "Ctrl-C")
            graceful_shutdown()

        except Exception as e:
            output("ERROR", traceback.format_exc())
            graceful_shutdown()

    def read(self):
        # return the frame most recently read
        return self.frame_pack

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

        self.stream.close()
        self.rawCapture.close()
        self.camera.close()

def output(t, message):
    j_str = json.dumps({"type": "VS_"+t, "message":message})
    print(j_str, flush=True)

FORMAT = "!QHHI"
def send_from(frame_id, arr):
    header = struct.pack(FORMAT, frame_id, res[0], res[1], arr.shape[0])
    payload = memoryview(arr).cast('B').tobytes()
    output("FRAME", base64.b64encode(header+payload).decode())

def graceful_shutdown():
    output("ERROR", "going down")
    vs.stop()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        output("USAGE", "./program WIDTHxHEIGHT")
        # exit()
        res = (640, 480)
    else:
        res = tuple(int(i) for i in sys.argv[1].split("x"))

    try:
        vs = PiVideoStream(resolution_in=res).start()
    except:
        vs = WebcamVideoStream(src=0, resolution_in=res).start()
        # vs = WebcamVideoStream(src=0, resolution_in=res)


    output("INFO", "running")
    try:
        previous_frame_id = None
        while True:
            # frame_id, frame = vs._read()
            frame_id, frame = vs.read()
            if previous_frame_id == frame_id:
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, -1)

            encoded, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 98])
            send_from(frame_id, buf)
            previous_frame_id = frame_id

    except KeyboardInterrupt:
        output("ERROR", "Ctrl-C")

    except Exception as e:
        output("ERROR", traceback.format_exc())

    graceful_shutdown()
    output("INFO", "Bye bye")