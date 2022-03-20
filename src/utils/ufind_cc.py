from utils import coords_to_tile, add_offset, is_in_bound, tile_to_coords

OFFSETS_X = (((-2, 0), 0), ((2, 0), 0), ((-1, -1), 1), ((0, -1), 1),
             ((1, -1), 1), ((-1, 1), 1), ((0, 1), 1), ((1, 1), 1))
OFFSETS_Y = (((0, -2), 1), ((0, 2), 1), ((-1, -1), 0), ((-1, 0), 0),
             ((-1, 1), 0), ((1, -1), 0), ((1, 0), 0), ((1, 1), 0))


# Basic union-find structure with parents flattening for O(1) queries
class UFindCC:

    def __init__(self, grid_size: int) -> None:
        # Initialize as many elements as there are possible wall spots
        self.nb_elements = 2 * (grid_size - 1) * (grid_size - 1) + 4
        self.border_threshold = 2 * (grid_size - 1) * (grid_size - 1)
        self.grid_size = grid_size
        self.parents = [i for i in range(self.nb_elements)]

    def wall_to_tile(self, pos, direction):
        if direction == 0:
            return coords_to_tile(pos, self.grid_size - 1)
        else:
            return coords_to_tile(
                pos, self.grid_size -
                1) + (self.grid_size - 1) * (self.grid_size - 1)

    # Returns true if it adds a connected component
    def check_wall(self, pos, direction) -> bool:
        adjacent_list = []
        # Test borders directly
        if pos[direction] == 0:
            adjacent_list.append(direction)
        if pos[direction] == self.grid_size - 1:
            adjacent_list.append(direction + 2)
        # Then test neighbours
        for offset, offset_dir in (OFFSETS_X if direction == 0 else OFFSETS_Y):
            nghb_pos = add_offset(pos, offset)
            if is_in_bound(nghb_pos, self.grid_size - 1):
                nghb_tile = self.wall_to_tile(nghb_pos, offset_dir)
                border_idx = self.find(nghb_tile)
                if border_idx >= self.border_threshold:
                    adjacent_list.append(border_idx)
        return len(adjacent_list) > 1

    def add_wall(self, pos, direction):
        # Test borders directly
        tile = self.wall_to_tile(pos, direction)
        if pos[direction] == 0:
            self.parents[tile] = self.border_threshold + direction
            return
        if pos[direction] == self.grid_size - 1:
            self.parents[tile] = self.border_threshold + direction + 2
            return
        # Then test neighbours
        for offset, offset_dir in (OFFSETS_X if direction == 0 else OFFSETS_Y):
            nghb_pos = add_offset(pos, offset)
            if is_in_bound(nghb_pos, self.grid_size - 1):
                nghb_tile = self.wall_to_tile(nghb_pos, offset_dir)
                if self.parents[nghb_tile] != nghb_tile:
                    self.union(tile, nghb_tile)
                    return

    def get_wall_cc(self, pos, direction):
        if direction < 0:
            return -1
        tile = self.wall_to_tile(pos, direction)
        return self.find(tile)

    def find(self, i) -> int:
        # Perform flattening if necessary
        if self.parents[i] != i:
            self.parents[i] = self.find(self.parents[i])
        return self.parents[i]

    def union(self, i, j) -> None:
        root_i = self.find(i)
        root_j = self.find(j)
        # If they are not already in the same CC, connect them
        if root_i != root_j:
            if root_i >= self.border_threshold:
                self.parents[root_j] = root_i
            else:
                self.parents[root_i] = root_j
