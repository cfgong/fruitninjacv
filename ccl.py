# -*- coding: utf-8 -*-
"""
Created on Mon Oct  8 22:20:39 2018

@author: Crystal Gong
edited by Alvin Tan (12/2/18)

Connect Component Labeling
input: image (binary image)
outputs: image (binary image)

"""
#import imageio

# referenced: https://stackoverflow.com/questions/20154368/union-find-implementation-using-python
def union_find(list_of_lists):
    list_of_lists = map(set, list_of_lists) # map each list in the list to a set
    unions = []
    for subset in list_of_lists:
        new_list = []
        for s in unions:
            if s.isdisjoint(subset):
                new_list.append(s)
            else: # is not disjoint
                subset = s.union(subset) # shares some elements with subset
        new_list.append(subset)
        unions = new_list
    # make the sets in the unions back to lists
    finalUnions = []
    for u in unions:
        finalUnions.append(list(u))
    return finalUnions


def CCL(frame, size_filter = 0): #size_filter is optional
    img = frame.copy()
    BG_COLOR = 0
    label_counter = 1
    labels = [] # to keep track of label
    
    x0, y0 = frame.shape
    
    for row in range(x0):
        for col in range(y0):
            if img[row][col] != BG_COLOR: # not background, so must be labeled
                if row - 1 >= 0 and col - 1 >= 0:
                    # if both left and top exist
                    # get minimum of pixel and square
                    topLabel = img[row-1][col]
                    leftLabel = img[row][col-1]
                    if (leftLabel != BG_COLOR and topLabel == BG_COLOR):
                        # only left label is labeled
                        img[row][col] = leftLabel
                    elif (topLabel != BG_COLOR and leftLabel == BG_COLOR):
                        # only top label is labeled
                        img[row][col] = topLabel
                    elif (topLabel != BG_COLOR and leftLabel != BG_COLOR):
                        # both are labeled, then we have to find the minimum
                        # and we have to put them in the labels array together
                        img[row][col] = leftLabel # just set it as one of the labels
                        labels.append({topLabel, leftLabel})
                    else:
                        # we need to make a new label
                        img[row][col] = label_counter
                        labels.append({label_counter})
                        label_counter = label_counter + 1
                elif row - 1 >= 0 and img[row - 1][col] != BG_COLOR:
                    # if only top exists and it has been labeled
                    img[row][col] = img[row-1][col]
                elif col - 1 >= 0 and img[row][col-1] != BG_COLOR:
                    img[row][col] = img[row][col-1]
                else:
                    # we need to make a new label
                    img[row][col] = label_counter
                    labels.append({label_counter})
                    label_counter = label_counter + 1
                    
    # we need to union find on labels 
    labels = union_find(labels)
    # we have to relabel the parts
    label_size_dict = {} # label, size
    for sublist in labels:
        label_size_dict[sublist[0]] = 0
    
    # put all the minimum values of the sets and ha
    # dictionary: key = value 
    for row in range(x0):
        for col in range(y0):
            if img[row][col] != BG_COLOR:
                 for label_set in labels: #iterate through the sets of labels
                     if (img[row][col] in label_set):
                         key = label_set[0]
                         img[row][col] = key 
                         label_size_dict[key] = label_size_dict[key] + 1
                         break
                                       
    # size filtering
    if (size_filter > 0):
        # find which labels have sections that are too small
        removed_labels = []
        for label, size in label_size_dict.items():
            if size < size_filter:
                removed_labels.append(label)
        # remove those labels
        for label in removed_labels:
            label_size_dict.pop(label)
        # set the picture to background color
        for row in range(x0):
            for col in range(y0):
                if img[row][col] in removed_labels:
                    img[row][col] = BG_COLOR
                if img[row][col] != 0:
                    img[row][col] = 1

    return img

    '''
    size = len(label_size_dict)
    print('When the size filter is set to {0}...'.format(size_filter))
    print('The labels of the img are:', end = " ")
    print(*label_size_dict.keys(), sep = ", ") 
    print('There are {0} labels total.'.format(size))
    imageio.imwrite(result_file, img) # for testing print result
    print('Find the image result at \"{0}\"'.format(result_file))
    '''
    
    
if __name__ == "__main__":
    img1 = imageio.imread("test.bmp")
    img2 = imageio.imread("face.bmp")
    img3 = imageio.imread("gun.bmp")
    CCL(img1, "test_result.bmp")
    CCL(img2, "face_result.bmp")
    CCL(img3, "gun_result.bmp")
    CCL(img3, "gun_filtered_result.bmp", 300)