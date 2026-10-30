import heapq
from itertools import count
from src.solver.state import State, is_goal
from src.solver.moves import (successors, walk_path, simple_deadlock,
                              freeze_deadlock, heuristic, reachable)

def build_solutionpath(states, goal_id, board):
    """
    This function rebuilds the string of moves tracing from the goal state and searched states, to be used in the weighted A* algo.
    @param states is a list of records in the format (state, parent_id, push_info).
    @param goal_id is an int that indexes the goal state
    @param board is the Board class used to compute walking paths between the pushes.
    @return the string of moves for solving the map level.
    """
    # so after getting the list it checks out the chain of pushes then computes like the walking path between
    # para once nalang computation di yung kada search is icococmpute

    pushes_chain = [] # empty list that holds the ids from start to goal
    state_id = goal_id # backtracks starting from the goal state
    
    # backtracks through parent states until start_state is reached
    while states[state_id][1] is not None:
        pushes_chain.append(state_id) # just keep looping until that node has a parent and add to the list
        state_id = states[state_id][1]
    pushes_chain.reverse() # then reverse since it starts from the goal_state

    sol_parts = [] # this one is like the final list of positions, walking paths, and pushes based on the earlier list
    
    # so for each state that has the push u compute the walking paths to that push position, then the push itself
    for state_id in pushes_chain:
        _, parent_id, (stand_pos, push_move) = states[state_id]
        parent_state = states[parent_id][0]
        sol_parts.append(walk_path(parent_state.player, stand_pos, parent_state, board))
        sol_parts.append(push_move)
    return "".join(sol_parts)


def A_star(board, weight=12):
    """
    This function is the application of the weighted A* based on the crates pushed by the player
    @param board is the Board class representing the map's layout.
    @param weight is an int that scales the heuristic.
    @return a string of moves to finish the level, and an empty string if no solution is found.
    """

    start_state = State(board.start_player, board.start_crates) # the start state of the board
    if is_goal(start_state, board): # base case
        return ""

    tie_breaker = count()  # yung tiebreaker para di macompare yung 2 state objects

    start_key = (min(reachable(start_state, board)), start_state.crates) # the areas thats reachable for the player and then the crate positions
    h0 = heuristic(start_state.crates, board) # the initial distance from the crates being place onto the target loc

    # laman per element would be = (state, parent_node_id, push_info)
    all_states = [(start_state, None, None)] # the list of states already visited 
    best_cost = {start_key: 0} # this like maps the lowest amt of pushes onto the state key
    frontier = [(weight * h0, h0, next(tie_breaker), 0, 0)] # prioq is being used and has the start node/state

    while frontier:
        # pops the state with lowest priority value 
        prio, h_estimate, _, current_cost, nid = heapq.heappop(frontier)
        state = all_states[nid][0]

        # once goal state is found, builds the solution from there and returns it
        if is_goal(state, board):
            return build_solutionpath(all_states, nid, board)

        reachable_loc = reachable(state, board)  # finds all locs the player can walk to 
        
        # recompute the state key
        key = (min(reachable_loc), state.crates)
        if current_cost > best_cost.get(key, 1 << 30):
            continue  # skip if a cheaper way to this state already exists

        # this looks over every push and prune the pushes that make some dead ends
        for next_state, push in successors(state, board, reachable_loc):
            if simple_deadlock(next_state, board):
                continue
            if freeze_deadlock(next_state, push, board):
                continue
            
            # each push costs 1 so add that then computes the resulting key.
            # if exact states been reached before with equal or lower cost its skipped and otherwise record as like the best cost for this state
            new_cost = current_cost + 1
            next_key = (min(reachable(next_state, board)), next_state.crates)
            if new_cost >= best_cost.get(next_key, 1 << 30):
                continue
            best_cost[next_key] = new_cost

            # computes with the new state and adds it to the frontier
            next_heur = heuristic(next_state.crates, board)
            all_states.append((next_state, nid, push))
            heapq.heappush(frontier, (new_cost + weight * next_heur, next_heur, next(tie_breaker), new_cost, len(all_states) - 1))

    return "" # if no solution is found

