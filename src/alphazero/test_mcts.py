import sys
import os

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import torch

from environment import QuoridorEnv, QuoridorState, QuoridorConfig
from alphazero import MCTS, QuoridorRepresentation, QuoridorModel

if __name__ == "__main__":

    # Set device used by torch
    device = torch.device(
        "cuda:0" if torch.cuda.is_available() else "cpu"
    )  #if you have a GPU with CUDA installed, this may speed up computation

    game_config = QuoridorConfig()

    state = QuoridorState(game_config)
    environment = QuoridorEnv(game_config)
    representation = QuoridorRepresentation(game_config)

    init_model = QuoridorModel(device, game_config, representation)
    init_model.to(device)

    mcts = MCTS(game_config, init_model, representation)

    mcts.select_action(environment, state)