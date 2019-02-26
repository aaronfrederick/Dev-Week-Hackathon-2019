import cv2
import time

def takeImage():
    cap = cv2.VideoCapture(0)
    time.sleep(0.5)

    # Capture frame-by-frame
    ret, frame = cap.read()

    # do what you want with frame
    #  and then save to file
    time.sleep(0.5)
    cv2.imwrite('static/image.png', frame)

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
    return (True)
