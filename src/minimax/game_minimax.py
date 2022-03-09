from argparse import Action
import copy
import sys
import os
import pygame as pg
import time

if not pg.font:
    print("Warning, fonts disabled")

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from environment import QuoridorEnv, QuoridorState, QuoridorConfig
from interactive import CELL_SIZE, INNER_CELL_SIZE, EMPTY_CELL_COLOR, PAWN_0_COLOR, PAWN_1_COLOR, SIZE, WALL_THICKNESS, FPS, WALL_COLOR
from interactive import draw_gui, draw_board, draw_state, init_surfaces
from environment.quoridor_action import MoveAction
from utils import coords_to_tile, tile_to_coords
from minimax import minimax, BoardGraph


def main():

    # Initialize Quoridor Config
    game_config = QuoridorConfig(grid_size=5, max_walls=5)

    # Initialize Quoridor Environment
    environment = QuoridorEnv(game_config)

    # Initialize Quoridor State
    state = QuoridorState(game_config)

    # Initialize action mode
    action_mode = 0

    # Min time between steps (in seconds)
    min_time = 1.0

    pg.init()
    screen = pg.display.set_mode(SIZE, pg.SCALED)
    pg.display.set_caption("QuoridorRL")

    background, cell, pawn_0, pawn_1, horizontal_wall, vertical_wall = init_surfaces(
        screen)

    # Display the background
    screen.blit(background, (0, 0))
    pg.display.flip()

    clock = pg.time.Clock()
    last_time = time.time() - min_time

    rendering = True
    while rendering:
        clock.tick(FPS)

        # handle input events
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.K_ESCAPE:
                rendering = False
        # draw
        screen.blit(background, (0, 0))
        draw_board(screen, game_config, cell)
        draw_state(screen, game_config, state, pawn_0, pawn_1, horizontal_wall,
                   vertical_wall)
        #draw_debug_offsets(screen, game_config, (5, 5), 11)
        draw_gui(screen, game_config, state, action_mode, state.done)
        pg.display.flip()

        if state.t < game_config.max_t and not state.done:
            # The following is used to make sure the refresh rate of actions is not too high
            time_diff = time.time() - last_time
            if time_diff < min_time:
                time.sleep(min_time - time_diff)
            last_time = time.time()

            #print("Round " + str(state.t))
            state.t += 1
            print(state.to_string(False, True, True))
            # act
            action = best_action(environment, state)
            #apply it to state
            environment.actNoCopy(state, action)
            #print("Position of PLAYER 0: " + str(state.player_positions[0]))
            #print("Position of PLAYER 1: " + str(state.player_positions[1]))

    pg.quit()
    print('GAME OVER')


def best_action(env: QuoridorEnv, state: QuoridorState) -> Action:
    #list of possible actions for current player
    cur_actions = env.get_possible_actions(state)
    move_actions = [
        action for action in cur_actions if isinstance(action, MoveAction)
    ]
    #TODO : istead of move_actions check if all() are instance of MoveAction
    #if no more walls available to put on board
    #search for shortest path to target
    if len(move_actions) == len(cur_actions):
        targets = env.get_targets_tiles(state.current_player)
        best_move = shortest_path(state, targets)
        print(
            f'no more walls for player {state.current_player} : move to {best_move.player_pos}'
        )
    else:
        best_score = float('-inf')
        best_move = None
        for action in cur_actions:
            #apply action to get possible board
            #do a copy of the state to apply action on it without altering real current state of the board
            #copy_position_player = state.player_positions[state.current_player]
            copy_state = copy.deepcopy(state)
            copy_env = copy.deepcopy(env)
            #print(action)

            copy_env.actNoCopy(copy_state, action)

            score = minimax(copy_env, copy_state, 0, False)
            #print(score)
            if score > best_score:
                #print(best_score)
                best_score = score
                best_move = action
        print(
            f'action chosen for player {state.current_player} is {best_move.type} and score is {best_score}'
        )
    return best_move


def shortest_path(state: QuoridorState, targets) -> MoveAction:
    """
    Use Dijkstra algorithm to find best move to reach target
    """
    board = BoardGraph(state.walls)
    parents_map, node_costs = board.dijkstra(
        coords_to_tile(state.player_positions[state.current_player],
                       state.grid_size))
    closest_target = None
    cost = float('inf')
    for target in targets:
        if node_costs[target] < cost:
            cost = node_costs[target]
            closest_target = target
    path = board.make_path(parents_map, closest_target)
    #convert vertex nb to coords
    path_coords = tile_to_coords(
        path[1], state.grid_size)  #path[0] is the current position
    best_move = MoveAction(path_coords, state.current_player)
    return best_move


if __name__ == "__main__":
    main()