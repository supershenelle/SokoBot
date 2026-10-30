from collections import deque
from src.solver.state import State

DIRECTIONS = {
    'u': (-1, 0), 'd': (1, 0),
    'l': (0, -1), 'r': (0, 1), }

# Finds every square the player can reach without moving a crate.
# Uses a stack (DFS) for fast exploration of the connected room.
# @param state the current State (holds player position and crates)
# @param board the Board class holding precomputed walkable neighbors
# @return a set of all reachable (row,col) coordinates
def reachable(state, board):
    crates = state.crates
    nbrs = board.neighbors
    explored = {state.player}
    stack = [state.player]

    while stack:
        current = stack.pop()
        for n in nbrs[current]:
            if n not in explored and n not in crates:
                explored.add(n)
                stack.append(n)
    return explored


# Return the top-leftmost reachable square for the player.
# @param state the current State
# @param board the Board class
# @reutnr a single (row,col) tuple representing the canonical position
def min_square(state, board):
    # returns yung minimum square na reachable ng player, used for heuristic
    # # cocompare niya yung row tas column
    return min(reachable(state, board)) 


# Reconstructs the exact walking path from a start position to a goal position.
# Uses BFS to guarantee the shortest walking distance.
# @param start the starting (row,col) position of the player
# @param goal the target (row,col) position to reach
# @param state the burrent State (para maiwasan yung crates)
# @param board the Board class
# @return a string of moves (u, d, l, r) or an empty string if already there
def walk_path(start, goal, state, board):
    if start == goal: # if nasa goal na return empty string
        return ""
    
    visited = {start: None} # track visited (prev, move)
    queue = deque([start]) # track queue

    while queue:
        cur = queue.popleft() # oldest square removed
        for move, (dr, dc) in DIRECTIONS.items(): # try each direction
            nxt = (cur[0] + dr, cur[1] + dc)
            if nxt in visited or not board.in_bounds(nxt): # filter explored, out of bounds
                continue
            if nxt in board.walls or nxt in state.crates:  # filter walls and crates
                continue
            visited[nxt] = (cur, move) # add sa visited

            if nxt == goal: # path found, backtrack to get the moves
                path = []
                p = nxt
                while visited[p] is not None:
                    prev, m = visited[p]
                    path.append(m)
                    p = prev
                path.reverse()
                return "".join(path)
            queue.append(nxt) # otherwise, add to queue for exploration
    return None

# Generates all valid crate pushes from the current state
# @param state the current State
# @param board the Boarad class
# @param player_moves optional pre-computed set of reachable squares to save time
# @return a list of tuples in the format (next_state, push_info) where push_info is (stand_pos, move)
def successors(state, board, player_moves=None):
    # returns (next_state, (stand_pos, move)) for every legal PUSH.
    if player_moves is None: # find reachable squares
        player_moves = reachable(state, board)
    result = []

    for crate_row, crate_col in state.crates: 
        for move, (dr, dc) in DIRECTIONS.items(): # try every direction
            stand = (crate_row - dr, crate_col - dc) # stand = square behind the crate, where the player must be to push it
            new_pos = (crate_row + dr, crate_col + dc) # new_pos = square in front of the crate, where the crate will be pushed to

            # checks if movements are valid
            if stand not in player_moves:
                continue
            if not board.in_bounds(new_pos) or new_pos in board.walls:
                continue
            if new_pos in state.crates:
                continue

            # creates the crate positions  after push, and the new state after the push
            new_crates = (state.crates - {(crate_row, crate_col)}) | {new_pos}
            nxt = State(player=(crate_row, crate_col), crates=new_crates)
            result.append((nxt, (stand, move)))
    return result


# ---------- deadlocks ----------

# Checks if any crate is currently sitting on a precomputed dead square.
# @param state the current State
# @param board the Board class
# @return True is a crate is on a dead squarem otherwise False
def simple_deadlock(state, board):
    dead = board.dead_squares_cache # retrieve lang ung dead squares na na precompute sa board
    return any(crate in dead for crate in state.crates)

# Computes all dead squares on the board (square from which a crate can never reach a target)
# A square is dead if it is not a wall and has no valid push distance to any target
# @param board the Board class
# @return a frozenset of dead (row,col) coordinatess
def compute_dead_squares(board):
    return frozenset(
        (r, c) for r in range(board.height) for c in range(board.width)
        if (r, c) not in board.walls and (r, c) not in board.push_dist )

# Precomputes the exact minimum number of pushes required to get a car ate from any square to a target.
# Uses BFS stating from all tar gets,
# @param board the Board class
# @return a dictionary mapping (row,col) to push distance
def compute_push_dist(board):
    def ok(p): # helper ko lang hehe if inside board and not wall
        return board.in_bounds(p) and p not in board.walls

    dist = {g: 0 for g in board.targets}
    queue = deque(board.targets)
    while queue:
        r, c = queue.popleft()
        for dr, dc in DIRECTIONS.values():
            crate_prev = (r - dr, c - dc)
            player_prev = (r - 2 * dr, c - 2 * dc)
            if ok(crate_prev) and ok(player_prev) and crate_prev not in dist:
                dist[crate_prev] = dist[(r, c)] + 1
                queue.append(crate_prev)
    return dist

# The A* heuristic is calculated by getting the sums of the exact minimum push distances of all crates to the targets
# @param crates the frozenset of current crates positions
# @param board the Board ckass
# @return an integer representing the estimated remaining pushes
def heuristic(crates, board):
    # sum of each crate's own min push distance to a goal
    d = board.push_dist
    return sum(d[c] for c in crates if c not in board.targets)

# Detects if a crate (or a group of connected crates) has become frozen in place and is not reting on a target
# (meaning the puzzle is unsolvable)
# @param state the current State
# @oaram push the push_info tuple (standard_pos, move) that just occurred
# @param board the Board class
# @return True if a dead freeze occurredm otherwise false.
def freeze_deadlock(state, push, board):
    # after a push, check the pushed crate (and crates touching it) for a frozen group
    crates = state.crates
    dead = board.dead_squares_cache
    walls = board.walls
    targets = board.targets

    def blocked(c, axis, path): # check if blocked horizontally or vertically
        a = (c[0], c[1] - 1) if axis == 'h' else (c[0] - 1, c[1])
        b = (c[0], c[1] + 1) if axis == 'h' else (c[0] + 1, c[1])

        # blocked by walls
        if a in walls or b in walls:
            return True

        # blocked by dead squares
        if a in dead and b in dead:
            return True

        # blocked by other crates in the path
        for n in (a, b):
            if n in crates and (n in path or frozen(n, path)):
                return True
        return False

    # helper lang to check if a crate is frozen, and if so, add it to the path
    def frozen(c, path):
        path = path | {c}
        return blocked(c, 'h', path) and blocked(c, 'v', path)

    # find crate na pushed
    _, move = push
    dr, dc = DIRECTIONS[move]
    moved = (state.player[0] + dr, state.player[1] + dc)
    check = [moved] + [(moved[0] + a, moved[1] + b) for a, b in DIRECTIONS.values()]

    # reject if any of the crates in the check list are frozen and not on a target
    for c in check:
        if c in crates and c not in targets and frozen(c, frozenset()):
            return True
    return False
