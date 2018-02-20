import cv2
import sys, os
import psutil
process = psutil.Process(os.getpid())

isOpenWindow = False

def detect(cascade, filename):
    isFile = True
    try:
        filename = int(filename)
        isFile = False
    except:
        pass

    camera = cv2.VideoCapture(filename)

    if isFile:
        total_frame = camera.get(cv2.CAP_PROP_FRAME_COUNT)

    if isOpenWindow:
        cv2.namedWindow('image',cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', 800,600)

    times = []
    mem_usage = []
    cpu_usage = []

    print("ready")
    frame_index = 1
    while True:
        (grabbed, frame) = camera.read()

        if not grabbed:
            print("\nVideo ended")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)


        # Start timer
        timer = cv2.getTickCount()
        rects = cascade.detectMultiScale(gray,
            scaleFactor = 1.1,
            # minNeighbors = 5,
            minNeighbors = 20,
            minSize = (5, 10),
            maxSize = (450,720),
            flags = 0|cv2.CASCADE_SCALE_IMAGE)
        #print("I found {} face(s)".format(len(rects)))

        # Calculate Frames per second (FPS)
        freq = cv2.getTickFrequency()
        count = (cv2.getTickCount() - timer)
        mem_usage.append(process.memory_info()[0] / float(2 ** 20))
        cpu_usage.append(process.cpu_percent())

        if rects != ():
            times.append(count/freq)
            print("\n", rects, count/freq, freq/count)

        if isOpenWindow:
            for (fX, fY, fW, fH) in rects:
                # print("{} - {} - {} - {}".format(fX, fY, fW, fH))
                cv2.rectangle(frame, (fX, fY), (fX+ fW, fY + fH), (0, 0, 255), 3)

            cv2.imshow("image", frame)

        if isFile:
            print("\r %.2f%% (%d/%d)" % (100.0*frame_index/total_frame, frame_index, total_frame), end="")

        frame_index += 1

        if isOpenWindow:
            if cv2.waitKey(1) & 0xFF == 27:
                break

    camera.release()
    cv2.destroyAllWindows()
    return times, mem_usage, cpu_usage


filename = sys.argv[2]
if sys.argv[1] == "face":
    cascade = cv2.CascadeClassifier("./data/haarcascades/haarcascade_frontalface_default.xml")
elif sys.argv[1] == "ped":
    cascade = cv2.CascadeClassifier("./data/lbpcascades/lbp_pedestrian.xml")
else:
    print("python3 detection.py [ped|face] <video filename>")
    exit()

times, mem_usage, cpu_usage = detect(cascade,filename)

print("\ntime", sum(times)/len(times))
print("FPS", len(times)/sum(times))
print("[INFO] MEM usage: {:.2f}MiB".format(sum(mem_usage)/len(mem_usage)))
print("[INFO] CPU usage: {:.2f}%".format(sum(cpu_usage)/len(cpu_usage)))