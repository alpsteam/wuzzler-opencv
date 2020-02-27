import numpy as np
import cv2
from collections import deque
import imutils

# settings
lower_green = np.array([37,100,50])
upper_green = np.array([80,255,255])
backup_coords = np.array([(73, 239), (356, 117), (475, 265), (187, 443)], dtype = "float32")

cached_coords = None
count = 0
def normalizePicture(color_image):
    global cached_coords
    global count

    green_circles = None
    if cached_coords is None or count > 100:
        green_circles = find_green_circles(color_image)

    if green_circles is not None and len(green_circles)==4:
        # print("found good points")
        pts_f32 = np.array(green_circles, dtype = "float32")
        rect = order_points(pts_f32)
        cached_coords = rect
        # print(cached_coords)
        count = 0
    elif cached_coords is not None:
        count += 1
        rect = np.array(cached_coords, dtype="float32")
    else:
        pts_f32 = backup_coords
        rect = order_points(pts_f32)

    # print(cached_coords)

    return four_point_transform(color_image, rect)

def find_green_circles(color_image):
    global count
    count+=1
    hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
    pts = deque([1024])
    
    mask = cv2.inRange(hsv, lower_green, upper_green)
    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=2)

    # cv2.imshow('mask',mask)
    
    res = cv2.bitwise_and(color_image, color_image, mask=mask)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    edges = []

    if len(cnts) > 0:
        # find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
        sorted_cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        for num, c in enumerate(sorted_cnts):
            if num == 4:
                break
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)

            # only proceed if the radius meets a minimum size
            if 20 > radius > 15:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                # cv2.circle(color_image, (int(x), int(y)), int(radius),
                #     (0, 255, 255), 2)
                cv2.circle(color_image, center, 5, (0, 0, 255), -1)
                # print((int(x), int(y)))
                edges.append((int(x),int(y)))
        
    return edges

def four_point_transform(image, rect):
	# print(rect)
	# obtain a consistent order of the points and unpack them
	# individually
	(tl, tr, br, bl) = rect

	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	# maxWidth = max(int(widthA), int(widthB))
	maxWidth = 1200

	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	# maxHeight = max(int(heightA), int(heightB))
	maxHeight = 700
 
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
 
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
 
	# return the warped image
	return warped

def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
 
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
 
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
 
	# return the ordered coordinates
	return transform_rect(rect)

# this function transforms the rect points because the green dots in the edges of the soccer field are not perfectly in the corner
def transform_rect(rect):
    new_rect = rect
    new_rect[0] = np.array([(rect[0][0]-75), (rect[0][1]-50)], dtype="float32")
    new_rect[1] = np.array([(rect[1][0]+75), (rect[1][1]-50)], dtype="float32")
    new_rect[2] = np.array([(rect[2][0]+75), (rect[2][1]+50)], dtype="float32")
    new_rect[3] = np.array([(rect[3][0]-75), (rect[3][1]+50)], dtype="float32")
    return new_rect

