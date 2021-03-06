class QuoridorAction:
    """Interface for Quoridor actions
    """

    def __init__(self) -> None:
        self.type = None

    def to_string(self) -> str:
        pass

    def to_perspective(self, perspective_player: int, grid_size: int):
        pass

    def to_index(self, grid_size: int) -> int:
        pass

    def __eq__(self, other) -> bool:
        pass


# to_string implementations follow the notations described in
# https://en.wikipedia.org/wiki/Quoridor#Notation

# TODO: extand this in case of bigger grid_size
XGRAD = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
YGRAD = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
DIRGRAD = ["h", "v"]


class MoveAction(QuoridorAction):
    """Action for pawn movement
    """

    def __init__(self, player_pos, player_idx: int) -> None:
        super().__init__()
        self.player_pos = player_pos
        self.player_idx = player_idx
        self.type = 0

    def to_string(self) -> str:
        return XGRAD[self.player_pos[0]] + YGRAD[self.player_pos[1]]

    def to_index(self, grid_size: int) -> int:
        return grid_size * self.player_pos[0] + self.player_pos[1]

    def to_perspective(self, perspective_player: int, grid_size: int):
        if perspective_player == 0:
            return self
        else:
            self.player_pos = (grid_size - 1 - self.player_pos[0],
                               grid_size - 1 - self.player_pos[1])
            return self

    def __eq__(self, other) -> bool:
        return self.type == other.type and self.player_idx == other.player_idx and self.player_pos[
            0] == other.player_pos[0] and self.player_pos[
                1] == other.player_pos[1]


class WallAction(QuoridorAction):
    """Action for wall placement
    """

    def __init__(self, wall_position, wall_direction: int) -> None:
        super().__init__()
        self.wall_position = wall_position
        self.wall_direction = wall_direction
        self.type = 1

    def to_string(self) -> str:
        return XGRAD[self.wall_position[0]] + YGRAD[
            self.wall_position[1]] + DIRGRAD[self.wall_direction]

    def to_index(self, grid_size: int) -> int:
        return grid_size * grid_size + (grid_size - 1) * (
            grid_size - 1) * self.wall_direction + (
                grid_size - 1) * self.wall_position[0] + self.wall_position[1]

    def to_perspective(self, perspective_player: int, grid_size: int):
        if perspective_player == 0:
            return self
        else:
            self.wall_position = (grid_size - 2 - self.wall_position[0],
                                  grid_size - 2 - self.wall_position[1])
            return self

    def __eq__(self, other) -> bool:
        return self.type == other.type and self.wall_direction == other.wall_direction and self.wall_position[
            0] == other.wall_position[0] and self.wall_position[
                1] == other.wall_position[1]
