import cv2
import sys
camera = cv2.VideoCapture(sys.argv[1])
faceCascade = cv2.CascadeClassifier("./data/lbpcascades/lbp_pedestrian.xml")

cv2.namedWindow('image',cv2.WINDOW_NORMAL)
cv2.resizeWindow('image', 800,600)

times = []
while True:
    (grabbed, frame) = camera.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    # Start timer
    timer = cv2.getTickCount()
    faceRects = faceCascade.detectMultiScale(gray,
        scaleFactor = 1.1,
        # minNeighbors = 5,
        minNeighbors = 20,
        minSize = (5, 10),
        maxSize = (450,720),
        flags = 0|cv2.CASCADE_SCALE_IMAGE)
    #print("I found {} face(s)".format(len(faceRects)))

    # Calculate Frames per second (FPS)
    freq = cv2.getTickFrequency()
    count = (cv2.getTickCount() - timer)

    if faceRects != ():
        times.append(count/freq)
        print(faceRects, count/freq, freq/count)

    for (fX, fY, fW, fH) in faceRects:
        # print("{} - {} - {} - {}".format(fX, fY, fW, fH))
        cv2.rectangle(frame, (fX, fY), (fX+ fW, fY + fH), (0, 0, 255), 3)

    cv2.imshow("image", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()

print("time", sum(times)/len(times))
print("FPS", len(times)/sum(times))