import sys
import os

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import torch

from environment import QuoridorEnv, QuoridorState, QuoridorConfig
from alphazero import MCTS, QuoridorRepresentation, QuoridorModel, SelfPlayer, SelfPlayConfig

if __name__ == "__main__":

    # Set device used by torch
    device = torch.device(
        "cuda:0" if torch.cuda.is_available() else "cpu"
    )  #if you have a GPU with CUDA installed, this may speed up computation

    game_config = QuoridorConfig(grid_size=5, max_walls=5)

    state = QuoridorState(game_config)
    environment = QuoridorEnv(game_config)
    representation = QuoridorRepresentation(game_config)

    init_model = QuoridorModel(device, game_config, representation)
    init_model.to(device)

    dir_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../../data/self_play/'))

    selfplay_config = SelfPlayConfig(nb_games=1,
                                     nb_simulations=50,
                                     max_workers=1)

    self_player = SelfPlayer(init_model, game_config, environment,
                             representation, dir_path, selfplay_config)

    self_player.play_games()
