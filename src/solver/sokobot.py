import time

from src.solver.board import Board
from src.solver.A_star import A_star


class SokoBot:
    def solveSokobanPuzzle(self, width, height, mapData, itemsData):
        
        board = Board(width, height, mapData, itemsData)

        if board.start_player is None:
            return ""

        return A_star(board)