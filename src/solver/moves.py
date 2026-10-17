from collections import deque
from src.solver.state import State

DIRECTIONS = {
    'u': (-1, 0), 'd': (1, 0),
    'l': (0, -1), 'r': (0, 1), }

def reachable(state, board):
    # return the set of cells the player can walk to from state.player 
    visited = {state.player} #CON: from list lang to a set para mas bumilis search time kapag cinall sa BFS
    queue = deque([state.player]) # get front player position and add sa queue

    while queue:
        row, col = queue.popleft()

        for directionRow, directionCol in DIRECTIONS.values(): #loop through all directions
            next_pos = (row + directionRow, col + directionCol)

            if next_pos in visited:
                continue

            # CON: added checking if in bounds
            if not board.in_bounds(next_pos):
                continue

            if next_pos in board.walls:
                continue

            if next_pos in state.crates:
                continue

            visited.add(next_pos) # CON: changed lang to add since set var uses add instead of append
            queue.append(next_pos)

    return visited #return lahat ng pede lakaran (skip crates)

# CON: para sa buong sequence of actions na need gawin ng player bcs yung successors is currently just the pushes
# na need gawin ng player pero hindi pa na aaccount yung walks na need (yes similra code with reachable kasi they boath use BFS)
def walk_path(start, goal, state, board):
    if start == goal:
        return ""

    visited = {start: None}
    queue = deque([start]) 
    
    while queue:
        current = queue.popleft()
    
        for move, (directionRow, directionCol) in DIRECTIONS.items():
            next = (current[0] + directionRow, current[1] + directionCol)
    
            if next in visited:
                continue
    
            if not board.in_bounds(next):
                continue
    
            if next in board.walls:
                continue
    
            if next in state.crates:
                continue

            visited[next] = (current, move)

            if next == goal:
                path = []
                p = next

                while visited[p] is not None:
                    prev, m = visited[p]
                    path.append(m)
                    p = prev
                path.reverse()
                return"".join(path)

            queue.append(next)
    return None


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

            # CON: added directionRow and directionCol kasi yung code before hindi nagalaw yung crate from it's orig position
            new_crates = (state.crates - {(crate_row, crate_col)}) | {(crate_row + directionRow, crate_col + directionCol)} # creates/updates new frozen set of new moves
            # the {} just makes new sets
            
            # instantiates a new state class
            next_state = State(player=(crate_row, crate_col), crates = new_crates) # uses old position of crate cuz thats where the player is after the push

            # CON: expand ung push moves lang with the full move string including the walk
            walk = walk_path(state.player, player_pos, state, board)
            if walk is None:
                continue
            
            # then this just appends to the list the new state and the move takeb from DIRECTIONS
            successors.append((next_state, walk + move))
            
    return successors

# return true if state is a simple deadlock, otherwise false
def simple_deadlock(state, board): #also called dead square deadlock
    # CON: naka cache na yung computation for the dead squares para di repetitive na chinecheck yung squares na yon every call
    # kasi sobrang tagal and haba niya and unnecessary since yung set naman ng dead square naman is naka base sa board mismo and hindi sa current state 
    if not hasattr(board, "dead_squares_cache"):
        board.dead_squares_cache = compute_dead_squares(board)
    dead_squares = board.dead_squares_cache

    return any(crate in dead_squares for crate in state.crates)
    
# CON: original simple deadlock code ni mav sineparate ko lang para macache siya since matagal yung run time niya so hindi papasok sa 15 secs na limit
def compute_dead_squares(board):    
    #to check if the pos is not out of bounds and is not a wall (bale gagamitin ko nlng in_bounds tapos add ako condition for walls)
    def is_dead_square(pos):
        return board.in_bounds(pos) and pos not in board.walls

    #put all target pos in queue
    alive_squares = set(board.targets)
    queue = deque(board.targets) # start sa goal 

    #BFS to find all alive squares
    while queue:
        row, col = queue.popleft()

        #get previous crate and player position from pulling the current crate position
        for directionRow, directionCol in DIRECTIONS.values():
            prev_crate = (row - directionRow, col - directionCol)
            prev_player = (row - 2 * directionRow, col - 2 * directionCol)

            #this checks if you pull the crate in a direction, valid ba sya or out of bounds or wall, and if the player can reach the position to push the crate
            if is_dead_square(prev_crate) and is_dead_square(prev_player) and prev_crate not in alive_squares:
                alive_squares.add(prev_crate)
                queue.append(prev_crate)

    # every non-wall square that is not in alive
    dead_squares = set()
    for row in range(board.height):
        for col in range(board.width):
            pos = (row, col)
            if is_dead_square(pos) and pos not in alive_squares:
                dead_squares.add(pos)
    return frozenset(dead_squares)



# return true if state is a corner deadlock, otherwise false
def corner_deadlock(state, board):
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

