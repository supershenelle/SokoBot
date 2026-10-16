from collections import deque
from solver.state import State, is_valid 

DIRECTIONS = {
    'u': (-1, 0), 'd': (1, 0),
    'l': (0, -1), 'r': (0, 1), }

def reachable(state, board):
    # return the set of cells the player can walk to from state.player 
    visited = []
    queue = deque([state.player]) # get front player position and add sa queue

    while queue:
        row, col = queue.popleft()

        for directionRow, directionCol in DIRECTIONS.values(): #loop through all directions
            next_pos = (row + directionRow, col + directionCol)

            if next_pos in visited:
                continue

            if next_pos in board.walls:
                continue

            if next_pos in state.crates:
                continue

            visited.append(next_pos)
            queue.append(next_pos)

    return visited #return lahat ng pede lakaran (skip crates)

def successors(state, board):
    # return a list of all possible successor states for player
    # pwedeng (next_state, move) yung ireturn
    
    # return list of possible states for the player
    player_moves = reachable(state, board)
    successors = [] # what will be returned
    
    # iterates thru every crate (a lot more efficient)
    for crate_row, crate_col in state.crates:
        for move, (directionRow, directionCol) in DIRECTIONS.items(): # iterates thru every possible direction the crate can move
            player_pos = (crate_row - directionRow, crate_col - directionCol) # the position of the player before pushing the crate
            new_crate_pos = (crate_row + directionRow, crate_col + directionCol) # where the crate moves to after
            
            # just checks if the movements are valid!
            if player_pos not in player_moves:
                continue
            if not board.in_bounds(new_crate_pos):
                continue
            if new_crate_pos in board.walls:
                continue
            if new_crate_pos in state.crates:
                continue
            
            new_crates = (state.crates - {(crate_row, crate_col)} | {(crate_row, crate_col)}) # creates/updates new frozen set of new moves
            # the {} just makes new sets
            
            # instantiates a new state class
            next_state = State(player=(crate_row, crate_col), crates = new_crates) # uses old position of crate cuz thats where the player is after the push
            
            # then this just appends to the list the new state and the move takeb from DIRECTIONS
            successors.append((next_state, move))
            
    return successors

def path_to_goal(state, board):
    # return a list of moves (string) to reach the goal from state.player
    ...

def simple_deadlock(state, board): #also called dead square deadlock
    # return true if state is a simple deadlock, otherwise false
    ...

def corner_deadlock(state, board):
    # return true if state is a corner deadlock, otherwise false
    for crate in state.crates:
        
        if crate in board.targets: # checks if crate is on target
            continue

        # check if crate is adjacent to a wall
        row, col = crate 
        up = (row - 1, col) in board.walls
        down = (row + 1, col) in board.walls
        left = (row, col - 1) in board.walls
        right = (row, col + 1) in board.walls

        # check if crate is in corner
        if (up and left) or (up and right) or (down and left) or (down and right):
            return True

    return False

