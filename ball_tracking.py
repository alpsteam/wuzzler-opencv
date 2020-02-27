import detect_goal
import oci_streaming

import numpy as np
import cv2
import imutils
from collections import deque
import datetime

lower_red = np.array([66,68,90])
upper_red = np.array([90,255,255])

# initialize variables ----------------------------------------------
buffer_size = 10 # size of coords buffer
max_vect_hist = 4 # must be smaller than buffer_size
pts = deque(maxlen=buffer_size) # buffer coords
vts = deque(maxlen=7) # buffer calculated vectors
(dX, dY) = (0, 0)
lastCoords = None
lastVector = None
lastTimestamp = None

def trackBall(normalized_pic, disable_oci_stream):
    global lastCoords
    global lastVector

    hsv = cv2.cvtColor(normalized_pic, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_red, upper_red)
    mask = cv2.erode(mask, None, iterations=1)
    mask = cv2.dilate(mask, None, iterations=2)

    res = cv2.bitwise_and(normalized_pic, normalized_pic, mask=mask)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)

        # only proceed if the radius meets a minimum size
        if radius > 5:
            M = cv2.moments(c)
            try:
                center = (int(M["m10"] / M["m00"]),
                            int(M["m01"] / M["m00"]))
            except:
                pass
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(normalized_pic, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(normalized_pic, center, 5, (0, 0, 255), -1)

            # update the points queue
            pts.appendleft(center)
            # print(center)
    else:
        detect_goal.increaseGoneCount()


    # calculate and save vectors
    if len(pts) is buffer_size:

        # get newest coords
        currentCoords = (pts[0][0], pts[0][1])

        detect_goal.checkForGoal(currentCoords[0],currentCoords[1])

        # currentTimestamp
        currentTimestamp = datetime.datetime.utcnow().timestamp()

        # compute newest direction/vector of ball
        dX = currentCoords[0] - pts[max_vect_hist][0]
        dY = pts[max_vect_hist][1] - currentCoords[1]
        currentVector = (dX, dY)

        # get last coords and vector
        if lastCoords is None and lastVector is None:
            lastCoords = (pts[max_vect_hist][0], pts[max_vect_hist][1])
            lastVector = (dX, dY)

        # get direction in degree's from vector (range +/- 180, 0 degrees = right, 180 degrees = left)
        angleOfCurrent = np.arctan2(currentVector[1], currentVector[0]) * (180/np.pi);
        
        # only include data in vector if ball is moving significantly
        if np.abs(dY) + np.abs(dX) > 5:
            angleOfLast = np.arctan2(lastVector[1], lastVector[0]) * (180/np.pi);

            if np.abs(angleOfLast - angleOfCurrent) > 15:


                lastTimestamp = datetime.datetime.utcnow().timestamp()

                # calculate and save vector
                vectorFromLastToCurrentCoords = (currentCoords[0]-lastCoords[0], currentCoords[1]-lastCoords[1])
                vts.appendleft((lastCoords, vectorFromLastToCurrentCoords))

                # must send vector to stream
                # publish_message(stream_client, stream_id,"foo","whatever")
                if not disable_oci_stream:
                    oci_streaming.stream_to_oci(currentCoords, currentVector, currentTimestamp, lastTimestamp)

                lastCoords = currentCoords
                lastVector = currentVector
                # print("direction change -----------------------")

        for i in np.arange(0, len(vts)):
            cv2.arrowedLine(normalized_pic, vts[i][0], (vts[i][0][0]+vts[i][1][0], vts[i][0][1]+vts[i][1][1]), (250, 240, 0), 2)

        cv2.arrowedLine(normalized_pic, lastCoords, currentCoords, (0,255,0), 3)

        # cv2.putText(normalized_pic, "angle: {}".format(angleOfCurrent),
        #     (10, normalized_pic.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
        #     0.35, (0, 0, 255), 1)

    
        
    # cv2.imshow('frame', normalized_pic)
