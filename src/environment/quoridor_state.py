import numpy as np
from environment import QuoridorConfig


class QuoridorState:

    def __init__(self, game_config: QuoridorConfig) -> None:
        # Set time and outcome-dependent variables
        self.t = 0
        self.done = False
        self.winner = -1

        # player positions
        self.player_positions = [(0, game_config.grid_size // 2),
                                 (game_config.grid_size - 1,
                                  game_config.grid_size // 2)]

        # number of already placed walls for a given player
        self.nb_walls = [0, 0]

        # (grid_size - 1)x(grid_size - 1) 2d int8 array to store the wall positions at intersections
        # -1 stands for empty
        # 0 stands for a wall along x
        # 1 stands for a wall along y
        self.walls = np.full(
            (game_config.grid_size - 1, game_config.grid_size - 1),
            -1,
            dtype=np.int8)

        # initialize the current player
        self.current_player = 0

    def to_string(self):
        # TODO: check that we do not to take into account invariances here
        return str(self.walls) + str(self.player_positions) + str(
            self.nb_walls)
