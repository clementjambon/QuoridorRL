import pygame as pg

from environment import INDIRECT_OFFSETS
from interactive import INNER_CELL_SIZE, WALL_THICKNESS, CELL_SIZE, CELL_PADDING, GRID_SIZE, draw_vertical_wall, draw_horizontal_wall
from utils import add_offset, is_in_bound

# ----------------------------
# DEBUG
# ----------------------------
DEBUG_PLAYER_COLOR = (0, 0, 0)
DEBUG_OPPONENT_COLOR = (255, 255, 255)
DEBUG_TARGET_COLOR = (0, 0, 255)
REQUIRED_WALLS_COLOR = (0, 0, 255)
FORBIDDEN_WALLS_COLOR = (255, 0, 0)


def draw_debug_offsets(screen, player_pos, offset_idx):
    # Player debug pawn
    debug_player_pawn = pg.Surface((INNER_CELL_SIZE, INNER_CELL_SIZE))
    debug_player_pawn = debug_player_pawn.convert()
    debug_player_pawn.fill(DEBUG_PLAYER_COLOR)

    # Player opponent pawn
    debug_opponent_pawn = pg.Surface((INNER_CELL_SIZE, INNER_CELL_SIZE))
    debug_opponent_pawn = debug_opponent_pawn.convert()
    debug_opponent_pawn.fill(DEBUG_OPPONENT_COLOR)

    # Player target pawn
    debug_target_pawn = pg.Surface((INNER_CELL_SIZE, INNER_CELL_SIZE))
    debug_target_pawn = debug_target_pawn.convert()
    debug_target_pawn.fill(DEBUG_TARGET_COLOR)

    # Required Horizontal wall
    required_horizontal_wall = pg.Surface(
        (2 * INNER_CELL_SIZE + WALL_THICKNESS, WALL_THICKNESS))
    required_horizontal_wall = required_horizontal_wall.convert()
    required_horizontal_wall.fill(REQUIRED_WALLS_COLOR)

    # Required Vertical wall
    required_vertical_wall = pg.Surface(
        (WALL_THICKNESS, 2 * INNER_CELL_SIZE + WALL_THICKNESS))
    required_vertical_wall = required_vertical_wall.convert()
    required_vertical_wall.fill(REQUIRED_WALLS_COLOR)

    # Forbidden Horizontal wall
    forbidden_horizontal_wall = pg.Surface(
        (2 * INNER_CELL_SIZE + WALL_THICKNESS, WALL_THICKNESS))
    forbidden_horizontal_wall = forbidden_horizontal_wall.convert()
    forbidden_horizontal_wall.fill(FORBIDDEN_WALLS_COLOR)

    # Forbidden Vertical wall
    forbidden_vertical_wall = pg.Surface(
        (WALL_THICKNESS, 2 * INNER_CELL_SIZE + WALL_THICKNESS))
    forbidden_vertical_wall = forbidden_vertical_wall.convert()
    forbidden_vertical_wall.fill(FORBIDDEN_WALLS_COLOR)

    indirect_offsets = INDIRECT_OFFSETS[offset_idx]

    # Draw player pawn
    debug_player_pos = (player_pos[0] * CELL_SIZE + CELL_PADDING,
                        player_pos[1] * CELL_SIZE + CELL_PADDING)
    screen.blit(debug_player_pawn, debug_player_pos)

    # Draw opponent pawn
    debug_opponent_pos = add_offset(player_pos, indirect_offsets[1])
    debug_opponent_pos = (debug_opponent_pos[0] * CELL_SIZE + CELL_PADDING,
                          debug_opponent_pos[1] * CELL_SIZE + CELL_PADDING)
    screen.blit(debug_opponent_pawn, debug_opponent_pos)

    # Draw target pawn
    debug_target_pos = add_offset(player_pos, indirect_offsets[0])
    debug_target_pos = (debug_target_pos[0] * CELL_SIZE + CELL_PADDING,
                        debug_target_pos[1] * CELL_SIZE + CELL_PADDING)
    screen.blit(debug_target_pawn, debug_target_pos)

    # Draw required walls
    for required_wall_offset, required_wall_direction in indirect_offsets[2]:
        wall_position = add_offset(player_pos, required_wall_offset)

        if is_in_bound(wall_position, GRID_SIZE - 1):
            if required_wall_direction == 0:
                draw_horizontal_wall(screen, required_horizontal_wall,
                                     wall_position[0], wall_position[1])
            elif required_wall_direction == 1:
                draw_vertical_wall(screen, required_vertical_wall,
                                   wall_position[0], wall_position[1])

    # Draw forbidden walls
    for forbidden_wall_offset, forbidden_wall_direction in indirect_offsets[3]:
        wall_position = add_offset(player_pos, forbidden_wall_offset)

        if is_in_bound(wall_position, GRID_SIZE - 1):
            if forbidden_wall_direction == 0:
                draw_horizontal_wall(screen, forbidden_horizontal_wall,
                                     wall_position[0], wall_position[1])
            elif forbidden_wall_direction == 1:
                draw_vertical_wall(screen, forbidden_vertical_wall,
                                   wall_position[0], wall_position[1])
