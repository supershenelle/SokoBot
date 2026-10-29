import heapq
from itertools import count

from src.solver.state import State, is_goal
from src.solver.moves import (successors, walk_path, simple_deadlock,
                              freeze_deadlock, heuristic, reachable)


def bfs(board, weight=12):
    """
    Kept the name `bfs` so sokobot.py doesn't change, but this is now A* over PUSHES.
    weight=1 -> normal A* (fewest pushes). weight>1 -> faster, slightly longer solutions.
    """
    start = State(board.start_player, board.start_crates)
    if is_goal(start, board):
        return ""

    tie = count()  # tie-breaker so heapq never has to compare State objects

    # visited key = (canonical player, crates). Same crate layout + same reachable
    # region of the player == same state, no matter where the player is standing.
    start_key = (min(reachable(start, board)), start.crates)
    h0 = heuristic(start.crates, board)

    # node = (state, parent_node_id, push_info)
    nodes = [(start, None, None)]
    best_g = {start_key: 0}
    heap = [(weight * h0, h0, next(tie), 0, 0)]  # (f, h, tie, g, node_id)

    while heap:
        f, h, _, g, nid = heapq.heappop(heap)
        state = nodes[nid][0]

        if is_goal(state, board):
            return build_solution(nodes, nid, board)

        reach = reachable(state, board)  # flood fill ONCE per expanded state
        key = (min(reach), state.crates)
        if g > best_g.get(key, 1 << 30):
            continue  # stale heap entry, a cheaper path to this state was found

        for next_state, push in successors(state, board, reach):
            if simple_deadlock(next_state, board):
                continue
            if freeze_deadlock(next_state, push, board):
                continue

            ng = g + 1
            nkey = (min(reachable(next_state, board)), next_state.crates)
            if ng >= best_g.get(nkey, 1 << 30):
                continue
            best_g[nkey] = ng

            nh = heuristic(next_state.crates, board)
            nodes.append((next_state, nid, push))
            heapq.heappush(heap, (ng + weight * nh, nh, next(tie), ng, len(nodes) - 1))

    return ""


def build_solution(nodes, goal_id, board):
    # walking paths are only computed ONCE here, for the final answer,
    # instead of for every candidate push during the search.
    chain = []
    nid = goal_id
    while nodes[nid][1] is not None:
        chain.append(nid)
        nid = nodes[nid][1]
    chain.reverse()

    out = []
    for nid in chain:
        _, parent_id, (stand_pos, move) = nodes[nid]
        parent_state = nodes[parent_id][0]
        out.append(walk_path(parent_state.player, stand_pos, parent_state, board))
        out.append(move)
    return "".join(out)
