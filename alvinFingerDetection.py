#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 13:22:56 2018

@author: Alverino
"""
import cv2

def drawRect(frame, x0, y0):
    cv2.rectangle(frame,(int(x0*3/7),int(y0/3)),(int(x0*4/7),int(y0*2/3)),(0,255,0),3)

def makeHisto(frame, x0, y0):
    crop_img = frame[int(y0/3)+3:int(y0*2/3)-3, int(x0*3/7)+3:int(x0*4/7)-3]
    cv2.imshow("cropped", crop_img)

# We open a new window and open access to the video camera
cv2.namedWindow("Finger Detection")
vidFeed = cv2.VideoCapture(0)

# If we have successfully connected to the webcam, we grab a frame
if vidFeed.isOpened():
    gotFrame, frame = vidFeed.read()
# Otherwise, we cry
else:
    gotFrame = False

x0 = int(vidFeed.get(3)) # Gets the width of the video feed
y0 = int(vidFeed.get(4)) # Gets the length of the video feed

smallFrame = cv2.resize(frame, (int(x0/8), int(y0/8)))

while gotFrame:
    frame = cv2.flip(frame, 1)
    
    drawRect(frame, x0, y0)
    
    # Once all the fruits have been drawn on the frame, we display the frame
    cv2.imshow("Finger Detection", frame)
    
    # Then, pause for 10 ms to see if we entered an interrupt key or not
    key = cv2.waitKey(10)
    if key == ord('q'): # Exit on 'q'
        gotFrame = False
    if key == ord('h'): # Create skin histogram on 'h'
        makeHisto(frame, x0, y0)
        
    # After displaying the frame, we grab a new frame from the video feed
    gotFrame, frame = vidFeed.read()

# Once an interrupt key is entered, or we fail to get another screen, 
# we print some statements, release the video feed, and close the window.
print("exited the loop")
vidFeed.release()
print("released video feed")
cv2.destroyAllWindows # For some reason python always crashes here