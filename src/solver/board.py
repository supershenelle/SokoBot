from src.solver.state import State
from src.solver.moves import compute_push_dist, compute_dead_squares


class Board:
    ###
    # stores information about the maps and precomputes functions used by the solver: push
    # distances, dead squares, and walkable neighbors for each cell.
    #
    # @param width    number of columns in the map
    # @param height   number of rows in the map
    # @param map      contains '#' walls and '.' targets
    # @param objects  contains '$' crates and '@' player
    ###
    def __init__(self, width, height, map, objects):
        self.width = width
        self.height = height
        self.map = map
        self.objects = objects


        #ITO DINAGDAG KO GUYS HELLO KAJSHDK
        #call map_info para maextract yung walls, targets, crates, and player
        walls, targets, crates, player = map_info(width, height, map, objects)

        #use frozenset to make the searching faster for the search algo
        self.walls = frozenset(walls)
        self.targets = frozenset(targets)
        self.start_crates = frozenset(crates) #para sa starting position ng crates and player
        self.start_player = player 

        # computes the distance of pushes to goal per loc, pero also adds the dead locs/squares prior
        # para di na icompute kada step
        self.push_dist = compute_push_dist(self)
        self.dead_squares_cache = compute_dead_squares(self)

        # builds the mapping from each loc/grid to yung walkable neighbors
        # precomputes beforehand so no filtering or rechecking needs to be done, mapping nalang
        self.neighbors = {}
        for r in range(height):
            for c in range(width):
                if (r, c) in self.walls:
                    continue
                self.neighbors[(r, c)] = tuple(
                    n for n in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                    if 0 <= n[0] < height and 0 <= n[1] < width and n not in self.walls
                )


    ###
    # Checks whether a position is inside the board (r, c).
    #
    # @param pos (row, col) position to check
    # @return True if 0 <= row < height and 0 <= col < width, otherwise False
    ###
    def in_bounds(self, pos):
        r, c = pos
        return 0 <= r < self.height and 0 <= c < self.width


###
# checks the map and collects  the positions of all walls, targets, crates, and the player.
# @param width number of columns in the map
# @param height number of rows in the map
# @param map      contains '#' walls and '.' targets
# @param objects  contains '$' crates and '@' player
# @return walls, targets, crates, player positions
###
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
