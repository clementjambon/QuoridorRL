import sys
import os

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import torch

from environment import QuoridorEnv, QuoridorState, QuoridorConfig
from alphazero import MCTS, QuoridorRepresentation, QuoridorModel, TrainingConfig, Trainer

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
    init_model = init_model.to(device)

    dir_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../../data/self_play/'))

    training_config = TrainingConfig()

    trainer = Trainer(device, init_model, [
        "/home/clement/Documents/courses/INF581/project/data/self_play/26-02-2022-19-46-21-r9-f256-g1-s50.pkl"
    ], dir_path, training_config)

    trainer.train()

    trainer.save_model()
