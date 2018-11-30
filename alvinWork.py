# -*- coding: utf-8 -*-
"""
EECS 332 Fruit Ninja Final Project
written by Alvin Tan

This file will eventually include declarations for objects and a live-stream
with the ability to overlay randomly generated objects over it.
"""

import cv2
import numpy

GRAVITY = 4
NUMFRUITS = 3
FONT = cv2.FONT_HERSHEY_COMPLEX
FONT_SIZE = 1.5

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
    
class Text:
    def __init__(this, pos, color, text):
        this.pos = pos
        this.color = color
        this.text = text
        
    def write(this, frame):
        cv2.putText(frame, this.text,this.pos, FONT, FONT_SIZE, this.color, 2, cv2.LINE_AA)
        
""" ACTUAL CODE STARTS HERE """

# We open a new window and open access to the video camera
cv2.namedWindow("Fruit Ninja")
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
    radius = numpy.random.randint(20, 70)
    color = (numpy.random.randint(255), numpy.random.randint(255), numpy.random.randint(255))
    xPos = numpy.random.randint(x0)
    yPos = y0
    xVel = int(((x0/2)-xPos)//10)
    yVel = -numpy.random.randint(y0//20, y0//10)
    fruits.append(Fruit(radius, color, xPos, yPos, xVel, yVel))

while gotFrame:
    # Flips the frame horizontally so it's a mirror image. Makes sense while
    # facing the screen.
    frame = cv2.flip(frame, 1)
    
    # For each fruit we have,
    for count in range(NUMFRUITS):
        # we draw it on screen
        fruits[count].draw(frame)
        
        # Just to test out explosions, if the fruit reaches halfway, it explodes
        if fruits[count].isAbove(y0/2):
            fruits[count].explode(explodedBits)
            
            # generates a new fruit to replace it
            radius = numpy.random.randint(20, 70)
            color = (numpy.random.randint(255), numpy.random.randint(255), numpy.random.randint(255))
            xPos = numpy.random.randint(x0)
            yPos = y0
            xVel = int(((x0/2)-xPos)//10)
            yVel = -numpy.random.randint(y0//20, y0//10)
            fruits[count] = Fruit(radius, color, xPos, yPos, xVel, yVel)
        
        # and increment the physics. If the fruit goes offscreen, we remove it
        # and implement another randomly generated fruit in its place
        if not fruits[count].doPhysics(x0, y0):
            #print("a fruit died")
            radius = numpy.random.randint(20, 70)
            color = (numpy.random.randint(255), numpy.random.randint(255), numpy.random.randint(255))
            xPos = numpy.random.randint(x0)
            yPos = y0
            xVel = int(((x0/2)-xPos)//10)
            yVel = -numpy.random.randint(y0//20, y0//10)
            fruits[count] = Fruit(radius, color, xPos, yPos, xVel, yVel)

    for exBit in explodedBits:
        exBit.draw(frame)
        if not exBit.doPhysics(x0, y0):
            explodedBits.remove(exBit)


    # Once all the fruits have been drawn on the frame, we display the frame
    cv2.imshow("Fruit Ninja", frame)
    
    # After displaying the frame, we grab a new frame from the video feed
    gotFrame, frame = vidFeed.read()
    
    # Then, pause for 10 ms to see if we entered an interrupt key or not
    if cv2.waitKey(10) == ord('q'): # Exit on q
        gotFrame = False

# Once an interrupt key is entered, or we fail to get another screen, 
# we print some statements, release the video feed, and close the window.
print("exited the loop")
vidFeed.release()
print("released video feed")
cv2.destroyAllWindows # For some reason python always crashes here


























