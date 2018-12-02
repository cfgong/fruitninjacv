#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 15:02:46 2018

@author: Alverino
"""
import cv2
import numpy

cv2.namedWindow("trial")
bitMatrix = numpy.zeros((20, 20))
cv2.imshow("trial", bitMatrix)

while True:
    # just chill for a bit
    for i in range(20):
        for j in range(20):
            if bitMatrix[i, j] == 0:
                bitMatrix[i, j] = 1
            else:
                bitMatrix[i, j] = 0
            '''
            for k in range(3):
                bitMatrix[i, j, k] = bitMatrix[i, j, k] + 1;
                cv2.imshow("trial", bitMatrix)
            '''
    
    cv2.imshow("trial", bitMatrix)

    if cv2.waitKey(2) == ord('q'):
        break
