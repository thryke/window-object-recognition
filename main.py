import cv2 as cv
import numpy as np
import os
from windowcapture import WindowCapture
import win32gui, win32ui, win32con
#from objectrecognition import PointFinder

os.chdir(os.path.dirname(os.path.abspath(__file__)))

#wincap = WindowCapture('RuneLite')
window_name = input('Window to capture: ')
wincap = WindowCapture(window_name)

def findClickPositions(needle_img_path, img, threshold=0.5, debug_mode=None):
    cv.imwrite('ss.png', img)
    haystack_img = cv.imread('ss.png', cv.IMREAD_UNCHANGED)
    needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)

    needle_w = needle_img.shape[1]
    needle_h = needle_img.shape[0]

    method = cv.TM_CCOEFF_NORMED
    result = cv.matchTemplate(haystack_img, needle_img, method)

    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))

    rectangles = []
    for loc in locations:
        rect = [int(loc[0]), int(loc[1]), needle_w, needle_h]
        rectangles.append(rect)
        rectangles.append(rect)

    rectangles, weights = cv.groupRectangles(rectangles, 1, 0.5)
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
    needle = 'iron2.png'
    screenshot = wincap.get_screenshot()
    #points = findClickPositions(needle, screenshot)
    #wincap.list_window_names()
    cv.imshow('Computer Vision', screenshot)

    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

print('Done.')