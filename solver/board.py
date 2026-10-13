from solver.state import State

class Board:
    def __init__(self, width, height, map, objects):
        self.width = width
        self.height = height
        self.map = map
        self.objects = objects

def map_info(width, height, map, objects):
    walls, targets, crates = [], [], []
    for row in range(height): 
        for col in range(width):
            if map[row][col] == '#':
                walls.append((row, col))
            elif map[row][col] == '.':
                targets.append((row, col))
            elif map[row][col] == '$':
                crates.append((row, col))



    """
    width: int
    height: int
    map: walls and goal
    objects: players and boxes
    """
    ...