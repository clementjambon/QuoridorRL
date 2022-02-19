import numpy as np

from utils import add_offset, is_in_bound
from utils import PathFinder

# Offsets are defined as (pos_offset, wall_offsets, wall_direction)
DIRECT_OFFSETS = [((-1, 0), [(-1, 0), (-1, -1)], 1),
                  ((1, 0), [(0, 0), (0, -1)], 1),
                  ((0, -1), [(0, -1), (-1, -1)], 0),
                  ((0, 1), [(0, 0), (-1, 0)], 0)]

# Indirect offsets are defined as (pos_offset, opponent_offset, required_wall_offsets, forbidden_wall_offsets)
# # where wall_offset = (wall_pos_offset, wall_direction)
INDIRECT_OFFSETS = [
    # Used for hopping over pawn without blocking wall
    ((-2, 0), (-1, 0), [], [((-2, 0), 1), ((-2, -1), 1)]),
    ((2, 0), (1, 0), [], [((1, 0), 1), ((1, -1), 1)]),
    ((0, -2), (0, -1), [], [((0, -2), 0), ((-1, -2), 0)]),
    ((0, 2), (0, 1), [], [((0, 1), 0), ((-1, 1), 0)]),
    # Used when there is a blocking wall
    ((-1, -1), (-1, 0), [((-2, 0), 1), ((-2, -1), 1)], [((-1, -1), 0),
                                                        ((-1, -1), 1),
                                                        ((-1, 0), 1)]),
    ((-1, -1), (0, -1), [((0, -2), 0), ((-1, -2), 0)], [((-1, -1), 1),
                                                        ((-1, -1), 0),
                                                        ((0, -1), 0)]),
    ((1, -1), (0, -1), [((0, -2), 0), ((-1, -2), 0)], [((-1, -1), 0),
                                                       ((0, -1), 0),
                                                       ((0, -1), 1)]),
    ((1, -1), (1, 0), [((1, 0), 1), ((1, -1), 1)], [
        ((0, -1), 1),
        ((0, 0), 1),
        ((0, -1), 0),
    ]),
    ((1, 1), (1, 0), [((1, 0), 1), ((1, -1), 1)], [((0, -1), 1), ((0, 0), 1),
                                                   ((0, 0), 0)]),
    ((1, 1), (0, 1), [((-1, 1), 0), ((0, 1), 0)], [((-1, 0), 0), ((0, 0), 0),
                                                   ((0, 0), 1)]),
    ((-1, 1), (0, 1), [((-1, 1), 0), ((0, 1), 0)], [((-1, 0), 0), ((0, 0), 0),
                                                    ((-1, 0), 1)]),
    ((-1, 1), (-1, 0), [((-2, 0), 1), ((-2, -1), 1)], [((-1, 0), 0),
                                                       ((-1, -1), 1),
                                                       ((-1, 0), 1)])
]


