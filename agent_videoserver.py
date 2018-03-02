# import the necessary packages
from threading import Thread
import cv2
import sys
import math

from socket import *
from queue import Queue
import socketserver
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

        self.stream.read()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
        output(0, "webcam up")

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
                output(1, msg)
                print(msg)
                break

    def _read(self):
        grabbed, frame = self.stream.read()
        frame_id = math.trunc(time.time()*1000)
        frame = cv2.flip(frame, -1)
        if not grabbed:
            print("not grabbed")
            output(1, "webcam not grabbed")
            self.stop()

        return (frame_id, frame)


    def read(self):
        # return the frame most recently read
        return self.frame_pack

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        self.stream.release()


FORMAT = "!QHHI"
def send_from(frame_id, arr, dest):
    msg = struct.pack(FORMAT, frame_id, res[0], res[1], arr.shape[0])
    dest.send(msg)
    view = memoryview(arr).cast('B')
    while len(view):
        nsent = dest.send(view)
        view = view[nsent:]

# class MyTCPHandler(socketserver.BaseRequestHandler):

#     def handle(self):
#         # self.request is the TCP socket connected to the client
#         previous_frame_id = None
#         global times, count
#         while True:
#             try:
#                 frame_id, frame = vs.read()
#                 if previous_frame_id == frame_id:
#                     continue

#                 encoded, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 98])
#                 send_from(frame_id, buf, self.request)
#                 previous_frame_id = frame_id
#                 times.append((time.time()-frame_id/1000))

#             except Exception as e:
#                 msg = traceback.format_exc() + "Bye bye " + self.client_address[0]
#                 output(1, msg)
#                 break



def output(status, message):
    outputstream.sendto(json.dumps({"src":"videoserver", "status": status, "msg":message}).encode(), OSERVER_ADDR)

def graceful_shutdown():
    # status_queue.put(None)
    # server.shutdown()
    # server.server_close()
    server.close()
    print("\n\n[INFO] stopped video capture server...")
    output(1, "server down")
    # cv2.destroyAllWindows()
    vs.stop()

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: ./program ServerHost ServerPort WIDTHxHEIGHT OutputHost OutputPort")
        exit()
    # Thread(target=status_update_thread, args=()).start()
    outputstream = socket(AF_INET, SOCK_DGRAM)

    HOST, PORT = sys.argv[1], int(sys.argv[2])#'192.168.10.1', 25000
    res = tuple(int(i) for i in sys.argv[3].split("x"))
    OSERVER_ADDR = (sys.argv[4], int(sys.argv[5]))#'192.168.10.1', 25000

    print("\n\n[INFO] sampling THREADED frames from webcam...")
    vs = WebcamVideoStream(src=0, resolution_in=res).start()
    # vs = WebcamVideoStream(src=0, resolution_in=res)

    print("\n\n[INFO] starting video capture server...")
    # server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    output(2, "videoserver running")
    print("videoserver running")
    try:
        # server.serve_forever()
        conn, addr = server.accept()
        print("client connected")
        with conn:
            previous_frame_id = None
            while True:
                frame_id, frame = vs.read()
                if previous_frame_id == frame_id:
                    time.sleep(0.01)
                    continue

                # frame_id, frame = vs._read()
                # print(frame_id)

                encoded, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 98])
                # times['imencode'][0] += (time.time()-frame_id/1000); times['imencode'][1] += 1
                send_from(frame_id, buf, conn)
                previous_frame_id = frame_id
                # times['send'][0] += (time.time()-frame_id/1000); times['send'][1] += 1

    except KeyboardInterrupt:
        print("Ctrl-C")

    except Exception as e:
        msg = traceback.format_exc() + "Bye bye " + addr[0]
        output(1, msg)
        print(msg)
    finally:
        graceful_shutdown()

    # for t in times:
    #     ts = times[t]
    #     print("latency from frame_id till ", t, ts[0]/ts[1])