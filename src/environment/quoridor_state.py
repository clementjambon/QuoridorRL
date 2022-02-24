import numpy as np
from environment import QuoridorConfig

# TODO: extand this in case of bigger grid_size
XGRAD = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
YGRAD = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
DIRGRAD = ["h", "v"]


class QuoridorState:

    def __init__(self, game_config: QuoridorConfig) -> None:
        self.grid_size = game_config.grid_size

        # Set time and outcome-dependent variables
        self.t = 0
        self.done = False
        self.winner = -1

        # player positions
        self.player_positions = [(0, self.grid_size // 2),
                                 (self.grid_size - 1, self.grid_size // 2)]

        # number of already placed walls for a given player
        self.nb_walls = [0, 0]

        # (grid_size - 1)x(grid_size - 1) 2d int8 array to store the wall positions at intersections
        # -1 stands for empty
        # 0 stands for a wall along x
        # 1 stands for a wall along y
        self.walls = np.full((self.grid_size - 1, self.grid_size - 1),
                             -1,
                             dtype=np.int8)

        # initialize the current player
        self.current_player = 0

    def to_string(self, invariance=True, add_nb_walls=False):
        # invariance specifies whether we make it invariant to the current player or not
        # add_nb_walls specifies whether we add the number of remaining walls for each player at the end of the string
        state_str = ""
        if invariance:
            invariant_pos = np.roll(self.player_positions, self.current_player)
            invariant_nb_walls = np.roll(self.nb_walls, self.current_player)
            invariant_walls = np.rot90(self.walls, 2 * self.current_player)
        else:
            invariant_pos = self.player_positions
            invariant_nb_walls = self.nb_walls
            invariant_walls = self.walls

        for pos in invariant_pos:
            state_str += XGRAD[pos[0]] + YGRAD[pos[1]] + ";"
        for i in range(self.grid_size - 1):
            for j in range(self.grid_size - 1):
                if invariant_walls[i, j] >= 0:
                    state_str += XGRAD[i] + YGRAD[j] + DIRGRAD[invariant_walls[
                        i, j]] + ";"

        if add_nb_walls:
            state_str += "p0:" + str(
                invariant_nb_walls[0]) + ";" + "p1:" + str(
                    invariant_nb_walls[1]) + ";"

        print(state_str)

        return state_str
        # return str(np.rot90(self.walls, 2 * self.current_player)) + str(
        #     np.roll(self.player_positions, self.current_player)) + str(
        #         np.roll(self.nb_walls, self.current_player))
