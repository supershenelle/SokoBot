from src.solver.state import State

class Board:
    def __init__(self, width, height, map, objects):
        self.width = width
        self.height = height
        self.map = map
        self.objects = objects


        #ITO DINAGDAG KO GUYS HELLO KAJSHDK
        #call map_info para maextract yung walls, targets, crates, and player
        walls, targets, crates, player = map_info(width, height, map, objects)

        #use frozenset to make the searching faster for BFS
        self.walls = frozenset(walls)
        self.targets = frozenset(targets)
        self.start_crates = frozenset(crates) #para sa starting position ng crates and player
        self.start_player = player 

        # precompute once: pushes-to-goal per square (also gives dead squares)
        from src.solver.moves import compute_push_dist, compute_dead_squares
        self.push_dist = compute_push_dist(self)
        self.dead_squares_cache = compute_dead_squares(self)

        # precompute: for every floor cell, its non-wall neighbors (so flood fill needs no bounds/wall checks)
        self.neighbors = {}
        for r in range(height):
            for c in range(width):
                if (r, c) in self.walls:
                    continue
                self.neighbors[(r, c)] = tuple(
                    n for n in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                    if 0 <= n[0] < height and 0 <= n[1] < width and n not in self.walls
                )

    #to check if nasa loob ng board yung (r,c)
    def in_bounds(self, pos):
        r, c = pos
        return 0 <= r < self.height and 0 <= c < self.width



def map_info(width, height, map, objects):
    walls, targets, crates = [], [], []  #check if may better data struct to represent this

    #para hindi mag crash yung code
    player = None

    for row in range(height): 
        for col in range(width):
            if map[row][col] == '#':
                walls.append((row, col))
            elif map[row][col] == '.':
                targets.append((row, col))

            # seperate map and objects kasi pwede same pos targets and crates
            if objects[row][col] == '$':
                crates.append((row, col))
            elif objects[row][col] == '@':
                player = (row, col)

    return walls, targets, crates, player
