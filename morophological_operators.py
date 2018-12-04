# -*- coding: utf-8 -*-
"""
Created on Sun Oct 14 22:17:24 2018

@author: Crystal Gong
edited by Alvin Tan (12/2/18)
"""
import imageio
import numpy as np

#function img out = Erosion(img in, SE); 
#function img out = Dilation(img in, SE); 
#function img out = Opening(img in, SE); 
#function img out = Closing(img in, SE); 
#function img out = Boundary(img in)

BG_COLOR = 0 # background color
FG_COLOR = 1 # foreground color

# return center pixel of a structure element
# element should have odd dimensions
def getCenterPixel(SE, row, col):
    return [len(SE)//2 + row, len(SE[0])//2 + col]
    
def Erosion(img, structuring_element):
    rows = len(img)
    cols = len(img[0])
    sub_rows = len(structuring_element)
    sub_cols = len(structuring_element[0])
    kept_index_list = []
    for row in range(rows):
        for col in range(cols):
            if (img[row, col] == structuring_element[0, 0]):
                matching_SE = True
                for sub_r in range(sub_rows):
                    for sub_c in range(sub_cols):
                        if row + sub_r >= rows or col + sub_c >= cols or img[row + sub_r, col + sub_r] != structuring_element[sub_r, sub_c]:
                            matching_SE = False
                            break
                    if not matching_SE:
                        break
                if matching_SE:
                    kept_index_list.append(getCenterPixel(structuring_element, row, col))
    img_result = img.copy()                    
    img_result.fill(BG_COLOR) ## zero out image array
    for item in kept_index_list:
        img_result[item[0], item[1]] = FG_COLOR
    
    return img_result
    
def Dilation(img, structuring_element):
    rows = len(img)
    cols = len(img[0])
    
    index_to_expand = []
    for row in range(rows):
        for col in range(cols):
            if img[row, col] == FG_COLOR:
                index_to_expand.append([row, col])
    # make a copy of image to get teh res            
    img_result = img.copy() 
    #img_result.fill(BG_COLOR) ## zero out image array
    xy = getCenterPixel(structuring_element, 0, 0)
    for item in index_to_expand:
        x = xy[0]; y = xy[1]; index_x = item[0]; index_y = item[1]
        for r in range(index_x - x, index_x + x + 1):
            for c in range(index_y - y, index_y + y + 1):
                if r >= 0 and r < rows and c >= 0 and c < cols:
                    img_result[r, c] = FG_COLOR
    
    return img_result

# erosion, then dilation
def Opening(img, structuring_element):
    return Dilation(Erosion(img, structuring_element), structuring_element)

# dilation, then erosion
def Closing(img, structuring_element):
    return Erosion(Dilation(img, structuring_element), structuring_element)

# original, with erosion removed
def Boundary(img):
    kernel = np.ones((5, 5), np.uint8)
    kernel.fill(FG_COLOR)
    dilation_img = Closing(img, kernel)
    
    kernel2 = np.ones((5, 5), np.uint8)
    kernel2.fill(FG_COLOR)
    
    return np.subtract(dilation_img, Erosion(dilation_img, kernel2))
    
    
if __name__ == "__main__":
    functions = [Erosion, Dilation, Opening, Closing]
    image_names = ["gun.bmp", "palm.bmp"]
    for img in image_names:
#        for func in functions:
#            for size in [1, 3, 5, 7]:
#                image = imageio.imread(img)
#                kernel = np.ones((size, size), np.uint8)
#                kernel.fill(FG_COLOR)
#                
#                img_result = func(image, kernel)
#
#                result_file = func.__name__ + "_kernel_size_" + str(size) +"_by_"+ str(size) + "_" + img
#                imageio.imwrite(result_file, img_result) # for testing print result            
#                print(func.__name__ + " " +img +': find the image result at \"{0}\"'.format(result_file))
        func = Boundary
        image = imageio.imread(img)
        img_result = func(image)
        result_file = func.__name__ + "_" + img
        imageio.imwrite(result_file, img_result) # for testing print result            
        print(func.__name__ + " " + img +': find the image result at \"{0}\"'.format(result_file))