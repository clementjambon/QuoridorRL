import sys
import os
import pygame as pg

if not pg.font:
    print("Warning, fonts disabled")

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from environment import INDIRECT_OFFSETS
from environment.quoridor_env import QuoridorEnv, QuoridorEnvAgents
from interactive import CELL_SIZE, TEXT_COLOR, GRID_SIZE, ACTION_DESCRIPTIONS, CELL_PADDING, INNER_CELL_SIZE, EMPTY_CELL_COLOR, PAWN_0_COLOR, PAWN_1_COLOR, SIZE, WALL_THICKNESS, FPS, WALL_COLOR, MAX_WALLS
from interactive import draw_gui, draw_board, draw_state


#agent chooses next move at each mouse click
def agent_plays_onclick(environment: QuoridorEnvAgents) -> None:
    # Prevents players from taking actions if the game is over
    if environment.done:
        return None

    #choose a random action
    environment.play()


def main():

    # Initialize Quoridor Environment
    environment = QuoridorEnvAgents(grid_size=GRID_SIZE, max_walls=MAX_WALLS)

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
                agent_plays_onclick(environment)

        # draw
        screen.blit(background, (0, 0))
        draw_board(screen, cell)
        draw_state(screen, environment, pawn_0, pawn_1, horizontal_wall,
                   vertical_wall)
        #draw_debug_offsets(screen, (5, 5), 11)
        draw_gui(screen, environment, action_mode, environment.done)
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()