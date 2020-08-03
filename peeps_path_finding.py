from collections import *

# Each tile is checked to determine if the goal is reached.
# When the goal is not reached the search result is only updated at the END
# of each search path (some map element that is not a path or a path at which
# a search limit is reached), NOT at each step along the way.
# This means that the search ignores thin paths that are "no through paths"
# no matter how close to the goal they get, but will follow possible "through
# paths".

# The implementation is a depth first search of the path layout in xyz
# according to the search limits. 

# The parameters/variables that limit the search space are:
#   - counter (param) - number of steps walked in the current search path;
#   - _peepPathFindTilesChecked (variable) - cumulative number of tiles that can be
#     checked in the entire search;
#   - _peepPathFindNumJunctions (variable) - number of thin junctions that can be
#     checked in a single search path;

# The parameters that hold the best search result so far are:
#   - score - the least heuristic distance from the goal
#   - endSteps - the least number of steps that achieve the score.

maxCounter = counter = 100
#guest path finding line 1172, orignal is 15000 for guest I don't know why 15000
maxTilesChecked = -1
checked = defaultdict(int) #key: (x,y)  val: score #lower is better
# maxpeepPathFindJunctions = 0
availablePath = None
goal = (0,0)
start = (0,0)

def main_path_finding(peep,space):
    global goal,start,counter,maxTilesChecked,availablePath,checked
    availablePath = space
    maxTilesChecked = len(availablePath)
    counter = maxCounter
    checked = defaultdict(int)
    print('Peep {} is on the way to {}'.format(peep.id,peep.headingTo.name))
    goal = peep.headingTo.position
    start = peep.position
    valid = valid_direction(start)
    ans = sorted([(i,path_finding_dfs(i))for i in valid],key = lambda x: x[1])
    print('current goal: {}\tcurrent position: {}\tnext ideal pos: {}'.format(goal,start,ans))
    if ans:
        return ans[0][0]
    else:
        return start

def path_finding_dfs(node):
    if node in checked:
        return checked[node]
    if node == goal:
        return 0
    global counter
    valid = valid_direction(node)
    if not valid or counter <= 0 or len(checked) >= maxTilesChecked:
        return heuristic_from_goal(node)
    counter -= 1
    checked[node] = min([path_finding_dfs(i)+1for i in valid])
    return checked[node]    

def valid_direction(loc:tuple):
    ans = []
    if (loc[0]+1,loc[1]) in availablePath or (loc[0]+1,loc[1]) == goal:
        ans.append((loc[0]+1,loc[1]))
    if (loc[0]-1,loc[1]) in availablePath or (loc[0]-1,loc[1]) == goal:
        ans.append((loc[0]-1,loc[1]))
    if (loc[0],loc[1]+1) in availablePath or (loc[0],loc[1]+1) == goal:
        ans.append((loc[0],loc[1]+1))
    if (loc[0],loc[1]-1) in availablePath or (loc[0],loc[1]-1) == goal:
        ans.append((loc[0],loc[1]-1))
    return ans

def heuristic_from_goal(pos:tuple):
    return abs(pos[0]-goal[0])+abs(pos[1]-goal[1])

# def peep_pathfind_choose_direction(peep:Peeps):
#     global maxpeepPathFindJunctions
#     maxpeepPathFindJunctions = get_max_junction(peep)

# def get_max_junction(peep:Peeps):
#     #base on guest path finding line 439
#     if peep.hasMap:
#         return 7
#     return 5