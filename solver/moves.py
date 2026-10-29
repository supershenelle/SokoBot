from collections import deque
from src.solver.state import State

DIRECTIONS = {
    'u': (-1, 0), 'd': (1, 0),
    'l': (0, -1), 'r': (0, 1), }


def reachable(state, board):
    # set of cells the player can walk to (crates block).
    # uses board.neighbors (walls/bounds already filtered) and a stack; order doesn't matter here
    crates = state.crates
    nbrs = board.neighbors
    seen = {state.player}
    stack = [state.player]
    pop = stack.pop
    push = stack.append
    add = seen.add
    while stack:
        for n in nbrs[pop()]:
            if n not in seen and n not in crates:
                add(n)
                push(n)
    return seen


def canonical_player(state, board):
    # smallest reachable square = one representative for the whole region
    return min(reachable(state, board))


def walk_path(start, goal, state, board):
    # only used when rebuilding the final answer now (not during search)
    if start == goal:
        return ""
    visited = {start: None}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        for move, (dr, dc) in DIRECTIONS.items():
            nxt = (cur[0] + dr, cur[1] + dc)
            if nxt in visited or not board.in_bounds(nxt):
                continue
            if nxt in board.walls or nxt in state.crates:
                continue
            visited[nxt] = (cur, move)
            if nxt == goal:
                path = []
                p = nxt
                while visited[p] is not None:
                    prev, m = visited[p]
                    path.append(m)
                    p = prev
                path.reverse()
                return "".join(path)
            queue.append(nxt)
    return None


def successors(state, board, player_moves=None):
    # returns (next_state, (stand_pos, move)) for every legal PUSH.
    # no walk string here: that was the expensive part (a BFS per push).
    if player_moves is None:
        player_moves = reachable(state, board)
    result = []

    for crate_row, crate_col in state.crates:
        for move, (dr, dc) in DIRECTIONS.items():
            stand = (crate_row - dr, crate_col - dc)
            new_pos = (crate_row + dr, crate_col + dc)

            if stand not in player_moves:
                continue
            if not board.in_bounds(new_pos) or new_pos in board.walls:
                continue
            if new_pos in state.crates:
                continue

            new_crates = (state.crates - {(crate_row, crate_col)}) | {new_pos}
            nxt = State(player=(crate_row, crate_col), crates=new_crates)
            result.append((nxt, (stand, move)))
    return result


# ---------- deadlocks ----------

def simple_deadlock(state, board):
    if not hasattr(board, "dead_squares_cache"):
        board.dead_squares_cache = compute_dead_squares(board)
    dead = board.dead_squares_cache
    return any(c in dead for c in state.crates)


def compute_dead_squares(board):
    return frozenset(
        (r, c) for r in range(board.height) for c in range(board.width)
        if (r, c) not in board.walls and (r, c) not in board.push_dist
    )


def compute_push_dist(board):
    # reverse BFS from goals (pulling crates). push_dist[sq] = min pushes to reach a goal.
    # a square that never gets reached is a dead square.
    def ok(p):
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


def heuristic(crates, board):
    # sum of each crate's own min push distance to a goal (lower bound)
    d = board.push_dist
    return sum(d[c] for c in crates if c not in board.targets)


def freeze_deadlock(state, push, board):
    # after a push, check the pushed crate (and crates touching it) for a frozen group
    # that isn't fully sitting on goals.
    crates = state.crates
    dead = board.dead_squares_cache if hasattr(board, "dead_squares_cache") else frozenset()
    walls = board.walls
    targets = board.targets

    def blocked(c, axis, path):
        a = (c[0], c[1] - 1) if axis == 'h' else (c[0] - 1, c[1])
        b = (c[0], c[1] + 1) if axis == 'h' else (c[0] + 1, c[1])
        if a in walls or b in walls:
            return True
        if a in dead and b in dead:
            return True
        for n in (a, b):
            if n in crates and (n in path or frozen(n, path)):
                return True
        return False

    def frozen(c, path):
        path = path | {c}
        return blocked(c, 'h', path) and blocked(c, 'v', path)

    _, move = push
    dr, dc = DIRECTIONS[move]
    moved = (state.player[0] + dr, state.player[1] + dc)
    check = [moved] + [(moved[0] + a, moved[1] + b) for a, b in DIRECTIONS.values()]
    for c in check:
        if c in crates and c not in targets and frozen(c, frozenset()):
            return True
    return False
