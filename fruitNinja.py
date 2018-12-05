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

''' First we set up the webcam feed and grab a histogram for skin detection '''

STALL = 5
LEVEL_START_PAUSE = 10

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

# We generate our skin-tone histogram here
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

''' Now we are ready to begin our gameplay '''

# Here we instantiate our levels:
levels = []
levels.append(gO.Level(1, 2, 0, 100))
levels.append(gO.Level(3, 5, 0, 100))
levels.append(gO.Level(3, 5, 1, 100))
levels.append(gO.Level(5, 7, 3, 200))

# We instantiate our score and our lives
score = 0
lives = 3
gameOver = False

# For each of the levels, we do game stuff
for curLevel in range(len(levels)):
    # We instantiate our game objects
    texts = []
    fruits = []
    bombs = []
    explodedBits = []

    # We generate the text for this level
    texts.append(gO.Text((10, 10), (0, 0, 0), "Lives: "))
    texts.append(gO.Text((int(x0/2)-20, 10), (0, 0, 0), "Level: " + str(curLevel)))
    texts.append(gO.Text((x0 - 50, 10), (0, 0, 0), "Score: "+str(score)))
    
    # We generate all of the fruits in this level
    for count in range(levels[curLevel].numFruits):
        fruits.append(gO.randomFruit(x0, y0))
    
    # We generate all of the bombs in this level
    for count in range(levels[curLevel].numBombs):
        bombs.append(gO.randomBomb(x0, y0))
    
    startPause = 0
    while (startPause < LEVEL_START_PAUSE) and gotFrame:
        # Flips the frame horizontally so it's a mirror image. Makes sense while
        # facing the screen.
        frame = cv2.flip(frame, 1)
        for text in texts:
            text.write(frame)
        
        cv2.imshow("Fruit Ninja", frame)
        startPause += 1
        
        # After displaying the frame, we grab a new frame from the video feed
        gotFrame, frame = vidFeed.read()
        # Then, pause for 10 ms to see if we entered an interrupt key or not
        if cv2.waitKey(STALL) == ord('q'): # Exit on q
            gotFrame = False
            break
    
    while gotFrame and not gameOver:
        # Flips the frame horizontally so it's a mirror image. Makes sense while
        # facing the screen.
        frame = cv2.flip(frame, 1)
        
        # Grab the coordinate of the player's fingertip
        fingerTip = aFD.getFingerTip(frame, x0, y0, histBits)
        
        # For each fruit we have,
        for count in range(len(fruits)):
            # we draw it on screen
            fruits[count].draw(frame)
            
            # If our fintertip intersects with the fruit, we explode the fruit
            if fruits[count].intersects(fingerTip):
                fruits[count].explode(explodedBits)
                
                # Update the score and display the new score
                score += levels[curLevel].pointsPerFruit
                texts[2] = gO.Text((x0 - 50, 10), (0, 0, 0), "Score: "+str(score))
                
                # Generate a new fruit to replace it
                fruits[count] = gO.randomFruit(x0, y0)
            
            # and increment the physics. If the fruit goes offscreen, we remove it
            # and implement another randomly generated fruit in its place
            if not fruits[count].doPhysics(x0, y0):
                fruits[count] = gO.randomFruit(x0, y0)
        
        # For each bomb we have,
        for count in range(len(bombs)):
            # we draw it on screen
            bombs[count].draw(frame)
            
            # If our fingertip intersects with the bomb, we explode the bomb
            if bombs[count].intersects(fingerTip):
                bombs[count].explode(explodedBits)
                
                # Update the number of lives and checks if you are dead
                lives -= 1
                if lives <= 0:
                    gameOver = True
                
                # Generates a new bomb to replace it
                bombs[count] = gO.randomBomb(x0, y0)
            
            # and increment the physics
            if not bombs[count].doPhysics(x0, y0):
                bombs[count] = gO.randomBomb(x0, y0)
        
        # Write all of our text on the screen
        for text in texts:
            text.write(frame)
            
            ''' CONTINUE FROM HERE '''
        
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


























