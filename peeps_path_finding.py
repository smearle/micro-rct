from class_peeps import Peeps 

# The primary heuristic used is distance from the goal; the secondary
# heuristic used (when the primary heuristic gives equal scores) is the number
# of steps. i.e. the search gets as close as possible to the goal in as few
# steps as possible.

# Each tile is checked to determine if the goal is reached.
# When the goal is not reached the search result is only updated at the END
# of each search path (some map element that is not a path or a path at which
# a search limit is reached), NOT at each step along the way.
# This means that the search ignores thin paths that are "no through paths"
# no matter how close to the goal they get, but will follow possible "through
# paths".

# The implementation is a depth first search of the path layout in xyz
# according to the search limits. 

# The parameters that hold the best search result so far are:
#   - score - the least heuristic distance from the goal
#   - endSteps - the least number of steps that achieve the score.