DIRECTIONS = {
    'u': (-1, 0), 'd': (1, 0),
    'l': (0, -1), 'r': (0, 1), }

def reachable(state, board):
    # return the set of cells the player can walk to from state.player
    ...

def successors(state, board):
    # return a list of all possible successor states for player
    # pwedeng (next_state, move) yung ireturn
    ...

def path_to_goal(state, board):
    # return a list of moves (string) to reach the goal from state.player
    ...