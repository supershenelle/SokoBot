import heapq
from itertools import count

from src.solver.state import State, is_goal
from src.solver.moves import (successors, walk_path, simple_deadlock,
                              freeze_deadlock, heuristic, reachable)

# technically this only focuses on whats being pushed
def A_star(board, weight=12):
    start_state = State(board.start_player, board.start_crates) # the start state
    if is_goal(start_state, board): # base case
        return ""

    tie_breaker = count()  # yung tiebreaker para di macompare yung 2 state objects

    #starts muna with start_key that has the (smallest) most reachable loc and the push conditions
    start_key = (min(reachable(start_state, board)), start_state.crates) # the areas thats reachable for the player and then the crate positions
    h0 = heuristic(start_state.crates, board) # the distance from the crates being place onto the target loc

    # laman per element would be = (state, parent_node_id, push_info)
    all_states = [(start_state, None, None)] # the list of states already visited 
    best_cost = {start_key: 0} # this like maps the lowest amt of pushes onto the state key
    frontier = [(weight * h0, h0, next(tie_breaker), 0, 0)] # prioq is being used and has the start node/state

    # what it does is pop lowest prio state
    while frontier:
        prio, h_estimate, _, current_cost, nid = heapq.heappop(frontier)
        state = all_states[nid][0]

        if is_goal(state, board):
            return build_solutionpath(all_states, nid, board) # if states is solved rebuild the sol and then like return it

        reachable_loc = reachable(state, board)  # then find all locs the player can walk to 
        key = (min(reachable_loc), state.crates)
        if current_cost > best_cost.get(key, 1 << 30):
            continue  # skip if a cheaper way was found to reach the state

        # this looks over every push and like prune the pushes that make some dead ends
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

            # computes estimate or score then adds to frontier
            next_heur = heuristic(next_state.crates, board)
            all_states.append((next_state, nid, push))
            heapq.heappush(frontier, (new_cost + weight * next_heur, next_heur, next(tie_breaker), new_cost, len(all_states) - 1))

    return ""

# so after getting the list it checks out the chain of pushes then computes like the walking path between
# para once nalang computation di yung kada search is icococmpute
def build_solutionpath(states, goal_id, board):

    pushes_chain = [] # empty list that holds the ids
    state_id = goal_id # so like u backtrack, starting from the goal naman
    while states[state_id][1] is not None:
        pushes_chain.append(state_id) # just keep looping until that node has a parent and add to the list
        state_id = states[state_id][1]
    pushes_chain.reverse() # then reverse since u start form end

    sol_parts = [] # this one is like the final list of positions, walking paths, and pushes based on the earlier list
    # so for each state that has the push u compute the walking paths alongside the push moves
    for state_id in pushes_chain:
        _, parent_id, (stand_pos, push_move) = states[state_id]
        parent_state = states[parent_id][0]
        sol_parts.append(walk_path(parent_state.player, stand_pos, parent_state, board))
        sol_parts.append(push_move)
    return "".join(sol_parts)
