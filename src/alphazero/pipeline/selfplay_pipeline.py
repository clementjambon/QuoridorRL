import sys
import os

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import torch

from environment import QuoridorEnv, QuoridorState, QuoridorConfig
from alphazero import MCTS, QuoridorRepresentation, QuoridorModel, SelfPlayer, SelfPlayConfig
from alphazero.pipeline import get_parser

if __name__ == "__main__":

    # ----------------------------
    # ARGUMENT PARSER
    # ----------------------------
    parser = get_parser()

    args = parser.parse_args()

    # ----------------------------
    # SELF-PLAY PIPELINE
    # ----------------------------

    # Set device used by torch
    device = torch.device(
        "cuda:0" if torch.cuda.is_available() else "cpu"
    )  #if you have a GPU with CUDA installed, this may speed up computation

    game_config = QuoridorConfig(grid_size=args.grid_size,
                                 max_walls=args.max_walls,
                                 max_t=args.max_t)

    state = QuoridorState(game_config)
    environment = QuoridorEnv(game_config)
    representation = QuoridorRepresentation(
        game_config, time_consistency=args.time_consistency)

    init_model = QuoridorModel(device,
                               game_config,
                               representation,
                               load_dir=args.model_path,
                               nb_filters=args.nb_filters,
                               nb_residual_blocks=args.nb_residual_blocks)
    init_model.to(device)

    if args.output_dir is None:
        dir_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__),
                         '../../../data/self_play/'))
    else:
        dir_path = args.output_dir

    selfplay_config = SelfPlayConfig(nb_games=args.nb_games,
                                     nb_simulations=args.nb_simulations,
                                     max_workers=args.max_workers)

    self_player = SelfPlayer(device, init_model, game_config, environment,
                             representation, dir_path, selfplay_config)

    self_player.play_games()
