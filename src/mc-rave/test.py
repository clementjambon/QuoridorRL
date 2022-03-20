import sys
import os
import pygame as pg

if not pg.font:
    print("Warning, fonts disabled")

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from environment import QuoridorEnv, QuoridorState, QuoridorConfig, MoveAction, WallAction
from interactive import CELL_SIZE, INNER_CELL_SIZE, EMPTY_CELL_COLOR, PAWN_0_COLOR, PAWN_1_COLOR, SIZE, WALL_THICKNESS, FPS, WALL_COLOR
from interactive import draw_gui, draw_board, draw_state, init_surfaces
from tree import MCTSNode


def handle_click(environment: QuoridorEnv, state: QuoridorState,
                 action_mode: int) -> None:
    # Prevents players from taking actions if the game is over
    if state.done:
        return None

    # if state.current_player == 1:
    #     # root = MCTSNode(environment, state, state.current_player)
    #     action = root.best_action()
    #     for child in root.children:
    #         if child.parent_action == action:
    #             root = child
    #             break
    #     # print('acting.
    #     # print('acting... type ' + str(action.type))
    #     environment.actNoCopy(state, action)
    #     print("Position of PLAYER 0: " + str(state.player_positions[0]))
    #     print("Position of PLAYER 1: " + str(state.player_positions[1]))
    #     return

    mouse_pos = pg.mouse.get_pos()
    action_taken = None
    if action_mode == 0:
        target_position = (mouse_pos[0] // CELL_SIZE,
                           mouse_pos[1] // CELL_SIZE)
        if environment.can_move_pawn(state, target_position):
            action_taken = MoveAction(target_position, state.current_player)
            state = environment.move_pawn(state, target_position)
        else:
            print(
                f"QuoridorEnv: cannot move player {state.current_player} to target position {target_position}"
            )
            return
    else:
        target_position = (int((mouse_pos[0] - CELL_SIZE / 2) // CELL_SIZE),
                           int((mouse_pos[1] - CELL_SIZE / 2) // CELL_SIZE))
        direction = 0 if action_mode == 1 else 1
        if environment.can_add_wall(state, target_position, direction):
            print(type(state))
            state = environment.add_wall(state, target_position, direction)
            action_taken = WallAction(target_position, direction)
        else:
            print(
                f"QuoridorEnv: cannot place wall for player {state.current_player} to target position {target_position} and direction {direction}"
            )
            return
    return action_taken

    # DEBUG
    # print the set of actions that the new player can take
    possible_actions = environment.get_possible_actions(state)
    possible_actions_str = [action.to_string() for action in possible_actions]

    print(
        f"Debug: possible actions for player {state.current_player} are {possible_actions_str}"
    )


def main():

    # Initialize Quoridor Config
    game_config = QuoridorConfig(grid_size=5, max_walls=5)

    # Initialize Quoridor Environment
    environment = QuoridorEnv(game_config)

    # Initialize Quoridor State
    state = QuoridorState(game_config)

    # Initialize action mode
    action_mode = 0

    pg.init()
    screen = pg.display.set_mode(SIZE, pg.SCALED)
    pg.display.set_caption("QuoridorRL")

    background, cell, pawn_0, pawn_1, horizontal_wall, vertical_wall = init_surfaces(
        screen)

    # Display the background
    screen.blit(background, (0, 0))
    pg.display.flip()

    clock = pg.time.Clock()

    rendering = True
    root = None
    while rendering:
        clock.tick(FPS)

        # handle input events
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.K_ESCAPE:
                rendering = False
            # TODO: handle key down
            elif event.type == pg.MOUSEBUTTONDOWN:
                if state.current_player == 1:
                    if not root:
                        root = MCTSNode(environment, state,
                                        state.current_player)
                    print('max depth: ' + str(root.max_depth()))
                    action = root.best_action()
                    exists = False
                    for child in root.children:
                        if child.parent_action == action:
                            root = child
                            exists = True
                            break
                    # print("exists: " + str(exists))
                    # print("new root depth: " + str(root.depth))
                    # print(action.player_pos)
                    environment.actNoCopy(state, action)
                    if not exists:
                        root = MCTSNode(environment, state,
                                        state.current_player)
                    print("Position of PLAYER 0: " +
                          str(state.player_positions[0]))
                    print("Position of PLAYER 1: " +
                          str(state.player_positions[1]))
                else:
                    action = handle_click(environment, state, action_mode)
                    if not action:
                        continue
                    if not root:
                        root = MCTSNode(environment, state,
                                        state.current_player)
                    exists = False
                    for child in root.children:
                        if child.parent_action == action:
                            root = child
                            exists = True
                            break
                    if not exists:
                        root = MCTSNode(environment, state,
                                        state.current_player)
                    # print("exists: " + str(exists))
                    # print("new root depth: " + str(root.depth))
                    # print(action.player_pos)
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                action_mode = (action_mode + 1) % 3
        # draw
        screen.blit(background, (0, 0))
        draw_board(screen, game_config, cell)
        draw_state(screen, game_config, state, pawn_0, pawn_1, horizontal_wall,
                   vertical_wall)
        #draw_debug_offsets(screen, game_config, (5, 5), 11)
        draw_gui(screen, game_config, state, action_mode, state.done)
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()