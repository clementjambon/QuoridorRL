from email.policy import default
import sys
import os
import argparse

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import torch

from environment import QuoridorEnv, QuoridorState, QuoridorConfig
from alphazero import MCTS, QuoridorRepresentation, QuoridorModel, SelfPlayer, SelfPlayConfig

if __name__ == "__main__":

    # ----------------------------
    # ARGUMENT PARSER
    # ----------------------------
    parser = argparse.ArgumentParser(
        description='Collect game data from self-play.')
    parser.add_argument('--nb_games',
                        type=int,
                        default=1000,
                        help='the number of games played with self-play')
    parser.add_argument(
        '--nb_simulations',
        type=int,
        default=100,
        help='the number of tree search performed before taking an action')
    parser.add_argument('--max_workers',
                        type=int,
                        default=4,
                        help='the number of parallel workers')
    parser.add_argument(
        '--model_path',
        type=str,
        default=None,
        help='the path of the model used to generate self-plays')

    args = parser.parse_args()

    # ----------------------------
    # SELF-PLAY PIPELINE
    # ----------------------------

    # Set device used by torch
    device = torch.device(
        "cuda:0" if torch.cuda.is_available() else "cpu"
    )  #if you have a GPU with CUDA installed, this may speed up computation

    game_config = QuoridorConfig(grid_size=5, max_walls=5, max_t=100)

    state = QuoridorState(game_config)
    environment = QuoridorEnv(game_config)
    representation = QuoridorRepresentation(game_config)

    init_model = QuoridorModel(device,
                               game_config,
                               representation,
                               load_dir=args.model_path)
    init_model.to(device)

    dir_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../../data/self_play/'))

    selfplay_config = SelfPlayConfig(nb_games=args.nb_games,
                                     nb_simulations=args.nb_simulations,
                                     max_workers=args.max_workers)

    self_player = SelfPlayer(init_model, game_config, environment,
                             representation, dir_path, selfplay_config)

    self_player.play_games()
