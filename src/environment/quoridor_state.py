import numpy as np


class QuoridorState:

    def __init__(self, grid_size=9) -> None:
        # Set time and outcome-dependent variables
        self.t = 0
        self.done = False
        self.winner = -1

        # player positions
        self.player_positions = [(0, grid_size // 2),
                                 (grid_size - 1, grid_size // 2)]

        # number of already placed walls for a given player
        self.nb_walls = [0, 0]

        # (grid_size - 1)x(grid_size - 1) 2d int8 array to store the wall positions at intersections
        # -1 stands for empty
        # 0 stands for a wall along x
        # 1 stands for a wall along y
        self.walls = np.full((grid_size - 1, grid_size - 1), -1, dtype=np.int8)

        # initialize the current player
        self.current_player = 0
