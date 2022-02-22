import sys
import os
import pygame as pg

if not pg.font:
    print("Warning, fonts disabled")

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from environment import QuoridorEnv, INDIRECT_OFFSETS
from interactive import CELL_SIZE, TEXT_COLOR, GRID_SIZE, ACTION_DESCRIPTIONS, CELL_PADDING, INNER_CELL_SIZE, EMPTY_CELL_COLOR, PAWN_0_COLOR, PAWN_1_COLOR, SIZE, WALL_THICKNESS, FPS, WALL_COLOR, MAX_WALLS
from interactive import draw_gui, draw_board, draw_state
from tree import MCTSNode


def main():

    # Initialize Quoridor Environment
    environment = QuoridorEnv(grid_size=GRID_SIZE, max_walls=MAX_WALLS)

    rendering = True
    print('rendering')
    i = 0
    while not environment.done:
        print(i)
        i += 1
        # act
        print('acting')
        root = MCTSNode(environment.state, environment.current_player)
        action = root.best_action()
        print('acting...')
        environment.act(action)
    print('GAME OVER')


if __name__ == "__main__":
    main()