class QuoridorState:

    def __init__(self, grid_size: int = 9) -> None:
        self.grid_size = grid_size
        # pairs used for wall tiling
        self.pairs = np.array([(i, j) for i in range(self.grid_size - 1)
                               for j in range(self.grid_size - 1)])

        # TODO: "de-hardcode" this!
        self.nb_players = 2
        self.max_walls = 10  # the maximum number of walls per player

        # player positions
        self.player_positions = [(0, self.grid_size // 2),
                                 (self.grid_size - 1, self.grid_size // 2)]
        # player x_targets (TODO: change this to handle more players)
        self.x_targets = [self.grid_size - 1, 0]

        # number of already placed walls for a given player
        self.nb_walls = [0, 0]

        # (grid_size - 1)x(grid_size - 1) 2d int8 array to store the wall positions at intersections
        # -1 stands for empty
        # 0 stands for a wall along x
        # 1 stands for a wall along y
        self.walls_state = np.full((self.grid_size - 1, self.grid_size - 1),
                                   -1,
                                   dtype=np.int8)

        # initialize the pathfinder used to check valid wall placement
        self.pathfinder = PathFinder(self.grid_size)

    def get_opponent(self, player_idx: int) -> int:
        return (player_idx + 1) % self.nb_players

    def get_neighbouring_cells(self, pos):
        neighbouring_cells = set()
        if pos[0] > 0:
            neighbouring_cells.add((pos[0] - 1, pos[1]))
        if pos[1] > 0:
            neighbouring_cells.add((pos[0], pos[1] - 1))
        if pos[0] < self.grid_size - 1:
            neighbouring_cells.add((pos[0] + 1, pos[1]))
        if pos[1] < self.grid_size - 1:
            neighbouring_cells.add((pos[0], pos[1] + 1))
        return neighbouring_cells

    def can_move_player(self, player_idx: int, target_position) -> bool:
        # Make sure the target position is in bound
        if not is_in_bound(target_position, self.grid_size):
            return False

        # Make sure the other player is not standing at the target_position
        if target_position == self.player_positions[self.get_opponent(
                player_idx)]:
            return False
        player_pos = self.player_positions[player_idx]

        # Check direct moves
        for pos_offset, wall_offsets, wall_direction in DIRECT_OFFSETS:
            if target_position == add_offset(player_pos, pos_offset):
                for wall_offset in wall_offsets:
                    wall_position = add_offset(player_pos, wall_offset)
                    if is_in_bound(
                            wall_position, self.grid_size - 1
                    ) and self.walls_state[wall_position] == wall_direction:
                        return False
                return True

        # Check moves with hopping
        for pos_offset, opponent_offset, required_wall_offsets, forbidden_wall_offsets in INDIRECT_OFFSETS:
            if target_position == add_offset(
                    self.player_positions[player_idx],
                    pos_offset) and self.player_positions[self.get_opponent(
                        player_idx)] == add_offset(
                            self.player_positions[player_idx],
                            opponent_offset):

                found_required_wall = False
                one_in_bound = False
                for required_wall_offset, required_wall_direction in required_wall_offsets:
                    wall_position = add_offset(player_pos,
                                               required_wall_offset)

                    if is_in_bound(wall_position, self.grid_size - 1):
                        one_in_bound = True
                        if self.walls_state[
                                wall_position] == required_wall_direction:
                            found_required_wall = True
                            break
                        else:
                            return False
                if one_in_bound and not found_required_wall:
                    return False

                for forbidden_wall_offset, forbidden_wall_direction in forbidden_wall_offsets:
                    wall_position = add_offset(player_pos,
                                               forbidden_wall_offset)
                    if is_in_bound(
                            wall_position,
                            self.grid_size - 1) and self.walls_state[
                                wall_position] == forbidden_wall_direction:
                        return False

                return True

        return False

    def move_player(self, player_idx: int, target_position) -> None:
        self.player_positions[player_idx] = target_position

    def player_win(self, player_idx: int) -> None:
        return (
            self.player_positions[player_idx][0] == self.x_targets[player_idx])

    def can_place_wall(self, player_idx: int, wall_position,
                       direction: int) -> bool:
        # Make sure the target position is in bound
        if not is_in_bound(wall_position, self.grid_size - 1):
            return False
        # Make sure the player has not used all of its walls yet
        if self.nb_walls[player_idx] >= self.max_walls:
            return
        # Make sure the intersection is not already used by a wall
        if self.walls_state[wall_position] != -1:
            return False

        # Check potential intersections
        if direction == 0:
            # One cannot place walls if there is already a wall of the same direction in the axis-aligned adjacent intersections
            if wall_position[0] > 0 and self.walls_state[(
                    wall_position[0] - 1, wall_position[1])] == 0:
                return False
            if wall_position[0] < self.grid_size - 2 and self.walls_state[(
                    wall_position[0] + 1, wall_position[1])] == 0:
                return False
        if direction == 1:
            # One cannot place walls if there is already a wall of the same direction in the axis-aligned adjacent intersections
            if wall_position[1] > 0 and self.walls_state[(
                    wall_position[0], wall_position[1] - 1)] == 1:
                return False
            if wall_position[1] < self.grid_size - 2 and self.walls_state[(
                    wall_position[0], wall_position[1] + 1)] == 0:
                return False

        # Test pathfinding i.e make sure he cannot block the opponent from reaching its goal (in practice, he can block himself)
        self.walls[wall_position] = direction
        opponent_idx = self.get_opponent(player_idx)
        if not self.pathfinder.check_path(self.walls,
                                          self.player_positions[opponent_idx],
                                          self.x_targets[opponent_idx]):
            self.walls[wall_position] = -1
            return False
        self.walls[wall_position] = -1

        return True

    def place_wall(self, player_idx: int, wall_position,
                   direction: int) -> None:
        self.nb_walls[player_idx] += 1
        self.walls_state[wall_position] = direction
