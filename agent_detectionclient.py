import cv2
import numpy as np
import io
from socket import *
import struct
import time
import sys
from threading import Thread, Event
from queue import Queue
import json
import traceback


FORMAT = "!QHHI"
INT_SIZE = struct.calcsize(FORMAT)
BBOX_FORMAT = "!QHHHHHH"

def recv_into(source):
    try:
        ret = source.recv(INT_SIZE)
        # start = time.time()
        # print(ret)
        frame_id, frame_w, frame_h, shape_w = struct.unpack(FORMAT, ret)
    except Exception as e:
        print(str(e), traceback.format_exc())
        raise

    arr = np.zeros(shape=(shape_w, 1), dtype="uint8")
    view = memoryview(arr).cast('B')
    while len(view):
        nrecv = source.recv_into(view)
        view = view[nrecv:]
    # times['recv'][0] += (time.time()-start); times['recv'][1] += 1

    return frame_id, frame_w, frame_h, arr


def send_from(frame_id, arr, dest):
    msg = struct.pack(FORMAT, frame_id, res[0], res[1], arr.shape[0])
    dest.send(msg)
    view = memoryview(arr).cast('B')
    while len(view):
        nsent = dest.send(view)
        view = view[nsent:]

class ThirdPartyThread:
    def __init__(self):

        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        self.t = Thread(target=self.update, args=())
        self.t.start()
        return self

    def update(self):
        while not self.stopped:
            try:
                third_party_socket = socket(AF_INET, SOCK_STREAM)
                third_party_socket.connect(THIRDSERVER_ADDR)
                print("\n\n[INFO] Detection client connecting to 3rd party...", end="")
                print("ready")
                output(0, "3rd party server connected")
                break
            except Exception as e:
                # print("failed")
                # msg = traceback.format_exc()
                # output(1, msg)
                # print(msg)
                time.sleep(1)

        # keep looping infinitely until the thread is stopped
        with third_party_socket:
            try:
                while not self.stopped:
                    frame_id, max_rect, buf = g_queue.get()
                    if max_rect is not None:
                        fX, fY, fW, fH = max_rect
                        cv2.rectangle(buf, (fX, fY), (fX+ fW, fY + fH), (0, 0, 255), 3)
                        encoded, buf = cv2.imencode('.jpg', buf, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

                    send_from(frame_id, buf, third_party_socket)

            except Exception:
                msg = traceback.format_exc()
                output(1, msg)
                print(msg)


    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        self.t.join()


# times = {'recv':[0.0, 0], 'decode':[0.0, 0], 'graystyle':[0.0, 0], 'detect':[0.0, 0], 'send':[0.0, 0]}
def detection():
    cascade = cv2.CascadeClassifier(CASCADE_FILE)
    while True:
        try:
            print("\n\n[INFO] Detection client connecting to video server...", end="")
            video_socket = socket(AF_INET, SOCK_STREAM)
            video_socket.connect(VSERVER_ADDR)
            print("ready")
            output(0, "video server connected")
            break
        except Exception as e:
            print("failed")
            msg = traceback.format_exc()
            output(1, msg)
            print(msg)
            time.sleep(1)

    # cv2.namedWindow('image',cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('image', 800,600)
    output(2, "detection running")

    with video_socket:
        try:
            global res
            while True :#not event.isSet():
                frame_id, frame_w, frame_h, a = recv_into(video_socket)
                # start = time.time()
                frame = cv2.imdecode(a, 1)

                res = (frame_w, frame_h)

                # times['decode'][0] += (time.time()-start); times['decode'][1] += 1

                # start = time.time()
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)


                # times['graystyle'][0] += (time.time()-start); times['graystyle'][1] += 1

                # start = time.time()
                rects = cascade.detectMultiScale(gray,
                    scaleFactor = 1.1,
                    # minNeighbors = 5,
                    minNeighbors = 20,
                    minSize = (50, 50),
                    # maxSize = (450,720),
                    flags = 1)#0|cv2.CASCADE_SCALE_IMAGE)
                # times['detect'][0] += (time.time()-start); times['detect'][1] += 1

                if rects != ():
                    max_rect_size = 0
                    max_rect = None
                    for rect in rects:
                        fX, fY, fW, fH = rect
                        # print("{} - {} - {} - {}".format(fX, fY, fW, fH))
                        # cv2.rectangle(frame, (fX, fY), (fX+ fW, fY + fH), (0, 0, 255), 3)
                        if fW * fH > max_rect_size:
                            max_rect = rect

                    # start = time.time()
                    # fcs_queue.put_nowait((frame_id, frame_w, frame_h, max_rect))
                    fcs_send(frame_id, frame_w, frame_h, max_rect)
                    # times['send'][0] += (time.time()-start); times['send'][1] += 1
                    g_queue.put_nowait((frame_id, max_rect, frame))
                else:
                    g_queue.put_nowait((frame_id, None, a))

                # cv2.imshow("image", frame)
                # cv2.waitKey(1)

        except Exception as e:
            msg = traceback.format_exc()
            output(1, msg)
            print(msg)
            cv2.destroyAllWindows()

