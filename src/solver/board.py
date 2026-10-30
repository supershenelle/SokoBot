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



    """
    width: int
    height: int
    map: walls and targets
    objects: players and crates
    """
    ...