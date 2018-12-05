# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 14:54:24 2018

@author: cfg9740
"""
# import the necessary packages
import numpy as np
import cv2

def findHighest(frame):
    x1, y1 = frame.shape
    
    for i in range(x1):
        for j in range(y1):
            if frame[i, j] != 0:
                return [i, j]

    return [0, 0]

if __name__ == "__main__":

    skinSample = None
    # skin max and min
    min_YCrCb = np.array([0,133,77],np.uint8)
    max_YCrCb = np.array([255,173,127],np.uint8)
    
    print("Starting video stream...")
    
    # Get pointer to video frames from primary device
    videoFrame = cv2.VideoCapture(0)
    
    # loop over frames from the video stream
    while True:
        # Grab video frame, decode it and return next video frame
        readSuccess, frame = videoFrame.read()
        
        if skinSample is not None:
            # Find region with skin tone in YCrCb image
            imageYCrCb = cv2.cvtColor(frame,cv2.COLOR_BGR2YCR_CB)
            skinRegion = cv2.inRange(imageYCrCb,min_YCrCb,max_YCrCb)
        
            # Do contour detection on skin region
            # contours, hierarchy = cv2.findContours(skinRegion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            im2, contours, hierarchy = cv2.findContours(skinRegion,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            print(contours)
            # Draw the contour on the source image
            for i, c in enumerate(contours):
                area = cv2.contourArea(c)
                # if area > 1000:
                cv2.drawContours(frame, contours, i, (0, 255, 0), 3)
                    
        # show the output frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
    
        # if the 's' key is selected, we are going to "select" a bounding
        # box to track
        if key == ord("s"):
            # select the bounding box of the object we want to track (make
            # sure you press ENTER or SPACE after selecting the ROI)
            r = cv2.selectROI("Frame", frame, fromCenter=False,
                showCrosshair=True)
            if max(r) > 0: # make sure a box was actually selected or else we will get an error
                skin = frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
                # Convert image to YCrCb
                imageYCrCb = cv2.cvtColor(frame,cv2.COLOR_BGR2YCR_CB)
                skinSample = cv2.cvtColor(skin,cv2.COLOR_BGR2YCR_CB)
                
                min_YCrCb = np.min(skinSample, axis = 1)[0] 
                max_YCrCb = np.max(skinSample, axis = 1)[0] 
        # if the `q` key was pressed, break from the loop
        elif key == ord("q"):
            break
    
    # if we are using a webcam, release the pointer
    videoFrame.release()
    # close all windows
    cv2.destroyAllWindows()