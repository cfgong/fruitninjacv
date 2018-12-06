#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 16:11:49 2018

@author: Alverino
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
    
    def intersects(this, fingerTip):
        return (abs(fingerTip[0] - this.yPos) <= this.radius) and (abs(fingerTip[1] - this.xPos) <= this.radius)
    
class Bomb(Fruit):
    def __init__(this, radius, color, xPos, yPos, xVel, yVel):
        Fruit.__init__(this, radius, color, xPos, yPos, xVel, yVel)
    
    def draw(this, frame):
        cv2.rectangle(frame, (this.xPos - this.radius, this.yPos - this.radius), (this.xPos + this.radius, this.yPos + this.radius), this.color, -1)
        cv2.putText(frame, "bomb",(this.xPos - this.radius, this.yPos - this.radius), FONT, FONT_SIZE, (255, 255, 255), 2, cv2.LINE_AA)

class Text:
    def __init__(this, pos, color, text):
        this.pos = pos
        this.color = color
        this.text = text
        
    def write(this, frame):
        cv2.putText(frame, this.text,this.pos, FONT, FONT_SIZE, this.color, 2, cv2.LINE_AA)

class Level:
    def __init__(this, numFruits, pointsPerFruit, numBombs, numFrames):
        this.numFruits = numFruits
        this.pointsPerFruit = pointsPerFruit
        this.numBombs = numBombs
        this.numFrames = numFrames
        
def randomFruit(x0, y0):
    # Generates reasonable random values for the initialization of each fruit
    radius = numpy.random.randint(30, 70)
    color = (numpy.random.randint(255), numpy.random.randint(255), numpy.random.randint(255))
    xPos = numpy.random.randint(x0)
    yPos = y0
    xVel = int(((x0/2)-xPos)//10)
    yVel = -numpy.random.randint(y0//20, y0//10)
    return Fruit(radius, color, xPos, yPos, xVel, yVel)

def randomBomb(x0, y0):
    # Generates reasonable random values for the initialization of each fruit
    xPos = numpy.random.randint(x0)
    yPos = y0
    xVel = int(((x0/2)-xPos)//10)
    yVel = -numpy.random.randint(y0//20, y0//10)
    return Bomb(50, (0, 0, 0), xPos, yPos, xVel, yVel)