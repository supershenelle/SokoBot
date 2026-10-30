from dataclasses import dataclass

###
# @param player (row, col) position of the player
# @param crates frozenset of (row, col) positions of all crates
###
@dataclass(frozen=True)
class State:
    player: tuple[int, int] #row, col
    crates: frozenset[tuple[int, int]]

###
# checks if all crates are on goal/targets
# @param state the State to check
# @param board the Board holding the set of target positions
# @return True if every crate is on a target, otherwise False
###
def is_goal(state, board):
    for crate in state.crates:
        if crate not in board.targets: 
            return False
    return True

###
# Checks whether a state is valid: if player and all crates are
# inside the board, not in wall, and  player is not on a crate
#
# @param state is the state to check
# @param board holds the dimensions and wall positions
# @return       True if the state is legal, otherwise False
# @pre          board.width, board.height and board.walls are initialized
###
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