
from pymongo import MongoClient
from PIL import Image
import io

import multiprocessing

from time import sleep
import numpy as np
import cv2
import os
import sys

PATH = os.path.dirname(os.path.realpath(__file__))
live_path = PATH+"/live/"
isExist = os.path.exists(live_path)
sys.path.append(PATH+'/../Face_Image_Scanner/')
import detector as Detector

lock = multiprocessing.Lock()
proteced_image_paths = []
pool = multiprocessing.Pool()

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
        # Clear image buffer from feed
        imageBufferCleaner(PATH+"/live/")

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
    vc.release()

# async thread that has a lock. It uses the detector to detect faces
def detectFace(image_path):
    proteced_image_paths.append(image_path)
    if(lock.acquire(block=False) ):
        print("<lock aquired>")
        try:
            # scan for face
            is_new_face, face_id= Detector.recognize_faces(image_path, "hog", False)
            if(is_new_face):
                Detector.encode_new_faces()

            # log this scan to mongodb
            if(face_id != None):
                URI="mongodb://root:example@mongo:27017/"
                client = MongoClient(URI);
                db = client.Face_Tracker
                images = db.Face_Logs

                im = Image.open("./image.jpg")
                image_bytes = io.BytesIO()
                im.save(image_bytes, format='JPEG')

                image = {
                    'data': image_bytes.getvalue()
                }

                image_id = images.insert_one(image).inserted_id

                client.close()

        except Exception as e:
            print(e)

        
       
        sleep(1)
        lock.release()
        print("<lock released>")
    proteced_image_paths.remove(image_path)

# a function that will clean up the image folder buffer
def imageBufferCleaner(buffer_path):
    for path in os.listdir(buffer_path):
        file_path = os.path.join(buffer_path, path)

        if(not file_path in proteced_image_paths):
            os.remove(file_path)

Recorder()