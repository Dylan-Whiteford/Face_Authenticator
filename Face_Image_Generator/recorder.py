import numpy as np
import cv2
import os
import sys

PATH = os.path.dirname(os.path.realpath(__file__))
live_path = PATH+"/live/"
isExist = os.path.exists(live_path)
sys.path.append(PATH+'/../Face_Image_Scanner/')
import detector as Detector


def Recorder():
    
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(live_path)
    else:
        # Clear buffer
        for f in os.listdir(live_path):
            os.remove(live_path+"/"+f)

    cv2.namedWindow("preview")
    vc = cv2.VideoCapture(0)
    count = 0
    if vc.isOpened(): # try to get the first frame
        rval, frame = vc.read()
    else:
        rval = False

    while rval:

        # Clear image buffer from feed
        if(count >= 10):
            path = PATH+"/live/frame%d.jpg"%(count-10)
            os.remove(path)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        name = PATH+"/live/frame%d.jpg"%count
        cv2.imwrite(name, frame)
        count +=1
        cv2.imshow("frame", gray)
            
        rval, frame = vc.read()
        key = cv2.waitKey(20)
        if key == 27: # exit on ESC
            break
    vc.release()

def detectFace():
    pass


Recorder()
