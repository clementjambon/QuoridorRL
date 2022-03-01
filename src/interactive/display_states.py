import sys
import os
import pygame as pg

if not pg.font:
    print("Warning, fonts disabled")

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from environment import QuoridorEnv, QuoridorState, QuoridorConfig
from interactive import INNER_CELL_SIZE, EMPTY_CELL_COLOR, PAWN_0_COLOR, PAWN_1_COLOR, SIZE, WALL_THICKNESS, FPS, WALL_COLOR
from interactive import draw_gui, draw_board, draw_state
from utils import read_history


def update_state(environment: QuoridorEnv, state: QuoridorState, history,
                 history_idx) -> None:
    # Prevents players from taking actions if the game is over
    if history_idx < len(history):
        state.load_from_string(history[history_idx])
        print(state.to_string(add_nb_walls=True, add_current_player=True))
        print(state.walls)
        print([
            action.to_string()
            for action in environment.get_possible_actions(state)
        ])


def main():

    # Initialize Quoridor Config
    game_config = QuoridorConfig(grid_size=5, max_walls=5, max_t=100)

    # Initialize environment
    environment = QuoridorEnv(game_config)

    # Initialize Quoridor State with the provided history
    state = QuoridorState(game_config)

    history_idx = 0
    if len(sys.argv) > 1:
        history = read_history(sys.argv[1])
        update_state(environment, state, history, history_idx)
    else:
        history = []

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
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                update_state(environment, state, history, history_idx)
                history_idx += 1
        # draw
        screen.blit(background, (0, 0))
        draw_board(screen, game_config, cell)
        draw_state(screen, game_config, state, pawn_0, pawn_1, horizontal_wall,
                   vertical_wall)
        #draw_debug_offsets(screen, game_config, (5, 5), 11)
        draw_gui(screen, game_config, state, 0, state.done)
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()