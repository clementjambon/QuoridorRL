from argparse import Action
from enum import Enum
import sys
import os
from matplotlib.pyplot import draw
import pygame as pg

if not pg.font:
    print("Warning, fonts disabled")

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from environment import QuoridorEnv

# ----------------------------
# COLORS
# ----------------------------
EMPTY_CELL_COLOR = (204, 190, 171)
WALL_COLOR = (116, 102, 242)
PAWN_0_COLOR = (255, 255, 255)
PAWN_1_COLOR = (0, 0, 0)
TEXT_COLOR = (10, 10, 10)

# ----------------------------
# CONSTANTS
# ----------------------------
SIZE = WIDTH, HEIGHT = 720, 900
FPS = 60
GRID_SIZE = 9
CELL_SIZE = 80
WALL_THICKNESS = 10
CELL_PADDING = WALL_THICKNESS / 2
INNER_CELL_SIZE = CELL_SIZE - WALL_THICKNESS

ACTION_DESCRIPTIONS = ["Move pawn", "Add horizontal wall", "Add vertical wall"]

# TODO: make cells subsurfaces of the big cell


def handle_click(environment: QuoridorEnv, action_mode: int):
    mouse_pos = pg.mouse.get_pos()
    if action_mode == 0:
        target_position = (mouse_pos[0] // CELL_SIZE,
                           mouse_pos[1] // CELL_SIZE)
        environment.move_pawn(target_position)
    else:
        target_position = (int((mouse_pos[0] - CELL_SIZE / 2) // CELL_SIZE),
                           int((mouse_pos[1] - CELL_SIZE / 2) // CELL_SIZE))
        direction = 0 if action_mode == 1 else 1
        environment.add_wall(target_position, direction)


def draw_gui(screen, environment: QuoridorEnv, action_mode: int, done: bool):
    if pg.font:
        font = pg.font.Font(None, 64)
        player_text = font.render(
            f"Player {environment.current_player} is playing", True,
            TEXT_COLOR)
        player_text_pos = (0, GRID_SIZE * CELL_SIZE)
        screen.blit(player_text, player_text_pos)

        action_text = font.render(
            f"Action: {ACTION_DESCRIPTIONS[action_mode]}", True, TEXT_COLOR)
        action_text_pos = (0, GRID_SIZE * CELL_SIZE + 64)
        screen.blit(action_text, action_text_pos)

        if done:
            done_text = font.render(f"Game is over!", True, TEXT_COLOR)
            done_text_pos = (0, GRID_SIZE * CELL_SIZE + 64 * 2)
            screen.blit(done_text, done_text_pos)


def draw_board(screen, cell):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            pixel_coord = (i * CELL_SIZE + CELL_PADDING,
                           j * CELL_SIZE + CELL_PADDING)
            screen.blit(cell, pixel_coord)


def draw_state(screen, environment: QuoridorEnv, pawn_0, pawn_1,
               horizontal_wall, vertical_wall):
    # Draw pawn 0
    pawn_0_position = environment.state.player_positions[0]
    pawn_0_position = (pawn_0_position[0] * CELL_SIZE + CELL_PADDING,
                       pawn_0_position[1] * CELL_SIZE + CELL_PADDING)
    screen.blit(pawn_0, pawn_0_position)
    # Draw pawn 1
    pawn_1_position = environment.state.player_positions[1]
    pawn_1_position = (pawn_1_position[0] * CELL_SIZE + CELL_PADDING,
                       pawn_1_position[1] * CELL_SIZE + CELL_PADDING)
    screen.blit(pawn_1, pawn_1_position)

    # Draw walls
    for i in range(0, GRID_SIZE - 1):
        for j in range(0, GRID_SIZE - 1):
            # Draw horizontal wall (i.e along x)
            if (environment.state.walls_state[i, j] == 0):
                wall_position = (CELL_PADDING + i * CELL_SIZE, CELL_PADDING +
                                 INNER_CELL_SIZE + CELL_SIZE * j)
                screen.blit(horizontal_wall, wall_position)
            # Draw vertical wall (i.e along y)
            elif (environment.state.walls_state[i,
                                                j] == 1):  # Draw vertical wall
                wall_position = (CELL_PADDING + INNER_CELL_SIZE +
                                 CELL_SIZE * i, CELL_PADDING + j * CELL_SIZE)
                screen.blit(vertical_wall, wall_position)


def main():

    # Initialize Quoridor Environment
    environment = QuoridorEnv()
    done = False

    # Initialize action mode
    action_mode = 0

    pg.init()
    screen = pg.display.set_mode(SIZE, pg.SCALED)
    pg.display.set_caption("QuoridorRL")

    # Background
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill((170, 238, 187))

    # Cell surface
    cell = pg.Surface((INNER_CELL_SIZE, INNER_CELL_SIZE))
    cell = cell.convert()
    cell.fill(EMPTY_CELL_COLOR)

    # Player 0 (white) pawn
    pawn_0 = pg.Surface((INNER_CELL_SIZE, INNER_CELL_SIZE))
    pawn_0 = pawn_0.convert()
    pawn_0.fill(PAWN_0_COLOR)

    # Player 1 (black) pawn
    pawn_1 = pg.Surface((INNER_CELL_SIZE, INNER_CELL_SIZE))
    pawn_1 = pawn_1.convert()
    pawn_1.fill(PAWN_1_COLOR)

    # Horizontal wall
    horizontal_wall = pg.Surface(
        (2 * INNER_CELL_SIZE + WALL_THICKNESS, WALL_THICKNESS))
    horizontal_wall = horizontal_wall.convert()
    horizontal_wall.fill(WALL_COLOR)

    # Vertical wall
    vertical_wall = pg.Surface(
        (WALL_THICKNESS, 2 * INNER_CELL_SIZE + WALL_THICKNESS))
    vertical_wall = vertical_wall.convert()
    vertical_wall.fill(WALL_COLOR)

    # Display the background
    screen.blit(background, (0, 0))
    pg.display.flip()

    clock = pg.time.Clock()

    rendering = True
    while rendering:
        clock.tick(FPS)

        # handle input events
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.K_ESCAPE:
                rendering = False
            # TODO: handle key down
            elif event.type == pg.MOUSEBUTTONDOWN:
                handle_click(environment, action_mode)
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                action_mode = (action_mode + 1) % 3
        # draw
        screen.blit(background, (0, 0))
        draw_board(screen, cell)
        draw_state(screen, environment, pawn_0, pawn_1, horizontal_wall,
                   vertical_wall)
        draw_gui(screen, environment, action_mode, done)
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()