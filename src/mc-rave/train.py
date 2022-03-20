import sys
import os
import pygame as pg

if not pg.font:
    print("Warning, fonts disabled")

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from environment import QuoridorEnv, QuoridorState, QuoridorConfig
from interactive import CELL_SIZE, INNER_CELL_SIZE, EMPTY_CELL_COLOR, PAWN_0_COLOR, PAWN_1_COLOR, SIZE, WALL_THICKNESS, FPS, WALL_COLOR
from interactive import draw_gui, draw_board, draw_state
from tree import MCTSNode


def main():

    # Initialize Quoridor Config
    game_config = QuoridorConfig(grid_size=5, max_walls=5)

    # Initialize Quoridor Environment
    environment = QuoridorEnv(game_config)

    # Initialize Quoridor State
    state = QuoridorState(game_config)

    rendering = True
    print('rendering')
    i = 0
    root = MCTSNode(environment, state, state.current_player)
    while i < 100 and not state.done:
        print("Round " + str(i))
        i += 1
        print(state.to_string(False, True, True))
        # act
        # print('acting')
        # root = MCTSNode(environment, state, state.current_player)
        action = root.best_action()
        for child in root.children:
            if child.parent_action == action:
                root = child
                break
        # print('acting... type ' + str(action.type))
        environment.actNoCopy(state, action)
        print("Position of PLAYER 0: " + str(state.player_positions[0]))
        print("Position of PLAYER 1: " + str(state.player_positions[1]))
    print('GAME OVER')


if __name__ == "__main__":
    main()