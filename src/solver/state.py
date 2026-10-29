from dataclasses import dataclass

@dataclass(frozen=True)
class State:
    player: tuple[int, int] #row, col
    crates: frozenset[tuple[int, int]]

# returns true if all crates are on goal/targets, otherwise false
# (we can just count if lahat ng boxes ay nasa targets pero e2 muna hwhahaha)
def is_goal(state, board):
    for crate in state.crates:
        if crate not in board.targets: #board.targets is yung dapat irereturn from map_info, need muna malaman sa iistore
            return False
    return True

def is_valid(state, board):
    row, col = state.player

    if not (0 <= row < board.height and 0 <= col < board.width): #negative or out of bounds
        return False

    if (row, col) in board.walls: #player is on wall
        return False

    if (row, col) in state.crates: #player is on crate
        return False

    # check if any crate is on wall or out of bounds
    for (row, col) in state.crates:
        if not (0 <= row < board.height and 0 <= col < board.width):
            return False
        if (row, col) in board.walls:
            return False

    return True

# implementation of the manhattan distance
def manhattan_distance(start_pos, end_pos):
    return abs(start_pos[0] - end_pos[0]) + abs(start_pos[1] - end_pos[1])


# GEANE: this gets the heuristic of the state, so like distance from the crates to the targets
def get_heuristic(state, board):
   if not board.targets:
       return 0
   
   total = 0
   for crate in state.crates:
       closest = None
       for target in board.targets:
           distance = manhattan_distance(crate, target)
           if closest is None or distance < closest:
               closest = distance
               
       total += closest
    
   return total
        
