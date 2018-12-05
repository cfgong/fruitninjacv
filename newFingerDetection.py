# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 15:52:30 2018

@author: cfg9740
"""

# -*- coding: utf-8 -*-
"""
EECS 332 Fruit Ninja Final Project
written by Alvin Tan

This file will eventually include declarations for objects and a live-stream
with the ability to overlay randomly generated objects over it.
"""

import cv2
import numpy as np

GRAVITY = 4
NUMFRUITS = 3
FONT = cv2.FONT_HERSHEY_COMPLEX
FONT_SIZE = 1.5
STALL = 5
CIRCLE_SIZE = 10

# These determine the positions to generate "exploded" bits of the fruit
EXX = [1, 0.70711, 0, -0.70711, -1, -0.70711, 0, 0.70711]
EXY = [0, 0.70711, 1, 0.70711, 0, -0.70711, -1, -0.70711]
EXV = 8

class Fruit:
    def __init__(this, radius, color, xPos, yPos, xVel, yVel):
        this.radius = radius
        this.color = color
        this.xPos = xPos
        this.yPos = yPos
        this.xVel = xVel
        this.yVel = yVel
        
    def draw(this, frame):
        cv2.circle(frame, (this.xPos, this.yPos), this.radius, this.color, -1)
        
    def doPhysics(this, xBound, yBound):
        this.xPos += this.xVel
        this.yPos += this.yVel
        this.yVel += GRAVITY
        
        return this.xPos >= 0 and this.xPos <= xBound and this.yPos <= yBound
    
    def explode(this, explosions):
        exRad = int(this.radius/2)
        explosions.append(Fruit(exRad, this.color, this.xPos, this.yPos, this.xVel, this.yVel))
        for i in range(8):
            explosions.append(Fruit(exRad, this.color, this.xPos + int(EXX[i]*exRad), this.yPos + int(EXY[i]*exRad), this.xVel + int(EXX[i]*EXV), this.yVel + int(EXY[i]*EXV)))
    
    def isAbove(this, yVal):
        return this.yPos < yVal
    
    def intersects(this, fingerTip):
        return (abs(fingerTip[0] - this.yPos) <= this.radius) and (abs(fingerTip[1] - this.xPos) <= radius)
    
class Text:
    def __init__(this, pos, color, text):
        this.pos = pos
        this.color = color
        this.text = text
        
    def write(this, frame):
        cv2.putText(frame, this.text,this.pos, FONT, FONT_SIZE, this.color, 2, cv2.LINE_AA)
        
"""
code for getting finger tip using contours
"""
def getFingerTip(frame, min_YCrCb, max_YCrCb):
    imageYCrCb = cv2.cvtColor(frame,cv2.COLOR_BGR2YCR_CB)
    skinRegion = cv2.inRange(imageYCrCb,min_YCrCb,max_YCrCb)

    # Do contour detection on skin region
    # contours, hierarchy = cv2.findContours(skinRegion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    im2, contours, hierarchy = cv2.findContours(skinRegion,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
  
    # Draw the contour on the source image
    
    fingerTip = [frame.shape[0], frame.shape[1]] #480 x 640
    # minIndex = [0, 0]

    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        # set some kind of threhold for area
        if area > 100:
            for cval in c:
                if cval[0, 1] < fingerTip[1]:
                    fingerTip = cval[0]
            print(fingerTip)
            
            # draw the contour
            # cv2.drawContours(frame, contours, i, (0, 255, 0), 3)
            
    return fingerTip


"""
use ROI selection to get min and max thresholds
"""
def selectSkin(frame, skinSample, min_YCrCb, max_YCrCb):
    # select the bounding box of the object we want to track (make
    # sure you press ENTER or SPACE after selecting the ROI)
    r = cv2.selectROI("Fruit Ninja", frame, fromCenter=False, showCrosshair=True)
    if max(r) > 0: # make sure a box was actually selected or else we will get an error
        skin = frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        # Convert skin sample image to YCrCb
        skinSample = cv2.cvtColor(skin,cv2.COLOR_BGR2YCR_CB)
        
        min_YCrCb = np.min(skinSample, axis = 1)[0] 
        max_YCrCb = np.max(skinSample, axis = 1)[0] 
    return skinSample, min_YCrCb, max_YCrCb



""" ACTUAL CODE STARTS HERE """
if __name__ == "__main__":
    # We open a new window and open access to the video camera
    vidFeed = cv2.VideoCapture(0)
    
    # If we have successfully connected to the webcam, we grab a frame
    if vidFeed.isOpened():
        gotFrame, frame = vidFeed.read()
    # Otherwise, we cry
    else:
        gotFrame = False
    
    x0 = int(vidFeed.get(3)) # Gets the width of the video feed
    y0 = int(vidFeed.get(4)) # Gets the length of the video feed
    
    # We instantiate an empty list of fruit, to be populated in the following
    # for-statement.
    fruits = []
    explodedBits = []
    
    for count in range(NUMFRUITS):
        # Generates reasonable random values for the initialization of each fruit
        radius = np.random.randint(20, 70)
        color = (np.random.randint(255), np.random.randint(255), np.random.randint(255))
        xPos = np.random.randint(x0)
        yPos = y0
        xVel = int(((x0/2)-xPos)//10)
        yVel = -np.random.randint(y0//20, y0//10)
        fruits.append(Fruit(radius, color, xPos, yPos, xVel, yVel))


    # We start off without a histogram
    test = None
    skinSample = None
    # skin max and min
    min_YCrCb = np.array([0,0,0],np.uint8)
    max_YCrCb = np.array([255,255,255],np.uint8)
        
    # This is the setup time, when we have not yet gotten a histogram yet
    while True:
        frame = cv2.flip(frame, 1)
        # After displaying the frame, we grab a new frame from the video feed
        gotFrame, frame = vidFeed.read()
        
        if skinSample is not None:
            fingerTip = getFingerTip(frame, min_YCrCb, max_YCrCb)
                    
            for count in range(NUMFRUITS):
                # we draw it on screen
                fruits[count].draw(frame)
                
                # Just to test out explosions, if the fruit reaches halfway, it explodes
                if fruits[count].intersects(fingerTip):
                    fruits[count].explode(explodedBits)
                    
                    # generates a new fruit to replace it
                    radius = np.random.randint(20, 70)
                    color = (np.random.randint(255), np.random.randint(255), np.random.randint(255))
                    xPos = np.random.randint(x0)
                    yPos = y0
                    xVel = int(((x0/2)-xPos)//10)
                    yVel = -np.random.randint(y0//20, y0//10)
                    fruits[count] = Fruit(radius, color, xPos, yPos, xVel, yVel)
                
                # and increment the physics. If the fruit goes offscreen, we remove it
                # and implement another randomly generated fruit in its place
                if not fruits[count].doPhysics(x0, y0):
                    #print("a fruit died")
                    radius = np.random.randint(20, 70)
                    color = (np.random.randint(255), np.random.randint(255), np.random.randint(255))
                    xPos = np.random.randint(x0)
                    yPos = y0
                    xVel = int(((x0/2)-xPos)//10)
                    yVel = -np.random.randint(y0//20, y0//10)
                    fruits[count] = Fruit(radius, color, xPos, yPos, xVel, yVel)
        
            for exBit in explodedBits:
                exBit.draw(frame)
                if not exBit.doPhysics(x0, y0):
                    explodedBits.remove(exBit)
        
            # Draw in the detected fingertip for troubleshooting purposes
            cv2.circle(frame,(fingerTip[0], fingerTip[1]), 10, (0,255,0), -1)
        
        # Once all the fruits have been drawn on the frame, we display the frame
        cv2.imshow("Fruit Ninja", frame)
        
        key = cv2.waitKey(STALL) & 0xFF
        # select bounding box for skin sample
        if key == ord("s"):
            skinSample, min_YCrCb, max_YCrCb = selectSkin(frame, skinSample, min_YCrCb, max_YCrCb)
        # quit
        elif key == ord('q'): # Exit on q
            break

# Once an interrupt key is entered, or we fail to get another screen, 
# we print some statements, release the video feed, and close the window.
print("exited the loop")
vidFeed.release()
print("released video feed")
cv2.destroyAllWindows() # For some reason python always crashes here
