import sys
import os
import argparse

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import torch

from environment import QuoridorEnv, QuoridorState, QuoridorConfig
from alphazero import MCTS, QuoridorRepresentation, QuoridorModel, TrainingConfig, Trainer
from alphazero.pipeline import get_parser

if __name__ == "__main__":

    # ----------------------------
    # ARGUMENT PARSER
    # ----------------------------
    parser = get_parser()

    args = parser.parse_args()

    # ----------------------------
    # TRAINING PIPELINE
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
    representation = QuoridorRepresentation(game_config)

    init_model = QuoridorModel(device,
                               game_config,
                               representation,
                               load_dir=args.model_path)
    init_model.to(device)

    dir_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../../data/self_play/'))

    training_config = TrainingConfig(
        batch_size=args.batch_size,
        epochs=args.epochs,
        regularization_param=args.regularization_param,
        learning_rate=args.learning_rate)

    trainer = Trainer(device, init_model, args.selfplay_paths, dir_path,
                      training_config)

    trainer.train()

    trainer.save_model()
