def add_offset(position, offset):
    return (position[0] + offset[0], position[1] + offset[1])


def get_offset(from_pos, to_pos):
    return (to_pos[0] - from_pos[0], to_pos[1] - from_pos[1])


def is_in_bound(position, side_length: int) -> bool:
    return (position[0] >= 0 and position[1] >= 0 and position[0] < side_length
            and position[1] < side_length)


def tile_to_coords(i: int, side_length: int):
    '''
        Return position coordinates given tile number.
    '''
    if i < 0:
        return None
    return (i // side_length, i % side_length)


def coords_to_tile(coords, side_length: int):
    '''
        Return tile ID given coordinates in 2D array 'coords'.
    '''
    i = coords[0] * side_length + coords[1]
    if i < side_length * side_length:
        return i
    return -1


X_STR_MAP = {
    '1': 0,
    '2': 1,
    '3': 2,
    '4': 3,
    '5': 4,
    '6': 5,
    '7': 6,
    '8': 7,
    '9': 8
}
Y_STR_MAP = {
    'a': 0,
    'b': 1,
    'c': 2,
    'd': 3,
    'e': 4,
    'f': 5,
    'g': 6,
    'h': 7,
    'i': 8
}


def string_to_coords(pos_str: str):
    return (X_STR_MAP[pos_str[0]], Y_STR_MAP[pos_str[1]])


# TODO: improve the efficiency of this
def change_action_perspective(perspective_player, action_idx, grid_size: int):
    if perspective_player == 0:
        return action_idx

    if action_idx < grid_size * grid_size:
        move_coord = tile_to_coords(action_idx, grid_size)
        move_coord = (grid_size - 1 - move_coord[0],
                      grid_size - 1 - move_coord[1])
        return coords_to_tile(move_coord, grid_size)
    else:
        action_idx -= grid_size * grid_size
        if action_idx < (grid_size - 1) * (grid_size - 1):
            wall_coord = tile_to_coords(action_idx, grid_size - 1)
            wall_coord = (grid_size - 2 - wall_coord[0],
                          grid_size - 2 - wall_coord[1])
            return grid_size * grid_size + coords_to_tile(
                wall_coord, grid_size - 1)
        else:
            action_idx -= (grid_size - 1) * (grid_size - 1)
            wall_coord = tile_to_coords(action_idx, grid_size - 1)
            wall_coord = (grid_size - 2 - wall_coord[0],
                          grid_size - 2 - wall_coord[1])
            return grid_size * grid_size + (grid_size - 1) * (
                grid_size - 1) + coords_to_tile(wall_coord, grid_size - 1)
