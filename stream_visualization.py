from detect_goal import left_goal_left_side, left_goal_top_side, left_goal_right_side, left_goal_bottom_side, right_goal_left_side, right_goal_top_side, right_goal_right_side, right_goal_bottom_side
import cv2

def visualize_stream(normalized_pic):
    # draw yellow reference circles			
    cv2.circle(normalized_pic, (1075, 80), 23, (0, 255, 255), 2)
    cv2.circle(normalized_pic, (1080, 625), 23, (0, 255, 255), 2)
    cv2.circle(normalized_pic, (120, 80), 23, (0, 255, 255), 2)
    cv2.circle(normalized_pic, (120, 630), 23, (0, 255, 255), 2)

    # lines for orientation
    cv2.line(normalized_pic, (600, 0), (600, 700), (255, 0, 255), 2, 2)

    # left goal
    cv2.line(normalized_pic, (left_goal_left_side, left_goal_top_side), (left_goal_left_side, left_goal_bottom_side), (0,255,0), 3)
    cv2.line(normalized_pic, (left_goal_right_side, left_goal_top_side), (left_goal_right_side, left_goal_bottom_side), (0,255,0), 3)
    # right goal
    cv2.line(normalized_pic, (right_goal_left_side, right_goal_top_side), (right_goal_left_side, right_goal_bottom_side), (0,255,0), 3)
    cv2.line(normalized_pic, (right_goal_right_side, right_goal_top_side), (right_goal_right_side, right_goal_bottom_side), (0,255,0), 3)

    cv2.imshow('normalized', normalized_pic)
    # cv2.imshow('frame',color_image)

    cv2.waitKey(1)