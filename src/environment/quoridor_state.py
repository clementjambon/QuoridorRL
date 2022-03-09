import numpy as np
from environment import QuoridorConfig
from utils import string_to_coords

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

    def load_from_string(self, state_str: str):
        splits = state_str.split(";")
        # Map positions
        self.player_positions[0] = string_to_coords(splits[0])
        self.player_positions[1] = string_to_coords(splits[1])
        # Map walls
        for i in range(2, len(splits) - 5):
            wall_position = string_to_coords(splits[i])
            wall_direction = 0 if splits[i][2] == 'h' else 1
            self.walls[wall_position] = wall_direction
        # Map nb_walls
        self.nb_walls[0] = int(splits[len(splits) - 5][3:])
        self.nb_walls[1] = int(splits[len(splits) - 4][3:])
        # Map current player
        self.current_player = int(splits[len(splits) - 3][1])
        # Map time
        print(splits[len(splits) - 2].split(":"))
        self.t = int(splits[len(splits) - 2].split(":")[1])
        print(self.t)

    def to_string(self,
                  invariance=False,
                  add_nb_walls=True,
                  add_current_player=True,
                  add_time=True):
        # invariance specifies whether we make it invariant to the current player or not
        # add_nb_walls specifies whether we add the number of remaining walls for each player at the end of the string
        state_str = ""
        if invariance and self.current_player == 1:
            invariant_pos = [
                self.player_positions[1], self.player_positions[0]
            ]
            invariant_nb_walls = [self.nb_walls[1], self.nb_walls[0]]
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

        if add_current_player:
            state_str += "p" + str(self.current_player) + ";"

        if add_time:
            state_str += "t:" + str(self.t) + ";"

        return state_str
        # return str(np.rot90(self.walls, 2 * self.current_player)) + str(
        #     np.roll(self.player_positions, self.current_player)) + str(
        #         np.roll(self.nb_walls, self.current_player))
