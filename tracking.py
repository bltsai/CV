import cv2
import sys, os
import psutil
process = psutil.Process(os.getpid())
import ast

(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

isOpenWindow = False

if __name__ == '__main__' :

    # Set up tracker.
    # Instead of MIL, you can also use

    tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN']
    tracker_type = tracker_types[int(sys.argv[1])]

    if int(minor_ver) < 3:
        tracker = cv2.Tracker_create(tracker_type)
    else:
        if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
        if tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
        if tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        if tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
        if tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
        if tracker_type == 'GOTURN':
            tracker = cv2.TrackerGOTURN_create()

    # Read video
    isFile = True
    try:
        filename = int(sys.argv[2])
        isFile = False
    except:
        filename = sys.argv[2]

    video = cv2.VideoCapture(filename)

    if isFile:
        total_frame = video.get(cv2.CAP_PROP_FRAME_COUNT)

    # Exit if video not opened.
    if not video.isOpened():
        print ("Could not open video")
        sys.exit()

    # Read first frame.
    ok, frame = video.read()
    if not ok:
        print ('Cannot read video file')
        sys.exit()

    # Define an initial bounding box
    info = {"chaplin.mp4": (164, 23, 94, 295),
            "street_360p.mp4": (111, 118, 15, 64),
            "street_720p.mp4": (223, 236, 30, 128),
            "street_1080p.mp4": (335, 354, 45, 192)
            }

    try:
        bbox = ast.literal_eval(sys.argv[3])
    except:
        if sys.argv[2] in info:
            bbox = info[sys.argv[2]]
        else:
            bbox = cv2.selectROI(frame, False)

    # Uncomment the line below to select a different bounding box
    print(bbox)

    # Initialize tracker with first frame and bounding box
    ok = tracker.init(frame, bbox)

    times = []
    mem_usage = []
    cpu_usage = []
    print("ready")
    frame_index = 2
    while True:
        # Read a new frame
        ok, frame = video.read()
        if not ok:
            break

        # Start timer
        timer = cv2.getTickCount()

        # Update tracker
        ok, bbox = tracker.update(frame)

        # Calculate Frames per second (FPS)
        freq = cv2.getTickFrequency()
        count = (cv2.getTickCount() - timer)
        mem_usage.append(process.memory_info()[0] / float(2 ** 20))
        cpu_usage.append(process.cpu_percent())

        fps = freq / count



        # Draw bounding box
        if ok:
            # Tracking success
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            if isOpenWindow:
                cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
            times.append(count/freq)

            print("\n", bbox)
        elif isOpenWindow:
            # Tracking failure
            cv2.putText(frame, "Tracking failure detected", (100,80), cv2.FONT_HERSHEY_SIMPLEX, 0.75,(0,0,255),2)


        if isOpenWindow:
            # Display tracker type on frame
            cv2.putText(frame, tracker_type + " Tracker", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);

            # Display FPS on frame
            cv2.putText(frame, "FPS : " + str(int(fps)), (100,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50), 2);

            # Display result
            cv2.imshow("Tracking", frame)


        if isFile:
            print("\r %.2f%% (%d/%d)" % (100.0*frame_index/total_frame, frame_index, total_frame), end="")

        frame_index += 1

        # Exit if ESC pressed

        if isOpenWindow:
            k = cv2.waitKey(1) & 0xff
            if k == 27 : break


    print("\ntime", sum(times)/len(times))
    print("FPS", len(times)/sum(times))
    print("[INFO] MEM usage: {:.2f}MiB".format(sum(mem_usage)/len(mem_usage)))
    print("[INFO] CPU usage: {:.2f}%".format(sum(cpu_usage)/len(cpu_usage)))