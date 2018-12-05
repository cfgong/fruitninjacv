#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 13:22:56 2018

@author: Alverino
"""
import cv2
import numpy
import morophological_operators as mo
from ccl import CCL

STALL = 2
THRESH = 0.1
SMALL_SCALE = 16

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
    #cv2.imshow("cropped", crop_img)

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
    
    threshold = numpy.max(RGnorm)*THRESH
    
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
                
def processSkin(frame):
    frame = CCL(frame, 3)
    #noiseSE = numpy.ones((2, 2))
    '''
    SE = numpy.array([[0, 0, 1, 1, 0, 0],
                      [0, 1, 1, 1, 1, 0],
                      [1, 1, 1, 1, 1, 1],
                      [1, 1, 1, 1, 1, 1],
                      [0, 1, 1, 1, 1, 0],
                      [0, 0, 1, 1, 0, 0]])
    '''
    SE = numpy.ones((4, 4))
    #frame = mo.Closing(frame, noiseSE)
    #frame = mo.Erosion(frame, noiseSE)
    #frame = mo.Dilation(frame, SE)
    #frame = mo.Closing(frame, SE)
    #frame = mo.Erosion(frame, SE)
    frame = mo.Closing(frame, SE)
    frame = CCL(frame, 40)
    return frame

def findCenter(frame):
    x1, y1 = frame.shape
    
    xCum = 0
    yCum = 0
    numPix = 0
    
    for i in range(x1):
        for j in range(y1):
            if frame[i, j] != 0:
                xCum += i
                yCum += j
                numPix += 1
    
    if numPix != 0:
        return [int(xCum/numPix), int(yCum/numPix)]
    else:
        return [int(x1/2), int(y1/2)]
    
def findFurthest(frame, center):
    x1, y1 = frame.shape
    
    maxPoint = [0, 0]
    maxDist = 0
    
    for i in range(center[0] - 2):
        for j in range(y1):
            if frame[i, j] != 0 and ((i - center[0])^2 + (j - center[1])^2) > maxDist:
                maxPoint = [i, j]
                maxDist = ((i - center[0])^2 + (j - center[1])^2)
    
    return maxPoint

def findHighest(frame):
    x1, y1 = frame.shape
    
    for i in range(x1):
        for j in range(y1):
            if frame[i, j] != 0:
                return [i, j]

    return [0, 0]

def findContourTip(cleanSkin):
    ''' @ Crystal '''

def getFingerTip(frame, x0, y0, histBits):
    smallFrame = cv2.resize(frame, (int(x0/SMALL_SCALE), int(y0/SMALL_SCALE)))
        
    skinFrame = findSkin(smallFrame, histBits)
    cleanSkin = processSkin(skinFrame)
    highest = findHighest(cleanSkin)
    #highest = findContourTip(cleanSkin)
    
    return [highest[0]*SMALL_SCALE, highest[1]*SMALL_SCALE]

if __name__ == "__main__":
    # We open a new window and open access to the video camera
    cv2.namedWindow("Finger Detection")
    vidFeed = cv2.VideoCapture(0)
    gotFrame = True
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
        key = cv2.waitKey(STALL)
        if key == ord('q'): # Exit on 'q'
            break
        elif key == ord('h'): # Create skin histogram on 'h'
            histBits = makeHisto(frame, x0, y0)
            gotHisto = True
            
        # After displaying the frame, we grab a new frame from the video feed
        gotFrame, frame = vidFeed.read()
    
    # This is after we got a histogram. Then we actually start finger detection
    while gotFrame:
        frame = cv2.flip(frame, 1)
        smallFrame = cv2.resize(frame, (int(x0/SMALL_SCALE), int(y0/SMALL_SCALE)))
        
        skinFrame = findSkin(smallFrame, histBits)
        cleanSkin = processSkin(skinFrame)
        center = findCenter(cleanSkin)
        fingerTip = findFurthest(cleanSkin, center)
        highest = findHighest(cleanSkin)
        
        cv2.circle(frame,(center[1]*SMALL_SCALE, center[0]*SMALL_SCALE), 10, (0,0,255), -1)
        cv2.circle(frame,(fingerTip[1]*SMALL_SCALE, fingerTip[0]*SMALL_SCALE), 10, (255,0,0), -1)
        cv2.circle(frame,(highest[1]*SMALL_SCALE, highest[0]*SMALL_SCALE), 10, (0,255,0), -1)
        
        cv2.imshow("Finger Detection", frame)
        cv2.imshow("Small Frame", smallFrame)
        cv2.imshow("Skin Frame", skinFrame)
        cv2.imshow("Clean Skin", cleanSkin)
        
        if cv2.waitKey(STALL) == ord('q'):
            break
        
        # After displaying the frame, we grab a new frame from the video feed
        gotFrame, frame = vidFeed.read()
    
    # Once an interrupt key is entered, or we fail to get another screen, 
    # we print some statements, release the video feed, and close the window.
    print("exited the loop")
    vidFeed.release()
    print("released video feed")
    cv2.destroyAllWindows() # For some reason python always crashes here