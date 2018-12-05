# -*- coding: utf-8 -*-
"""
EECS 332 Fruit Ninja Final Project
written by Alvin Tan

This file will eventually include declarations for objects and a live-stream
with the ability to overlay randomly generated objects over it.
"""

import cv2
import numpy
import alvinFingerDetection as aFD
import gameObjects as gO

STALL = 5

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

# Here we instantiate our levels:
levels = []
levels.append(gO.Level(1, 2, 0, 100))
levels.append(gO.Level(3, 5, 0, 100))
levels.append(gO.Level(3, 5, 1, 100))
levels.append(gO.Level(5, 7, 3, 200))

# We instantiate an empty list of fruit, to be populated in the following
# for-statement.
fruits = []
bombs = []
explodedBits = []

for curLevel in range(len(levels)):
    # We generate all of the fruits in this level
    for count in range(levels[curLevel].numFruits):
        fruits.append(gO.randomFruit(x0, y0))
        
    for count in range(levels[curLevel].numBombs):
        bombs.append(gO.randomBomb(x0, y0))
    
    # We start off without a histogram
    gotHisto = False
    histBits = None
        
    # This is the setup time, when we have not yet gotten a histogram yet
    while gotFrame and not gotHisto:
        frame = cv2.flip(frame, 1)
        
        aFD.drawRect(frame, x0, y0)
            
        # Once all the fruits have been drawn on the frame, we display the frame
        cv2.imshow("Fruit Ninja", frame)
            
        # Then, pause for 10 ms to see if we entered an interrupt key or not
        key = cv2.waitKey(STALL)
        if key == ord('q'): # Exit on 'q'
            break
        elif key == ord('h'): # Create skin histogram on 'h'
            histBits = aFD.makeHisto(frame, x0, y0)
            gotHisto = True
            
        # After displaying the frame, we grab a new frame from the video feed
        gotFrame, frame = vidFeed.read()
    
    while gotFrame:
        # Flips the frame horizontally so it's a mirror image. Makes sense while
        # facing the screen.
        frame = cv2.flip(frame, 1)
        
        # Grab the coordinate of the player's fingertip
        fingerTip = aFD.getFingerTip(frame, x0, y0, histBits)
        
        # For each fruit we have,
        for count in range(NUMFRUITS):
            # we draw it on screen
            fruits[count].draw(frame)
            
            # Just to test out explosions, if the fruit reaches halfway, it explodes
            if fruits[count].intersects(fingerTip):
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
    
        # Draw in the detected fingertip for troubleshooting purposes
        cv2.circle(frame,(fingerTip[1], fingerTip[0]), 10, (0,255,0), -1)
    
        # Once all the fruits have been drawn on the frame, we display the frame
        cv2.imshow("Fruit Ninja", frame)
        
        # After displaying the frame, we grab a new frame from the video feed
        gotFrame, frame = vidFeed.read()
        
        # Then, pause for 10 ms to see if we entered an interrupt key or not
        if cv2.waitKey(STALL) == ord('q'): # Exit on q
            break
    
    # Once an interrupt key is entered, or we fail to get another screen, 
    # we print some statements, release the video feed, and close the window.
    print("exited the loop")
    vidFeed.release()
    print("released video feed")
    cv2.destroyAllWindows # For some reason python always crashes here


























