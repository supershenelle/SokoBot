import time

from src.solver.board import Board
from src.solver.astar import astar


class SokoBot:
    def solveSokobanPuzzle(self, width, height, mapData, itemsData):
        # YOU NEED TO REWRITE THE IMPLEMENTATION OF THIS METHOD TO MAKE THE BOT SMARTER
        # Default stupid behavior: Think (sleep) for 3 seconds, and then return a
        # sequence
        # that just moves left and right repeatedly.
        board = Board(width, height, mapData, itemsData)

        if board.start_player is None:
            return ""

        return astar(board)