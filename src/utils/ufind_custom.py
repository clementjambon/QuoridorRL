import numpy as np
from utils import coords_to_tile, add_offset, is_in_bound, tile_to_coords

OFFSETS_X = (((-2, 0), 0), ((2, 0), 0), ((-1, -1), 1), ((0, -1), 1),
             ((1, -1), 1), ((-1, 1), 1), ((0, 1), 1), ((1, 1), 1))
OFFSETS_Y = (((0, -2), 1), ((0, 2), 1), ((-1, -1), 0), ((-1, 0), 0),
             ((-1, 1), 0), ((1, -1), 0), ((1, 0), 0), ((1, 1), 0))


def compare0(adjacent1, adjacent2):
    entry1, border1 = adjacent1
    entry2, border2 = adjacent2

    if ((border1 + 1) % 4) != ((border2 + 1) % 4):
        return ((border1 + 1) % 4) - ((border2 + 1) % 4)
    # In the case where it touches the same border
    else:
        border_direction = 1 - border1 % 2
        return entry1[border_direction] - entry2[border_direction]


def compare1(adjacent1, adjacent2):
    entry1, border1, parent1 = adjacent1
    entry2, border2, parent2 = adjacent2

    if ((border1 + 1) % 4) != ((border2 + 1) % 4):
        return ((border1 + 1) % 4) - ((border2 + 1) % 4)
    # In the case where it touches the same border
    else:
        border_direction = 1 - border1 % 2
        return entry1[border_direction] - entry2[border_direction]


# Basic union-find structure with parents flattening for O(1) queries
class UFindCustom:
    def __init__(self, grid_size: int) -> None:
        # Initialize as many elements as there are possible wall spots
        self.nb_elements = 2 * (grid_size - 1) * (grid_size - 1) + 4
        self.border_threshold = 2 * (grid_size - 1) * (grid_size - 1)
        self.grid_size = grid_size
        self.border_rep = [i for i in range(self.nb_elements)]
        self.parents = [i for i in range(self.nb_elements)]
        self.children = [i for i in range(self.nb_elements)]
        self.entry_pos = [(-1, -1) for _ in range(self.nb_elements)]

    def wall_to_tile(self, pos, direction):
        if direction == 0:
            return coords_to_tile(pos, self.grid_size - 1)
        else:
            return coords_to_tile(
                pos, self.grid_size -
                1) + (self.grid_size - 1) * (self.grid_size - 1)

    def tile_to_wall_pos(self, tile):
        if tile < (self.grid_size - 1) * (self.grid_size - 1):
            return tile_to_coords(tile, self.grid_size - 1)
        else:
            return tile_to_coords(
                tile - (self.grid_size - 1) * (self.grid_size - 1),
                self.grid_size - 1)

    # Returns the adjacent border index
    def get_border_adjacent(self, pos, direction):
        adjacent_list = []
        # Test borders directly
        if pos[direction] == 0:
            adjacent_list.append(
                (direction, pos, self.border_threshold + direction))
        if pos[direction] == self.grid_size - 1:
            adjacent_list.append(
                (2 + direction, pos, self.border_threshold + direction + 2))
        # Then test neighbours
        for offset, offset_dir in (OFFSETS_X if direction == 0 else OFFSETS_Y):
            nghb_pos = add_offset(pos, offset)
            if is_in_bound(nghb_pos, self.grid_size - 1):
                tile = self.wall_to_tile(nghb_pos, offset_dir)
                tile_parent = self.parents[tile]
                border_idx = self.find(tile)
                if border_idx >= self.border_threshold:
                    adjacent_list.append(
                        (self.entry_pos[tile_parent],
                         border_idx - self.border_threshold, tile_parent))
        return adjacent_list

    def player_dist(self, player_pos, wall_pos):
        return (player_pos[0] - wall_pos[0] - 0.5)**2 + (player_pos[1] -
                                                         wall_pos[1] - 0.5)**2

    def target_dist

    def find_closest_tile_to_player(self, tile, player_pos):
        min_dist = float('inf')
        closest_tile = -1
        while tile != self.parents[tile]:
            curr_dist = self.player_dist(player_pos,
                                         self.tile_to_wall_pos(tile))
            if curr_dist < min_dist:
                min_dist = curr_dist
                closest_tile = tile
            tile = self.parents[tile]
        return closest_tile

    def check_wall(self, pos, direction, player_idx, player_pos,
                   player_target):
        # First, get border adjacent
        adjacent_border = self.get_border_adjacent(pos, direction)
        # If it is empty, then no pb to add wall!
        if len(adjacent_border) == 0:
            return True
        # Otherwise, use relative position of the player
        else:
            # Sort the adjacent_border depending on the player
            adjacent_border = sorted(
                adjacent_border,
                key=(compare0 if player_idx == 0 else compare1))

            # Find closest tile to player for each path to the border
            closest_tiles = [
                self.find_closest_tile_to_player(parent_tile, player_pos)
                for entry, border, parent_tile in adjacent_border
            ]
            # TODO: add current tile ?
            closest_tile_idx = np.argmax(closest_tiles)
            tile_orientation = 0 if 

    def add_wall(self, pos, direction):
        # Convert pos to tile
        tile = self.wall_to_tile(pos, direction)
        # Test borders directly
        if pos[direction] == 0:
            self.border_rep[tile] = self.border_threshold + direction
            self.parents[tile] = self.border_threshold + direction
            self.entry_pos[tile] = pos
        if pos[direction] == self.grid_size - 1:
            self.border_rep[tile] = self.border_threshold + 2 + direction
            self.parents[tile] = self.border_threshold + 2 + direction
            self.entry_pos[tile] = pos
        # Then test neighbours
        for offset, offset_dir in (OFFSETS_X if direction == 0 else OFFSETS_Y):
            nghb_pos = add_offset(pos, offset)
            if is_in_bound(nghb_pos, self.grid_size - 1):
                nghb_tile = self.wall_to_tile(nghb_pos, offset_dir)
                self.border_rep[tile] = self.border_rep[nghb_tile]
                self.parents[tile] = nghb_tile
                self.children[nghb_tile] = tile
                # Propagates entry position
                self.entry_pos[tile] = self.entry_pos[nghb_tile]

    def find(self, i) -> int:
        # Perform flattening if necessary
        if self.border_rep[i] != i:
            self.border_rep[i] = self.find(self.border_rep[i])
        return self.border_rep[i]