import sys
import os

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import torch

from environment import QuoridorEnv, QuoridorState, QuoridorConfig
from alphazero import MCTS, QuoridorRepresentation, QuoridorModel, SelfPlayer, SelfPlayConfig, TrainingConfig, Manager

if __name__ == "__main__":

    # Set device used by torch
    device = torch.device(
        "cuda:0" if torch.cuda.is_available() else "cpu"
    )  #if you have a GPU with CUDA installed, this may speed up computation

    game_config = QuoridorConfig(grid_size=5, max_walls=5, max_t=100)

    state = QuoridorState(game_config)
    environment = QuoridorEnv(game_config)
    representation = QuoridorRepresentation(game_config)

    init_model = QuoridorModel(device, game_config, representation)
    init_model.to(device)

    dir_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../data/self_play/'))

    selfplay_config = SelfPlayConfig(nb_games=1000,
                                     nb_simulations=100,
                                     max_workers=1,
                                     max_t=100)

    training_config = TrainingConfig()

    manager = Manager(device,
                      nb_iterations=20,
                      selfplay_history=4,
                      game_config=game_config,
                      environment=environment,
                      representation=representation,
                      save_dir=dir_path,
                      selfplay_config=selfplay_config,
                      training_config=training_config)

    manager.iterate()
