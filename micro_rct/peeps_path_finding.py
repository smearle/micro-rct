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


class PathFinder:
    def __init__(self):

        self.maxCounter = self.counter = 100
        #guest path finding line 1172, orignal is 15000 for guest I don't know why 15000
        self.maxTilesChecked = -1
        self.checked = defaultdict(int) #key: (x,y)  val: score #lower is better
        # since we only consider 'checked' once score is returned
        self.checking = {}
        # maxpeepPathFindJunctions = 0
        self.availablePath = None
        self.goal = (0,0)
        self.start = (0,0)
        pass


    def main_path_finding(self,peep,space):
        self.availablePath = space
        self.maxTilesChecked = len(self.availablePath)
        self.counter = self.maxCounter
        self.checked = defaultdict(int)
        print('Peep {} is on the way to {}'.format(peep.id,peep.headingTo.name))
        self.checking = {}
        self.goal = peep.headingTo.enter
        start = peep.position
        valid = self.valid_direction(start)
        ans = []

        for i in valid:
            counter = self.counter
            ans.append((i, self.path_finding_dfs(i, counter)))
        ans = sorted(ans, key = lambda x: x[1])
        print('current goal: {}\tcurrent position: {}\tnext ideal pos: {}'.format(self.goal,start,ans))

        if ans:
            return ans[0][0]
        else:
            return start

    def path_finding_dfs(self,node,counter):
        print('checking', node)
        print(self.checking)
        if node in self.checking:
            return float('inf')
        self.checking[node] = True
        goal = self.goal
        maxTilesChecked = self.maxTilesChecked

        if node in self.checked:
            return self.checked[node]

        if node == self.goal:
            self.checking.pop(node)
            return 0
        valid = self.valid_direction(node)

        if not valid or counter <= 0 or len(self.checked) >= maxTilesChecked:
            print('use heuristic')

            return self.heuristic_from_goal(node)
        counter -= 1

       #for i in valid:
       #    if i not in self.checking:
       #        path_score = self.pathfinding_dfs(i)
       #        if not path_score
        self.checked[node] = min([self.path_finding_dfs(i, counter)+1 for i in valid])
        #       print(self.checking)
        self.checking.pop(node)

        return self.checked[node]

    def valid_direction(self,loc:tuple):
        goal = self.goal
        ans = []
        availablePath = self.availablePath

        if (loc[0]+1,loc[1]) in availablePath or (loc[0]+1,loc[1]) == goal \
                and (loc[0]+1,loc[1]) not in self.checking:

            ans.append((loc[0]+1,loc[1])) 
        if (loc[0]-1,loc[1]) in availablePath or (loc[0]-1,loc[1]) == goal \
                and (loc[0]-1,loc[1]) not in self.checking:
            ans.append((loc[0]-1,loc[1]))

        if (loc[0],loc[1]+1) in availablePath or (loc[0],loc[1]+1) == goal \
                and (loc[0],loc[1]+1) not in self.checking:
            ans.append((loc[0],loc[1]+1))

        if (loc[0],loc[1]-1) in availablePath or (loc[0],loc[1]-1) == goal \
             and (loc[0],loc[1]-1) not in self.checking:
            ans.append((loc[0],loc[1]-1))

        return ans

    def heuristic_from_goal(self,pos:tuple):
        goal = self.goal

        return abs(pos[0]-goal[0])+abs(pos[1]-goal[1])

# def peep_pathfind_choose_direction(peep:Peeps):
#     global maxpeepPathFindJunctions
#     maxpeepPathFindJunctions = get_max_junction(peep)

# def get_max_junction(peep:Peeps):
#     #base on guest path finding line 439
#     if peep.hasMap:
#         return 7
#     return 5
