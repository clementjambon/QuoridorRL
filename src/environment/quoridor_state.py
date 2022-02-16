import numpy as np

from utils import add_offset, is_in_bound, coords_to_tile
from utils import UnionFind


class QuoridorState:

    empty_move_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    # Offsets used if the adjacent cell is not empty
    occupied_move_offsets = [[(-1, -1), (-1, 1)], [(1, -1), (1, 1)],
                             [(-1, -1), (1, -1)], [(-1, 1), (1, 1)]]

    # Pairs of (offset, direction) wall offsets that get to connect components
    # a "direction" offset of 0 means that walls must be aligned in the provided direction
    wall_offsets = [(-1, 1), (1, 1), (-2, 0), (2, 0)]

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

        # number of already placed walls for a given player
        self.nb_walls = [0, 0]

        # (grid_size - 1)x(grid_size - 1) 2d int8 array to store the wall positions at intersections
        # 0 stands for empty
        # 1 stands for horizontal wall
        # 2 stands for vertical wall
        self.walls_state = np.full((self.grid_size - 1, self.grid_size - 1),
                                   -1,
                                   dtype=np.int8)

        # union-find structure used for valid wall testing
        # the structure includes all possible walls AND the 4 grid boundaries
        self.ufind = UnionFind((self.grid_size - 1) * (self.grid_size - 1) + 4)
        self.size_wall_grid = (self.grid_size - 1) * (self.grid_size - 1)

    def get_opponent(self, player_idx: int) -> int:
        return (player_idx + 1) % self.nb_players

    def can_move_player(self, player_idx: int, target_position) -> bool:
        # Make sure the target position is in bound
        if not is_in_bound(target_position, self.grid_size):
            return False
        # Compute valid targets
        player_position = self.player_positions[player_idx]
        valid_targets = set()
        for i, offset in enumerate(self.empty_move_offsets):
            potential_target = add_offset(player_position, offset)
            if is_in_bound(potential_target, self.grid_size):
                # Check that the corresponding cell is empty
                if potential_target != self.player_positions[self.get_opponent(
                        player_idx)]:
                    valid_targets.add(potential_target)
                # Otherwise, add all other in-bound targets based of occupied_offsets
                else:
                    for occupied_offset in self.occupied_move_offsets[i]:
                        new_target = add_offset(player_position,
                                                occupied_offset)
                        if is_in_bound(new_target, self.grid_size):
                            valid_targets.add(new_target)

        # Check that the target_position is within valid distance of the player
        if target_position in valid_targets:
            return True
        else:
            return False

    def move_player(self, player_idx: int, target_position) -> None:
        self.player_positions[player_idx] = target_position

    def player_win(self, player_idx: int) -> None:
        target_line = self.grid_size - 1 if player_idx == 0 else 0
        return (self.player_positions[player_idx][0] == target_line)

    def can_place_wall(self, player_idx: int, wall_position,
                       direction: int) -> bool:
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
            if wall_position[0] < self.grid_size - 1 and self.walls_state[(
                    wall_position[0] + 1, wall_position[1])] == 0:
                return False
        if direction == 1:
            # One cannot place walls if there is already a wall of the same direction in the axis-aligned adjacent intersections
            if wall_position[1] > 0 and self.walls_state[(
                    wall_position[0], wall_position[1] - 1)] == 1:
                return False
            if wall_position[1] < self.grid_size - 1 and self.walls_state[(
                    wall_position[0], wall_position[1] + 1)] == 0:
                return False

        # Check connected components
        # this list records the potentially merged cc
        merged_cc = []
        boundary_cc = {
            self.ufind.find(self.size_wall_grid),
            self.ufind.find(self.size_wall_grid + 1),
            self.ufind.find(self.size_wall_grid + 2),
            self.ufind.find(self.size_wall_grid + 3)
        }
        for offset in self.wall_offsets:
            potential_position = wall_position
            potential_position[offset[1]] += offset[0]

            # Check bounds first
            # 1. with other walls
            if is_in_bound(potential_position, self.grid_size - 1):
                # Connect if walls are "connectable" wall at the potential_position
                if self.walls_state[potential_position] == (direction +
                                                            offset[0]) % 2:
                    tile_potential = coords_to_tile(potential_position,
                                                    self.grid_size - 1)
                    merged_cc.append(self.ufind.find(tile_potential))
            # 2. with the boundaries of the board as well
            if potential_position[0] == -2:
                merged_cc.append(self.ufind.find(self.size_wall_grid))
            if potential_position[1] == -2:
                merged_cc.append(self.ufind.find(self.size_wall_grid + 1))
            if potential_position[0] == self.grid_size:
                merged_cc.append(self.ufind.find(self.size_wall_grid + 2))
            if potential_position[1] == self.grid_size:
                merged_cc.append(self.ufind.find(self.size_wall_grid + 3))

        # If it connects twice the boundaries by being placed there, reject the wall
        if len([i for i in merged_cc if i in boundary_cc]) > 1:
            return False

        return True

    def place_wall(self, player_idx: int, wall_position,
                   direction: int) -> None:
        self.nb_walls[player_idx] += 1
        self.walls_state[wall_position] = direction
        # Update the ufind structure accordingly
        for offset in self.wall_offsets:
            potential_position = wall_position
            potential_position[offset[1]] += offset[0]

            tile_current = coords_to_tile(wall_position, self.grid_size - 1)
            # Check bounds first
            # 1. with other walls
            if is_in_bound(potential_position, self.grid_size - 1):
                # Connect if walls are "connectable" wall at the potential_position
                if self.walls_state[potential_position] == (direction +
                                                            offset[0]) % 2:
                    tile_potential = coords_to_tile(potential_position,
                                                    self.grid_size - 1)
                    self.ufind.union(tile_current, tile_potential)
            # 2. with the boundaries of the board as well
            if potential_position[0] == -2:
                self.ufind.union(self.size_wall_grid, tile_current)
            if potential_position[1] == -2:
                self.ufind.union(self.size_wall_grid + 1, tile_current)
            if potential_position[0] == self.grid_size:
                self.ufind.union(self.size_wall_grid + 2, tile_current)
            if potential_position[1] == self.grid_size:
                self.ufind.union(self.size_wall_grid + 3, tile_current)
