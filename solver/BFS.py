from collections import deque
from solver.board import Board
from solver.state import State, is_goal
from solver.moves import successors
                

def bfs(board):
    # uses board cuz instance of it and makes use of the contents in it
    
    start_state = State(board.start_player, board.start_crates) # instantiation of the start state based on what we know
    
    if start_state.is_goal(start_state, board):
        return ""
    
    queue = deque([start_state]) # creation of queue w/ start state
    visited = {start_state: None} # so this is a dictionary that holds the current state (key) and its associated move (value)
    
    while queue:
        state = queue.popleft() # start of dequeue
        
        for next_state, move in successors(state, board): # this iterates thru both whats returned in successors
        # assuming na it returns a list of (next_state, move) pairs
        
            if next not in visited: # checks only if not visited yet
                visited[next_state] = (state, move)
                
                if is_goal(next_state, board):
                    return get_moves(next_state, visited)
                
                queue.append(next_state)
                    
    return ""

# ok sana tama gawa ko rito pero this js takes the associated moves from the visited dictionary, reverses it, then returns the list of moves
def get_moves(goal_state, visited):
    moves = []
    current_state = goal_state
    
    while visited[current_state] is not None: # u start from goal state and the state before it and continue until u reach start state
        initial_state, move = visited[current_state]
        moves.append(move) # places the rlud whatever sa moves
        current_state = initial_state
        
    moves.reverse()
    return "".join(moves) # since string of moves yung needdd
    