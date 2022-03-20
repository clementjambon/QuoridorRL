import sys
import os
import pygame as pg
from argparse import ArgumentParser

if not pg.font:
    print("Warning, fonts disabled")

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from environment import QuoridorEnv, QuoridorState, QuoridorConfig
from interactive import INNER_CELL_SIZE, EMPTY_CELL_COLOR, PAWN_0_COLOR, PAWN_1_COLOR, SIZE, WALL_THICKNESS, FPS, WALL_COLOR
from interactive import draw_gui, draw_board, draw_state, init_surfaces, draw_debug_adjacent
from utils import read_history


def init_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Parameters for state visualization')
    parser.add_argument('--history_path',
                        type=str,
                        default=None,
                        help='path of the history to visualize')
    parser.add_argument('--state_str',
                        type=str,
                        default=None,
                        help='string of the state to visualize')
    return parser


def update_state(environment: QuoridorEnv, state: QuoridorState, history,
                 history_idx) -> None:
    # Prevents players from taking actions if the game is over
    if history_idx < len(history):
        state.load_from_string(history[history_idx])
        print("Updating state............................")
        print(state.to_string(add_nb_walls=True, add_current_player=True))
        print(state.walls)
        print([
            action.to_string()
            for action in environment.get_possible_actions(state)
        ])


def main():

    # Initialize parser
    parser = init_parser()
    args = parser.parse_args()

    # Initialize Quoridor Config
    game_config = QuoridorConfig(grid_size=5, max_walls=5, max_t=100)

    # Initialize environment
    environment = QuoridorEnv(game_config)

    # Initialize Quoridor State with the provided history
    state = QuoridorState(game_config)

    history_idx = 0
    if args.history_path is not None:
        history = read_history(args.history_path)
        update_state(environment, state, history, history_idx)
    elif args.state_str is not None:
        history = [args.state_str]
        update_state(environment, state, history, history_idx)
    else:
        history = []

    pg.init()
    screen = pg.display.set_mode(SIZE, pg.SCALED)
    pg.display.set_caption("QuoridorRL - State Visualization")

    background, cell, pawn_0, pawn_1, horizontal_wall, vertical_wall = init_surfaces(
        screen)

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
        #draw_debug_adjacent(screen, (2, 2), 1, horizontal_wall, vertical_wall)
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()