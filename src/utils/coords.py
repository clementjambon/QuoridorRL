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


def convert_poscoord_to_posnodenb(posCoord: tuple[int, int],
                                  grid_size: int) -> int:
    '''
    Return node nb in graph representation given coordinates in 2D array 'coords'.
    '''
    node_nb = posCoord[1] + grid_size * posCoord[0]
    return node_nb