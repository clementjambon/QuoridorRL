import sys
import os
from matplotlib.pyplot import draw
import pygame as pg

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

# ----------------------------
# CONSTANTS
# ----------------------------
SIZE = WIDTH, HEIGHT = 720, 720
FPS = 60
GRID_SIZE = 9
CELL_SIZE = 80
WALL_THICKNESS = 10
CELL_PADDING = WALL_THICKNESS / 2
INNER_CELL_SIZE = CELL_SIZE - WALL_THICKNESS


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
            # Draw horizontal wall
            if (environment.state.walls_state[i, j] == 0):
                wall_position = (CELL_PADDING + i * CELL_SIZE, CELL_PADDING +
                                 INNER_CELL_SIZE + CELL_SIZE * j)
                screen.blit(horizontal_wall, wall_position)
            elif (environment.state.walls_state[i,
                                                j] == 1):  # Draw vertical wall
                wall_position = (CELL_PADDING + INNER_CELL_SIZE +
                                 CELL_SIZE * i, CELL_PADDING + j * CELL_SIZE)
                screen.blit(vertical_wall, wall_position)


def main():

    # Initialize Quoridor Environment
    environment = QuoridorEnv()
    environment.add_wall((1, 1), 0)

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
                pass
        # draw
        screen.blit(background, (0, 0))
        draw_board(screen, cell)
        draw_state(screen, environment, pawn_0, pawn_1, horizontal_wall,
                   vertical_wall)
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()