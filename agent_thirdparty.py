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


def output(status, message):
    outputstream.sendto(json.dumps({"src":"3rd party", "status": status, "msg":message}).encode(), OSERVER_ADDR)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: ./program ServerHost ServerPort OutputHost OutputPort")
        exit()
    # Thread(target=status_update_thread, args=()).start()
    outputstream = socket(AF_INET, SOCK_DGRAM)

    HOST, PORT = sys.argv[1], int(sys.argv[2])#'192.168.10.1', 25000
    OSERVER_ADDR = (sys.argv[3], int(sys.argv[4]))#'192.168.10.1', 25000

    print("\n\n[INFO] starting 3rd party server...")
    # server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)

    output(2, "3rd party running")
    print("3rd party running")

    conn, addr = server.accept()
    print("client connected " + addr[0])
    try:
        cv2.namedWindow('image',cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', 640,480)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        filename = time.strftime("%Y%m%d-%H%M%S") + ".avi"
        out = cv2.VideoWriter(filename, fourcc, 20.0, (640,480))
        with conn:
            while True:
                frame_id, frame_w, frame_h, a = recv_into(conn)
                frame = cv2.imdecode(a, 1)
                out.write(frame)
                cv2.imshow("image", frame)
                cv2.waitKey(1)

    except KeyboardInterrupt:
        print("Ctrl-C")

    except Exception as e:
        msg = traceback.format_exc() + "Bye bye " + addr[0]
        output(1, msg)
        print(msg)

    out.release()
    cv2.destroyAllWindows()
    server.close()