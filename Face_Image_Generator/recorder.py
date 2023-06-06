
import pymongo
from PIL import Image
import io
import socket

import multiprocessing

from time import sleep
import numpy as np
import cv2
import os
import sys
import datetime
PATH = os.path.dirname(os.path.realpath(__file__))
live_path = PATH+"/live/"
isExist = os.path.exists(live_path)
sys.path.append(PATH+'/../Face_Image_Scanner/')
import detector as Detector

#Parrellism Libs
lock = multiprocessing.Lock()
pool = multiprocessing.Pool()

try:
    client = pymongo.MongoClient("mongodb://root:example@localhost:27017/")
    db = client["Face_Tracker"]
    timeseries= {
        "timeField": "timestamp",
        "metaField": "metadata",
        "granularity": "seconds"
    }
    db.createCollection("Face_Log", timeseries, False )

except Exception as err:
    # do whatever you need
    print(err)



def Recorder():


    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(live_path)
    else:
        # Clear buffer
        for f in os.listdir(live_path):
            os.remove(live_path+"/"+f)

    vc = cv2.VideoCapture(0)
    count = 0
    if vc.isOpened(): # try to get the first frame
        rval, frame = vc.read()
    else:
        rval = False

    while rval:

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        image_path = PATH+"/live/frame%d.jpg"%count

        cv2.imwrite(image_path, frame)

        count +=1
        cv2.imshow("frame",gray)
            
        # create thread to run face scan 
        pool.apply_async(detectFace, (image_path,))

        rval, frame = vc.read()
        key = cv2.waitKey(20)
        if key == 27: # exit on ESC
            break
    
    client.close()
    vc.release()

# Thread that has a lock. It uses the detector to detect faces
def detectFace(image_path):
    if(lock.acquire(block=False) ):
        print("<lock aquired>")
        try:
            # scan for face
            is_new_face, face_id= Detector.recognize_faces(image_path, "hog", False)
            if(is_new_face):
                Detector.encode_new_faces()

            # log this scan to mongodb
            if(face_id != None):
                print("Attempting to log face detection")

                face_logs = db["Face_Log"]
                # print(face_logs[0])
                # print("Loaded Collection")
                im = Image.open(image_path)
                image_bytes = io.BytesIO()
                im.save(image_bytes, format='JPEG')
                
                log = {
                    'time_captured': datetime.datetime.now(),
                    'face_id': face_id,
                    'img': image_bytes.getvalue(),
                    'agent': socket.gethostname(),
                    'geo-data': 'mock-geo-data'
                }

                image_id = face_logs.insert_one(log)


            # Clear image buffer from feed
            imageBufferCleaner(PATH+"/live/",image_path)

        except Exception as e:
            print(e)

        
       
        sleep(1)
        lock.release()
        print("<lock released>")

# a function that will clean up the image folder buffer
def imageBufferCleaner(buffer_path,protected_path):
    for path in os.listdir(buffer_path):
        file_path = os.path.join(buffer_path, path)
        if(not file_path == protected_path):
            os.remove(file_path)

Recorder()