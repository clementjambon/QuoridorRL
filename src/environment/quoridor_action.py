class QuoridorAction:

    def __init__(self) -> None:
        pass

    def to_string(self) -> str:
        pass


# TODO: extand this in case of bigger grid_size
XGRAD = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
YGRAD = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
DIRGRAD = ["h", "v"]


class MoveAction(QuoridorAction):

    def __init__(self, player_pos, player_idx: int) -> None:
        super().__init__()
        self.player_pos = player_pos
        self.player_idx = player_idx

    def to_string(self) -> str:
        return XGRAD[self.player_pos[0]] + YGRAD[self.player_pos[1]]


class WallAction(QuoridorAction):

    def __init__(self, wall_position, wall_direction: int) -> None:
        super().__init__()
        self.wall_position = wall_position
        self.wall_direction = wall_direction

    def to_string(self) -> str:
        return XGRAD[self.wall_position[0]] + YGRAD[
            self.wall_position[1]] + DIRGRAD[self.wall_direction]
