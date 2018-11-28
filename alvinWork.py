# -*- coding: utf-8 -*-
"""
EECS 332 Fruit Ninja Final Project
written by Alvin Tan

This file will eventually include declarations for objects and a live-stream
with the ability to overlay randomly generated objects over it.
"""

import cv2
import numpy

GRAVITY = 2
NUMFRUITS = 3

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
    

""" ACTUAL CODE STARTS HERE """

fruits = []
fruits.append(Fruit(5, (0, 0, 255), 0, 0, 4, 0))
fruits.append(Fruit(8, (255, 0, 0), 30, 50, 10, -2))

cv2.namedWindow("Fruit Ninja")
vidFeed = cv2.VideoCapture(0)

if vidFeed.isOpened():
    gotFrame, frame = vidFeed.read()
else:
    gotFrame = False

x0 = int(vidFeed.get(3)) # Gets the width of the video feed
y0 = int(vidFeed.get(4)) # Gets the length of the video feed

fruits = []

for count in range(NUMFRUITS):
    radius = numpy.random.randint(20, 70)
    color = (numpy.random.randint(255), numpy.random.randint(255), numpy.random.randint(255))
    xPos = numpy.random.randint(x0)
    yPos = y0
    xVel = int(((x0/2)-xPos)//10)
    yVel = -numpy.random.randint(y0//20, y0//10)
    fruits.append(Fruit(radius, color, xPos, yPos, xVel, yVel))

while gotFrame:
    for count in range(NUMFRUITS):
        fruits[count].draw(frame)
        if not fruits[count].doPhysics(x0, y0):
            print("a fruit died")
            radius = numpy.random.randint(20, 70)
            color = (numpy.random.randint(255), numpy.random.randint(255), numpy.random.randint(255))
            xPos = numpy.random.randint(x0)
            yPos = y0
            xVel = int(((x0/2)-xPos)//10)
            yVel = -numpy.random.randint(y0//20, y0//10)
            fruits[count] = Fruit(radius, color, xPos, yPos, xVel, yVel)
    cv2.imshow("Fruit Ninja", frame)
    gotFrame, frame = vidFeed.read()
    if cv2.waitKey(10) == ord('q'): # Exit on q
        gotFrame = False

print("exited the loop")
vidFeed.release()
print("released video feed")
cv2.destroyAllWindows # For some reason python always crashes here


























