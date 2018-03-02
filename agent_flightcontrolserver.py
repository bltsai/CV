from threading import Thread
import json
import sys
import math
# import psutil, os
import time
import traceback
# process = psutil.Process(os.getpid())

from socket import *
import struct
from queue import Queue

BBOX_FORMAT = "!QHHHHHH"
BBOX_SIZE = struct.calcsize(BBOX_FORMAT)

# times = {'json':[0.0,0], 'all':[0.0,0]}
class FlightControlThread:
    def __init__(self):

        s = socket(AF_INET, SOCK_DGRAM)
        s.bind(FCSERVER_ADDR)
        s.settimeout(6)
        self.serverstream = s

        s = socket(AF_INET, SOCK_DGRAM)
        self.outputstream = s

        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        self.t = Thread(target=self.update, args=())
        self.t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while not self.stopped:
            try:
                ret, addr = self.serverstream.recvfrom(BBOX_SIZE)

                frame_id, frame_w, frame_h, x, y, w, h = struct.unpack(BBOX_FORMAT, ret)
                output(frame_id, "fcs recv")
                # times['all'][0] += (time.time() - frame_id/1000); times['all'][1] += 1


                # start = time.time()
                # j_str = json.dumps({"fid": frame_id, "bbox_x": x, "bbox_y": y, "bbox_w": w, "bbox_h": h})
                # self.outputstream.sendto(j_str.encode(), OSERVER_ADDR)
                # times['json'][0] += (time.time()-start); times['json'][1] += 1

                # print("-------RECEIVE--------", frame_id, x, y, w, h)
            except timeout:
                # print("hihihi")
                continue


    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        self.t.join()



def output(status, message):
    outputstream.sendto(json.dumps({"src":"fcs", "status": status, "msg":message}).encode(), OSERVER_ADDR)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: ./program ServerHost ServerPort OutputHost OutputPort")
        exit()


    FCSERVER_ADDR = (sys.argv[1], int(sys.argv[2]))#'192.168.10.1', 25000
    OSERVER_ADDR = (sys.argv[3], int(sys.argv[4]))#'192.168.10.1', 25000
    outputstream = socket(AF_INET, SOCK_DGRAM)
    output(0, "fcs server up")

    print("\n\n[INFO] starting flight control server...")
    fcs = FlightControlThread().start()

    try:
        while True: time.sleep(5)

    except KeyboardInterrupt:
        pass
    finally:
        print("\n\n[INFO] stopped flight control server...")
        fcs.stop()
        output(1, "fcs all down")

    # for t in times:
    #     ts = times[t]
    #     print("latency of ", t, ts[0]/ts[1])

