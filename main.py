import cv2 as cv
import numpy as np
import os
from windowcapture import WindowCapture
import win32gui, win32ui, win32con
import pyautogui as pag
import pygetwindow as gw
import time
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))

wincap = WindowCapture('RuneLite - popomeister')
#window_name = input('Window to capture: ')
#wincap = WindowCapture(window_name)

def findClickPositions(needle_img_path, img, threshold=0.80, debug_mode=None):
    cv.imwrite('ss.png', img)
    haystack_img = cv.imread('ss.png', cv.IMREAD_GRAYSCALE)
    haystack = haystack_img.astype(np.uint8)
    needle_img = cv.imread(needle_img_path, cv.IMREAD_GRAYSCALE)

    needle_w = needle_img.shape[1]
    needle_h = needle_img.shape[0]

    method = cv.TM_CCOEFF_NORMED
    result = cv.matchTemplate(haystack, needle_img, method)

    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))

    rectangles = []
    for loc in locations:
        rect = [int(loc[0]), int(loc[1]), needle_w, needle_h]
        rectangles.append(rect)
        rectangles.append(rect)

    rectangles, weights = cv.groupRectangles(rectangles, 1, 0.95)
    #print(rectangles)

    points = []
    if len(rectangles):
        line_color = (0, 255, 0)
        line_type = cv.LINE_4

        marker_color = (255, 0, 255)
        marker_type = cv.MARKER_CROSS

        for (x, y, w, h) in rectangles:
            # determine center position
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            points.append((center_x, center_y))
            if debug_mode == 'rectangles':
                top_left = (x, y)
                bottom_right = (x + w, y + h)
                cv.rectangle(haystack_img, top_left, bottom_right, line_color, line_type)
            elif debug_mode == 'points':
                cv.drawMarker(haystack_img, (center_x, center_y), marker_color, marker_type)
                
        if debug_mode:
            cv.imshow('Matches', haystack_img)
            cv.waitKey()
            
    return points

while(True):
    
    needle = 'assets/mining/iron-ore.png'
    screenshot = wincap.get_screenshot()
    points = findClickPositions(needle, screenshot)
    rl = gw.getWindowsWithTitle('RuneLite')[0]
    x_off, y_off = rl.topleft
    
    #needles = ["iron-ore.png", "iron-ore-2.png", "iron-ore-3.png", "iron-ore-4.png", "iron-ore-5.png"]
    #needles = ["tree.png", "tree-2.png"]

    '''
    for needle in needles:
        #print(needle)
        points = findClickPositions(needle, screenshot)
    '''
    print(points)
    
    if points:
        coords = points.pop(0)
        x, y = coords
        runeLiteWindows = pag.getWindowsWithTitle('RuneLite')  
        win = runeLiteWindows[0]
        time.sleep(1) 
        pag.moveTo(x + x_off + random.randrange(10), y + y_off + random.randrange(10), duration=random.uniform(1.0, 3.0))
        pag.click()
        time.sleep(3)
    else:
        pag.moveTo(x_off + 270 + random.randrange(30), y_off + 240 + random.randrange(30), duration=random.uniform(1.0, 3.0))
        pag.click()
        time.sleep(5)
        
    cv.imshow('Computer Vision', screenshot)
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')