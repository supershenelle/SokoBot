class State:

    def __init__(self, player, crates):
        self.player = player
        self.crates = crates

# returns true if all crates are on goal/targets, otherwise false
# (we can just count if lahat ng boxes ay nasa targets pero e2 muna hwhahaha)
def is_goal(state, board):
    for crate in state.crates:
        if crate not in board.targets:
            return False
    return True



def is_valid(state, board):
    ...

# dito ba sya or sa moves.py? kasi andito rin is_valid e
def is_deadlock(state, board):
    ...

