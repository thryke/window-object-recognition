import cv2 as cv
import numpy as np
import os
from windowcapture import WindowCapture
import win32gui, win32ui, win32con
import pyautogui as pag
import pygetwindow as gw
import time
import random
from config import AccountInfo
import math
import sys
import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# format for setting up an account
#user = AccountInfo('username', 'login', 'password')

# setting up window capture 
username = user.getUsername()
window_name = 'RuneLite - ' + username
wincap = WindowCapture(window_name)


# returns a set of points where cv2 returns a confidence level >= threshold
# format of return is a list of tuples
def findClickPositions(needle_img_path, img, threshold=0.40, debug_mode=None):
    # saving temporary versions of provided images and converting them to grayscale
    cv.imwrite('temp/ss.png', img)
    haystack_img = cv.imread('temp/ss.png', cv.IMREAD_GRAYSCALE)
    haystack = haystack_img.astype(np.uint8)
    needle_img = cv.imread(needle_img_path, cv.IMREAD_GRAYSCALE)

    # obtaining dimensions of the needle image
    needle_w = needle_img.shape[1]
    needle_h = needle_img.shape[0]

    # setting template matching method and performing template matching
    # TODO: experiment with different models and setup model switching
    method = cv.TM_CCOEFF_NORMED
    result = cv.matchTemplate(haystack, needle_img, method)

    # obtain locations and format them into tuples that can be easily used
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))

    # creating rectangles around all previously computed locations
    rectangles = []
    for loc in locations:
        rect = [int(loc[0]), int(loc[1]), needle_w, needle_h]
        rectangles.append(rect)
        rectangles.append(rect)

    rectangles, weights = cv.groupRectangles(rectangles, 1, 0.5)

    points = []
    if len(rectangles):
        # settings for rectangles debug mode
        line_color = (0, 255, 0)
        line_type = cv.LINE_4
        # settings for points debug mode
        marker_color = (255, 0, 255)
        marker_type = cv.MARKER_CROSS

        for (x, y, w, h) in rectangles:
            # determine center point of each rectangle and add this point to points
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
            #cv.waitKey()
            
    return points

# used to check if on the home screen or already in game on startup
def loginCheck(img):
    needle = 'assets/util/existing.png'
    cv.imwrite('temp/ss2.png', img)
    haystack_img = cv.imread('temp/ss2.png', cv.IMREAD_GRAYSCALE)
    haystack = haystack_img.astype(np.uint8)
    needle_img = cv.imread(needle, cv.IMREAD_GRAYSCALE)
    method = cv.TM_CCOEFF_NORMED
    result = cv.matchTemplate(haystack, needle_img, method)
    locations = np.where(result >= 0.99)
    locations = list(zip(*locations[::-1]))
    if locations:
        return False
    else:
        return True

# script to login to the game
# TODO: add functionality to allow for login if not on the home screen
def login(username, password):
    img = wincap.get_screenshot()
    rl = gw.getWindowsWithTitle('RuneLite')[0]
    x_off, y_off = rl.topleft  
    # clicks the "existing user" button, enters the user credentials
    needle = 'assets/util/existing.png'
    points = findClickPositions(needle, img, threshold=0.99)
    coords = points.pop(0)
    x, y = coords
    pag.moveTo(x + x_off, y + y_off)
    pag.click()
    pag.write(user.getLogin())
    pag.press('tab')
    pag.write(user.getPassword())
    pag.press('enter')
    # sleep between logging in and looking for the next button because of server lag
    time.sleep(7)
    # find and click the "click here to play button"
    needle = 'assets/util/clickheretoplay.png'
    screenshot = wincap.get_screenshot()
    points = findClickPositions(needle, screenshot, threshold=0.99)
    coords = points.pop(0)
    x, y = coords
    pag.moveTo(x + x_off, y + y_off)
    pag.click()

# script to logout of game, looks for the door thumbnail image
def logout():
    img = wincap.get_screenshot()
    rl = gw.getWindowsWithTitle('RuneLite')[0]
    x_off, y_off = rl.topleft  
    tabSwitch('assets/util/logout.png', img)
    needle = 'assets/util/clickheretologout.png'
    screenshot = wincap.get_screenshot()
    points = findClickPositions(needle, screenshot, threshold=0.99)
    # if the logout tab is not on the world switcher page, click the logout button
    if points:
        x, y = points.pop(0)
        pag.moveTo(x + x_off, y + y_off)
        pag.click()
    # if the logout tab is on the world switcher page, exit the page and then click the logout button
    else:
        needle = 'assets/util/x.png'
        screenshot = wincap.get_screenshot()
        points = findClickPositions(needle, screenshot, threshold=0.99)
        x_x, x_y = points.pop(0)
        pag.moveTo(x_x + x_off, x_y + y_off)
        pag.click()
        time.sleep(1)
        needle = 'assets/util/clickheretologout.png'
        screenshot = wincap.get_screenshot()
        points = findClickPositions(needle, screenshot, threshold=0.99)
        x, y = points.pop(0)
        pag.moveTo(x + x_off, y + y_off)
        pag.click()

# switch to a desired tab by passing in the thumbnail of the tab
def tabSwitch(tab, img):
    points = findClickPositions(tab, img, threshold=0.80)
    rl = gw.getWindowsWithTitle('RuneLite')[0]
    x_off, y_off = rl.topleft  
    x, y = points.pop(0)
    pag.moveTo(x + x_off + random.randrange(-8, 8), y + y_off + random.randrange(-8, 8), duration=random.uniform(0.1, 0.3))
    pag.click()

