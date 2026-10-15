from src.solver.state import State

class Board:
    def __init__(self, width, height, map, objects):
        self.width = width
        self.height = height
        self.map = map
        self.objects = objects

def map_info(width, height, map, objects):
    walls, targets, crates = [], [], []  #check if may better data struct to represent this
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