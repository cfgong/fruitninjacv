# -*- coding: utf-8 -*-
"""
EECS 332 Fruit Ninja Final Project
written by Alvin Tan & Crystal Gong

Fruit Ninja Game
"""

import cv2
import numpy as np
from gameObjects import Text, Level, randomFruit, randomBomb

NUMFRUITS = 3
STALL = 5
LEVEL_START_PAUSE = 20
GAME_TITLE = "Squares are Bombs!"

# font color
GREEN = (0,255,0) #(B, G, R) 
RED = (0,0,255) #(B, G, R) 

        
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
        if area > 50:
            for cval in c:
                if cval[0, 1] < fingerTip[1]:
                    fingerTip = cval[0]
            # print(fingerTip)
            
            # draw the contour
            # cv2.drawContours(frame, contours, i, (0, 255, 0), 3)
            
    return fingerTip


"""
use ROI selection to get min and max thresholds
"""
def selectSkin(frame, skinSample, min_YCrCb, max_YCrCb):
    # select the bounding box of the object we want to track (make
    # sure you press ENTER or SPACE after selecting the ROI)
    r = cv2.selectROI(GAME_TITLE, frame, fromCenter=False, showCrosshair=True)
    if max(r) > 0: # make sure a box was actually selected or else we will get an error
        skin = frame[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
        # Convert skin sample image to YCrCb
        skinSample = cv2.cvtColor(skin,cv2.COLOR_BGR2YCR_CB)
        
        min_YCrCb = np.min(skinSample, axis = 1)[0] 
        max_YCrCb = np.max(skinSample, axis = 1)[0] 
    return skinSample, min_YCrCb, max_YCrCb

""" ACTUAL GAME CODE STARTS HERE """
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

    # We start off without a skin sample
    test = None
    skinSample = None
    # skin max and min
    min_YCrCb = np.array([0,0,0],np.uint8)
    max_YCrCb = np.array([255,255,255],np.uint8)
    
    # keep track if game ended
    gameOver = False
    exitGame = False
    
    # This is the setup time, when we have not yet gotten a skin sample
    while skinSample is None:
        frame = cv2.flip(frame, 1)
        # After displaying the frame, we grab a new frame from the video feed
        gotFrame, frame = vidFeed.read()
        if not gotFrame:
            break
        key = cv2.waitKey(STALL) & 0xFF
        # select bounding box for skin sample
        if key == ord("s"):
            skinSample, min_YCrCb, max_YCrCb = selectSkin(frame, skinSample, min_YCrCb, max_YCrCb)
        # quit
        elif key == ord('q'): # Exit on q
            gameOver = True
            break
            
        # write starting text
        Text((120, 20), GREEN, "Welcome to "+str(GAME_TITLE)).write(frame)
        Text((115, 45), GREEN, "Hit the circles, avoid the bombs!").write(frame)
        Text((95, y0-35), GREEN, "Press 'S' to select hand skin sample").write(frame)
        Text((105, y0-10), GREEN, "Then, press 'ENTER' to begin game").write(frame)
        
        
        # Once all the fruits have been drawn on the frame, we display the frame
        cv2.imshow(GAME_TITLE, frame)

    
    # Here we instantiate our levels:
    levels = []
    levels.append(Level(1, 2, 0, 300)) # numFruits, pointsPerFruit, numBombs, numFrame
    levels.append(Level(3, 5, 0, 300))
    levels.append(Level(3, 5, 1, 300))
    levels.append(Level(5, 7, 3, 300))
    
    # We instantiate our score and our lives
    score = 0
    lives = 3

    # For each of the levels, we do game stuff
    for curLevel in range(len(levels)):
        if gameOver:
            break
        # We instantiate our game objects
        texts = []
        fruits = []
        bombs = []
        explodedBits = []
    
        # We generate the text for this level
        texts.append(Text((10, 50), GREEN, "Lives: "))
        texts.append(Text((int(x0/2), 50), GREEN, "Level: " + str(curLevel)))
        texts.append(Text((x0 - 150, 50), GREEN, "Score: "+str(score)))
        
        # We generate all of the fruits in this level
        for count in range(levels[curLevel].numFruits):
            fruits.append(randomFruit(x0, y0))
        
        # We generate all of the bombs in this level
        for count in range(levels[curLevel].numBombs):
            bombs.append(randomBomb(x0, y0))
        
        startPause = 0
        while (startPause < LEVEL_START_PAUSE) and gotFrame:
            # Flips the frame horizontally so it's a mirror image. Makes sense while
            # facing the screen.
            frame = cv2.flip(frame, 1)
            
            Text((int(x0/2)-100, int(y0/2)), GREEN, GAME_TITLE).write(frame)
            Text((int(x0/2)-45, int(y0/2)+25), GREEN, "LEVEL "+str(curLevel)).write(frame)
            
            cv2.imshow(GAME_TITLE, frame)
            startPause += 1
            
            # After displaying the frame, we grab a new frame from the video feed
            gotFrame, frame = vidFeed.read()
            # Then, pause for 10 ms to see if we entered an interrupt key or not
            key = cv2.waitKey(STALL) & 0xFF
            if key == ord('q'): # Exit on q
                gameOver = True
                break
        
        levelFrames = 0
        
        while gotFrame and not gameOver and levelFrames < levels[curLevel].numFrames:
            # Flips the frame horizontally so it's a mirror image. Makes sense while
            # facing the screen.
            frame = cv2.flip(frame, 1)
            
            # Grab the coordinate of the player's fingertip
            fingerTip = getFingerTip(frame, min_YCrCb, max_YCrCb)
            
            # For each fruit we have,
            for count in range(len(fruits)):
                # we draw it on screen
                fruits[count].draw(frame)
                
                # If our fintertip intersects with the fruit, we explode the fruit
                if fruits[count].intersects(fingerTip):
                    fruits[count].explode(explodedBits)
                    
                    # Update the score and display the new score
                    score += levels[curLevel].pointsPerFruit
                    texts[2] = Text((x0 - 150, 50), GREEN, "Score: "+str(score))
                    
                    # Generate a new fruit to replace it
                    fruits[count] = randomFruit(x0, y0)
                
                # and increment the physics. If the fruit goes offscreen, we remove it
                # and implement another randomly generated fruit in its place
                if not fruits[count].doPhysics(x0, y0):
                    fruits[count] = randomFruit(x0, y0)
            
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
                    bombs[count] = randomBomb(x0, y0)
                
                # and increment the physics
                if not bombs[count].doPhysics(x0, y0):
                    bombs[count] = randomBomb(x0, y0)
            
            # Write all of our text on the screen
            for text in texts:
                text.write(frame)
                
            # Display the lives we have
            for count in range(lives):
                cv2.circle(frame, (175 + count*50, 35), 20, RED, -1)
            
            # Let exploded bits continue falling down
            for exBit in explodedBits:
                exBit.draw(frame)
                if not exBit.doPhysics(x0, y0):
                    explodedBits.remove(exBit)
        
            # Draw in the detected fingertip for troubleshooting purposes
            cv2.circle(frame,(fingerTip[0], fingerTip[1]), 10, GREEN, -1)
        
            # Once all the fruits have been drawn on the frame, we display the frame
            cv2.imshow(GAME_TITLE, frame)
            
            # Increment the frame counter
            levelFrames += 1
            
            # After displaying the frame, we grab a new frame from the video feed
            gotFrame, frame = vidFeed.read()
            key = cv2.waitKey(STALL) & 0xFF
            # Then, pause to see if we entered an interrupt key or not
            if key == ord('q'): # Exit on q
                exitGame = True
                break
        if exitGame:
            break
    # just need to write text once
    if gameOver and skinSample is not None:
        frame = cv2.flip(frame, 1) # just need to flip the frame once
        Text((int(x0/2) - 70, int(y0/2)), RED, "GAME OVER").write(frame)
        Text((int(x0/2) - 90, int(y0/2)+25), RED, "FINAL SCORE: "+str(score)).write(frame)
        
    # If the player loses and the game was actually started
    while gameOver and skinSample is not None: 
        cv2.imshow(GAME_TITLE, frame)
        key = cv2.waitKey(STALL) & 0xFF
        if key == ord('q'): # Exit on q
            break
         
    print("terminating program, quitting windows")
    vidFeed.release()
    cv2.waitKey(1)
    cv2.destroyAllWindows()
