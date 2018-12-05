# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 14:54:24 2018

@author: cfg9740
"""
# import the necessary packages
import numpy as np
import cv2

SMALL_SCALE = 16
GRAVITY = 4
NUMFRUITS = 3
FONT = cv2.FONT_HERSHEY_COMPLEX
FONT_SIZE = 1.5
STALL = 5

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

def findHighest(frame):
    x1, y1 = frame.shape
    
    for i in range(x1):
        for j in range(y1):
            if frame[i, j] != 0:
                return [i, j]

    return [0, 0]

if __name__ == "__main__":
    test = None
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
            x0 = int(videoFrame.get(3)) # Gets the width of the video feed
            y0 = int(videoFrame.get(4)) # Gets the length of the video feed
            
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
            # Find region with skin tone in YCrCb image
            imageYCrCb = cv2.cvtColor(frame,cv2.COLOR_BGR2YCR_CB)
            skinRegion = cv2.inRange(imageYCrCb,min_YCrCb,max_YCrCb)
        
            # Do contour detection on skin region
            # contours, hierarchy = cv2.findContours(skinRegion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            im2, contours, hierarchy = cv2.findContours(skinRegion,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
          
            # Draw the contour on the source image
            
            minIndex = [frame.shape[0], frame.shape[1]] #480 x 640
            # minIndex = [0, 0]
        
            for i, c in enumerate(contours):
                area = cv2.contourArea(c)
                # set some kind of threhold for area
                if area > 100:
                    for cval in c:
                        if cval[0, 1] < minIndex[1]:
                            minIndex = cval[0]
                    print(minIndex)
                    
                    # draw the contour
                    # cv2.drawContours(frame, contours, i, (0, 255, 0), 3)
                    
            cv2.circle(frame, (minIndex[0], minIndex[1]), SMALL_SCALE, 3, thickness=-1, lineType=8, shift=0) 
            
            ### TO DO
            ### make an intersect part 
            for count in range(NUMFRUITS):
                # we draw it on screen
                fruits[count].draw(frame)
                
                # Just to test out explosions, if the fruit reaches halfway, it explodes
                if fruits[count].intersects(minIndex):
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