# determine when inventory is full based on the text that appears in the chat box
def fullInvCheck(img):
    needle = 'assets/inventory/fullinv.png'
    cv.imwrite('temp/ss1.png', img)
    haystack_img = cv.imread('temp/ss1.png', cv.IMREAD_GRAYSCALE)
    haystack = haystack_img.astype(np.uint8)
    needle_img = cv.imread(needle, cv.IMREAD_GRAYSCALE)
    method = cv.TM_CCOEFF_NORMED
    result = cv.matchTemplate(haystack, needle_img, method)
    locations = np.where(result >= 0.95)
    locations = list(zip(*locations[::-1]))
    if locations:
        return True
    else:
        return False

# remove all instances of the item currently being collected from the inventory
def clearInv(item):
    rl = gw.getWindowsWithTitle('RuneLite')[0]
    x_off, y_off = rl.topleft  
    img = wincap.get_screenshot()
    # make sure that the inventory tab is open, move cursor to map to get rid of text that was blocking items
    tabSwitch('assets/inventory/inventory-tab.png', img)
    map_list = findClickPositions('assets/util/map.png', img, threshold=0.95)
    map_x, map_y = map_list.pop(0)
    pag.moveTo(map_x + x_off, map_y + y_off)
    img = wincap.get_screenshot()
    points = findClickPositions(item, img, threshold=0.95)
    # drop each individual item, current implementation requires the shift-drop option to be enabled
    for p in points:
        x, y = p
        pag.keyDown('shift')
        pag.moveTo(x + x_off + random.randrange(-8, 8), y + y_off + random.randrange(-8, 8), duration=random.uniform(0.03, 0.06))
        pag.click()
        pag.keyUp('shift')

# decides if the on-click action currently hovered is the desired action
def validAction(action, img):
    needle = action
    cv.imwrite('temp/ss1.png', img)
    haystack_img = cv.imread('temp/ss1.png', cv.IMREAD_GRAYSCALE)
    haystack = haystack_img.astype(np.uint8)
    needle_img = cv.imread(needle, cv.IMREAD_GRAYSCALE)
    method = cv.TM_CCOEFF_NORMED
    result = cv.matchTemplate(haystack, needle_img, method)
    locations = np.where(result >= 0.95)
    locations = list(zip(*locations[::-1]))
    if locations:
        return True
    else:
        return False


screenshot = wincap.get_screenshot()
#logout()

# login if on the login screen
# TODO: add functionality to allow for logging in to a new window
if not loginCheck(screenshot):
    login(user.getUsername(), user.getPassword())

# remain logged in for a random amount of time within range
login_time = random.randrange(1800, 7200)
start_time = datetime.datetime.now()
t = (start_time.year, start_time.month, start_time.day, start_time.hour, start_time.minute, start_time.second, start_time.microsecond, 0, 0)
current_time = time.mktime(t)
end_time = time.mktime(t) + login_time
print('logging in for:', login_time, 'seconds, or', round(((float)(login_time/60)), 2), 'minutes')
invalid_points = []

while(True):  
    # path to image of the desired needle
    needle = 'assets/mining/iron-ore.png'
    screenshot = wincap.get_screenshot()
    points = findClickPositions(needle, screenshot, threshold=0.50)   
    
    # iterate through current list of known invalid points and remove them from the list of valid points
    for point in invalid_points:
        if point in points:
            points.remove(point)

    rl = gw.getWindowsWithTitle('RuneLite')[0]
    x_off, y_off = rl.topleft
    curr_x, curr_y = pag.position()

    if fullInvCheck(screenshot):
        clearInv('assets/inventory/iron-inv.png')
        
    # if the list of points is not empty, compute its position relative to the window
    if points:
        coords = points.pop(random.randrange(0, len(points)))
        x, y = coords
        runeLiteWindows = pag.getWindowsWithTitle('RuneLite')  
        win = runeLiteWindows[0]

        # adding randomness to mouse positioning
        x1 = x + x_off + random.randrange(10)
        y1 = y + y_off + random.randrange(10)
        pag.moveTo(x1, y1, duration=random.uniform(0.5, 1.0))
        screenshot = wincap.get_screenshot()
        # establish that the on-click action is valid, waiting because of action completion
        if validAction('assets/mining/minerocks.png', screenshot):
            pag.click()
            time.sleep(random.uniform(2.0, 3.0))
        else:
            # if the on-click action is deemed invalid the point is added to the list of invalid points
            invalid_points.append(coords)

    # imshow used to do live monitoring of the obtained images
    # not useful in current implementation because of the use of time.sleep()
    cv.imshow('Computer Vision', screenshot)

    # 'p' can be used to pause operation for 30 seconds and 'q' can be used to quit
    # not needed in current implementation because of the automatic timeout
    if cv.waitKey(1) == ord('p'):
        time.sleep(30)
    if cv.waitKey(1) == ord('q'):
        cv.destroyAllWindows()
        break

    # calculating current time and comparing it to the previously computed finish time
    current_time = datetime.datetime.now()
    t = (current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second, current_time.microsecond, 0, 0)
    current_time = time.mktime(t)
    print((int)(end_time - current_time), 'seconds remaining')

    if current_time > end_time:
        logout()
        break

print('Done.')