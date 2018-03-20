import cv2
import numpy as np
import struct
import time
import sys
import json
import traceback


FORMAT = "!QHHI"
INT_SIZE = struct.calcsize(FORMAT)
BBOX_FORMAT = "!QHHHHHH"

def recv_into():
    try:
        j_str = sys.stdin.readline().strip('\n')
        d = json.loads(j_str)
        if "FRAME" not in d["type"]:
            output("ERROR", "received is not of type *_FRAME but %s"%d["type"])
            return (None,)*4

        msg = base64.b64decode(d["message"])
        header = msg[:INT_SIZE]
        payload = msg[INT_SIZE:]
        frame_id, frame_w, frame_h, shape_w = struct.unpack(FORMAT, header)

        arr = np.zeros(shape=(shape_w, 1), dtype="uint8")
        view = memoryview(arr).cast('B')
        view[:] = payload

    except Exception as e:
        output("ERROR", traceback.format_exc())
        return (None,)*4

    return frame_id, frame_w, frame_h, arr

def detection():
    cascade = cv2.CascadeClassifier(CASCADE_FILE)

    output("INFO", "detection begin")

    try:
        while True :

            frame_id, frame_w, frame_h, a = recv_into()
            # start = time.time()
            frame = cv2.imdecode(a, 1)

            res = (frame_w, frame_h)

            # times['decode'][0] += (time.time()-start); times['decode'][1] += 1

            # start = time.time()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)

            rects = cascade.detectMultiScale(gray,
                scaleFactor = 1.1,
                # minNeighbors = 5,
                minNeighbors = 20,
                minSize = (50, 50),
                # maxSize = (450,720),
                flags = 1)#0|cv2.CASCADE_SCALE_IMAGE)

            send_str = struct.pack(BBOX_FORMAT, frame_id, frame_w, frame_h, 0, 0, 0, 0)
            if rects != ():
                max_rect_size = 0
                max_rect = None
                for rect in rects:
                    fX, fY, fW, fH = rect
                    # print("{} - {} - {} - {}".format(fX, fY, fW, fH))
                    # cv2.rectangle(frame, (fX, fY), (fX+ fW, fY + fH), (0, 0, 255), 3)
                    if fW * fH > max_rect_size:
                        max_rect = rect
                        max_rect_size = fW*fH

                send_str = struct.pack(BBOX_FORMAT, frame_id, frame_w, frame_h, fX, fY, fW, fH)

            output("BBOX", base64.b64encode(send_str))


            # cv2.imshow("image", frame)
            # cv2.waitKey(1)

    except Exception as e:
        output("ERROR", traceback.format_exc())
        # cv2.destroyAllWindows()

def output(t, message):
    j_str = json.dumps({"type": "DT_"+t, "message":message})
    print(j_str, flush=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        output("Usage", "./program CasscadeFile")
        # exit()
        CASCADE_FILE = "./data/haarcascades/haarcascade_frontalface_default.xml"
    else:
        CASCADE_FILE = sys.argv[1]


    try:
        detection()
    except KeyboardInterrupt:
        output("ERROR","Ctrl-C")

    output("INFO", "Bye bye")
