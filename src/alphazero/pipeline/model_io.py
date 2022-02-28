from json import load
import sys
import os
import torch
import pygame as pg

if not pg.font:
    print("Warning, fonts disabled")

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from environment import QuoridorEnv, QuoridorState, QuoridorConfig
from interactive import CELL_SIZE, INNER_CELL_SIZE, EMPTY_CELL_COLOR, PAWN_0_COLOR, PAWN_1_COLOR, SIZE, WALL_THICKNESS, FPS, WALL_COLOR
from interactive import draw_gui, draw_board, draw_state
from alphazero import QuoridorModel, QuoridorRepresentation, MCTS
from alphazero.pipeline import get_parser


def play_model(mcts: MCTS, feature_planes, environment: QuoridorEnv,
               state: QuoridorState, representation: QuoridorRepresentation,
               limited_time: float):
    if state.done:
        return
    action_idx, _ = mcts.select_action(environment,
                                       state,
                                       feature_planes,
                                       limited_time=limited_time,
                                       temperature=0.0)
    state = environment.step_from_index(state, action_idx)

    # Add the new feature planes to existing feature planes
    current_feature_planes = representation.generate_instant_planes(state)
    feature_planes.append(current_feature_planes)


def handle_click(environment: QuoridorEnv, state: QuoridorState,
                 action_mode: int, mcts: MCTS, feature_planes,
                 representation: QuoridorRepresentation,
                 limited_time: float) -> None:
    # Prevents player from taking actions if the game is over or it is not its turn
    if state.done or state.current_player != 0:
        return None

    mouse_pos = pg.mouse.get_pos()
    if action_mode == 0:
        target_position = (mouse_pos[0] // CELL_SIZE,
                           mouse_pos[1] // CELL_SIZE)
        if environment.can_move_pawn(state, target_position):
            state = environment.move_pawn(state, target_position)

            # Add the new feature planes to existing feature planes
            current_feature_planes = representation.generate_instant_planes(
                state)
            feature_planes.append(current_feature_planes)

            play_model(mcts, feature_planes, environment, state,
                       representation, limited_time)
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
            state = environment.add_wall(state, target_position, direction)

            # Add the new feature planes to existing feature planes
            current_feature_planes = representation.generate_instant_planes(
                state)
            feature_planes.append(current_feature_planes)

            play_model(mcts, feature_planes, environment, state,
                       representation, limited_time)
        else:
            print(
                f"QuoridorEnv: cannot place wall for player {state.current_player} to target position {target_position} and direction {direction}"
            )
            return

    # DEBUG
    # print the set of actions that the new player can take
    possible_actions = environment.get_possible_actions(state)
    possible_actions_str = [action.to_string() for action in possible_actions]

    print(
        f"Debug: possible actions for player {state.current_player} are {possible_actions_str}"
    )


def main():

    # ----------------------------
    # ARGUMENT PARSER
    # ----------------------------
    parser = get_parser()

    args = parser.parse_args()

    # ----------------------------
    # IO PIPELINE
    # ----------------------------

    # Set device used by torch
    device = torch.device(
        "cuda:0" if torch.cuda.is_available() else "cpu"
    )  #if you have a GPU with CUDA installed, this may speed up computation

    # Initialize Quoridor Config
    game_config = QuoridorConfig(grid_size=args.grid_size,
                                 max_walls=args.max_walls,
                                 max_t=args.max_t)

    # Initialize Quoridor Environment
    environment = QuoridorEnv(game_config)

    # Initialize Quoridor State Representation
    representation = QuoridorRepresentation(
        game_config, time_consistency=args.time_consistency)

    # Initialize Quoridor State
    state = QuoridorState(game_config)

    # Load the model against which we want to play
    if args.output_dir is None:
        model_path = os.path.join(os.path.dirname(__file__),
                                  '../../../data/self_play/default-model.pt')
    else:
        model_path = args.model_path

    model = QuoridorModel(device,
                          game_config,
                          representation,
                          load_dir=model_path,
                          nb_filters=args.nb_filters,
                          nb_residual_blocks=args.nb_residual_blocks)
    model = model.to(device)

    # Initialize the feature planes that are generated from each visited state
    feature_planes = []

    # Initialize the MCTS (and the limited search time)
    limited_search_time = 2.0
    mcts = MCTS(game_config, model, representation)

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
                handle_click(environment, state, action_mode, mcts,
                             feature_planes, representation,
                             limited_search_time)
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                action_mode = (action_mode + 1) % 3
        # draw
        screen.blit(background, (0, 0))
        draw_board(screen, game_config, cell)
        draw_state(screen, game_config, state, pawn_0, pawn_1, horizontal_wall,
                   vertical_wall)

        draw_gui(screen, game_config, state, action_mode, state.done)
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()