# status_queue = Queue()
def output(status, message):
    # status_queue.put_nowait((status, message))
    outputstream.sendto(json.dumps({"src":"detection", "status": status, "msg":message}).encode(), OSERVER_ADDR)

# def status_update_thread():
#     outputstream = socket(AF_INET, SOCK_DGRAM)
#     while True:
#         data = status_queue.get()
#         if data is None:
#             break
#         status, message = data
#         outputstream.sendto(json.dumps({"src":"detection", "status": status, "msg":message}).encode(), OSERVER_ADDR)
#     outputstream.close()


# fcs_queue = Queue()
# def fcsstream_thread():
#     fcsstream = socket(AF_INET, SOCK_DGRAM)
#     while True:
#         data = fcs_queue.get()
#         if data is None: break
#         frame_id, frame_w, frame_h, max_rect = data
#         fX, fY, fW, fH = max_rect
#         send_str = struct.pack(BBOX_FORMAT, frame_id, frame_w, frame_h, fX, fY, fW, fH)
#         try:
#             fcsstream.sendto(send_str, FCSERVER_ADDR)
#         except Exception as e:
#             msg = traceback.format_exc() + "send failed"
#             output(1, msg)
#             print(msg)

def fcs_send(frame_id, frame_w, frame_h, max_rect):
    fX, fY, fW, fH = max_rect
    try:
        send_str = struct.pack(BBOX_FORMAT, frame_id, frame_w, frame_h, fX, fY, fW, fH)
        fcsstream.sendto(send_str, FCSERVER_ADDR)
    except Exception as e:
        msg = traceback.format_exc() + "send failed"
        output(1, msg)
        print(msg)


if __name__ == "__main__":
    if len(sys.argv) < 10:
        print("Usage: ./program VideoServerHost VSPort CasscadeFile FlightControlServerHost FCSPort OutputServerHost OSPort 3rdPartyServerHost 3rdPartyPort")
        exit()

    FCSERVER_ADDR = (sys.argv[4], int(sys.argv[5]))
    OSERVER_ADDR = (sys.argv[6], int(sys.argv[7]))#'192.168.10.1', 25000
    VSERVER_ADDR = (sys.argv[1], int(sys.argv[2]))
    THIRDSERVER_ADDR = (sys.argv[8], int(sys.argv[9]))

    CASCADE_FILE = sys.argv[3]
    g_queue = Queue()


    tpt = ThirdPartyThread().start()
    outputstream = socket(AF_INET, SOCK_DGRAM)
    fcsstream = socket(AF_INET, SOCK_DGRAM)
    output(0, "threads up")

    try:
        detection()
    except KeyboardInterrupt:
        pass
    finally:
        # fcs_queue.put(None)
        output(1, "all down")
        # status_queue.put(None)

    # for t in times:
    #     ts = times[t]
    #     print("latency of ", t, ts[0]/ts[1])
