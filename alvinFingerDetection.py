#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 13:22:56 2018

@author: Alverino
"""
import cv2
import numpy

def drawRect(frame, x0, y0):
    cv2.rectangle(frame,(int(x0*3/7),int(y0/3)),(int(x0*4/7),int(y0*2/3)),(0,255,0),3)

def getnRG(r, g, b):
    n = r+g+b
    if n != 0:
        rNorm = int(49*(r/n))
        gNorm = int(49*(g/n))
    else:
        rNorm = 0
        gNorm = 0
    return rNorm, gNorm

def makeHisto(frame, x0, y0):
    crop_img = frame[int(y0/3)+3:int(y0*2/3)-3, int(x0*3/7)+3:int(x0*4/7)-3]
    cv2.imshow("cropped", crop_img)

    #print(crop_img)

    # Here we will use a normalized R and G space to do skin tone detection
    RGnorm = numpy.zeros((50, 50))
    x1, y1, z1 = crop_img.shape
    
    for i in range(x1):
        for j in range(y1):
            # Note we need to change the type of the numbers read out of the 
            # image because otherwise n tends to overflow
            r = int(crop_img[i, j, 0])
            g = int(crop_img[i, j, 1])
            b = int(crop_img[i, j, 2])
            
            rNorm, gNorm = getnRG(r, g, b)
            
            #print("r: " + str(r) + ", g: " + str(g) + ", b: " + str(b) + ", n: " + str(n))
            #print("rNorm is: " + str(rNorm))
            #print("gNorm is: " + str(gNorm))
            
            RGnorm[rNorm, gNorm] = RGnorm[rNorm, gNorm] + 1
    
    threshold = numpy.max(RGnorm)/10
    
    nRGbits = numpy.zeros((50, 50))
    
    for i in range(50):
        for j in range(50):
            if RGnorm[i, j] > threshold:
                nRGbits[i, j] = 1
    
    return nRGbits

def findSkin(frame, histBits):
    x1, y1, z1 = frame.shape
    
    skinBits = numpy.zeros((x1, y1))
    
    for i in range(x1):
        for j in range(y1):
            r = int(frame[i, j, 0])
            g = int(frame[i, j, 1])
            b = int(frame[i, j, 2])
            
            rNorm, gNorm = getnRG(r, g, b)
            
            skinBits[i, j] = histBits[rNorm, gNorm]
    
    return skinBits
                

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

# We start off without a histogram
gotHisto = False
histBits = None

# This is the setup time, when we have not yet gotten a histogram yet
while gotFrame and not gotHisto:
    frame = cv2.flip(frame, 1)
    smallFrame = cv2.resize(frame, (int(x0/8), int(y0/8)))
    
    drawRect(frame, x0, y0)
    
    # Once all the fruits have been drawn on the frame, we display the frame
    cv2.imshow("Finger Detection", frame)
    cv2.imshow("Small Frame", smallFrame)
    
    # Then, pause for 10 ms to see if we entered an interrupt key or not
    key = cv2.waitKey(10)
    if key == ord('q'): # Exit on 'q'
        gotFrame = False
    elif key == ord('h'): # Create skin histogram on 'h'
        histBits = makeHisto(frame, x0, y0)
        gotHisto = True
        
    # After displaying the frame, we grab a new frame from the video feed
    gotFrame, frame = vidFeed.read()

# This is after we got a histogram. Then we actually start finger detection
while gotFrame:
    frame = cv2.flip(frame, 1)
    smallFrame = cv2.resize(frame, (int(x0/8), int(y0/8)))
    
    smallFrame = findSkin(smallFrame, histBits)
    
    cv2.imshow("Finger Detection", frame)
    cv2.imshow("Small Frame", smallFrame)
    
    # After displaying the frame, we grab a new frame from the video feed
    gotFrame, frame = vidFeed.read()

# Once an interrupt key is entered, or we fail to get another screen, 
# we print some statements, release the video feed, and close the window.
print("exited the loop")
vidFeed.release()
print("released video feed")
cv2.destroyAllWindows # For some reason python always crashes here