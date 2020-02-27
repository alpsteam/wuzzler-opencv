import requests

# define goal barriers -----------------------------------

# show_goal_barriers = args.show_goal_barriers
show_goal_barriers = True

# left goal
left_goal_left_side = 0
left_goal_top_side = 240
left_goal_right_side = 50
left_goal_bottom_side = 460

# right goal
right_goal_left_side = 1150
right_goal_top_side = 240
right_goal_right_side = 1200
right_goal_bottom_side = 460

gone_count = 0

def checkForGoal(x,y):
    global gone_count
    isGoal = calculateGoal(x,y)
    if isGoal:
        if gone_count == 25:
            print(isGoal)
            sendGoalToServer(isGoal)
    else:
        gone_count=0

def increaseGoneCount():
    global gone_count
    if gone_count<30:
        gone_count+=1
        
def calculateGoal(x,y):
    # print(x,y)
    global gone_count
    if left_goal_left_side<x and x<left_goal_right_side:
        if left_goal_top_side<y and y<left_goal_bottom_side:
            return {'team_1': 1}
    if right_goal_left_side<x and x<right_goal_right_side:
        if right_goal_top_side<y and y<right_goal_bottom_side:
            return {'team_2': 1}
    return None

def sendGoalToServer(data):
    url = "http://130.61.11.200:8080/score"
    try:
        print(requests.put(url, data=data).text)
    except:
        print("Something went wrong sending goal to server.")

