import sys
import os

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import torch

from environment import QuoridorEnv, QuoridorState, QuoridorConfig
from alphazero import QuoridorRepresentation, QuoridorModel, TrainingConfig, SelfPlayConfig, Manager
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
    representation = QuoridorRepresentation(
        game_config, time_consistency=args.time_consistency)

    init_model = QuoridorModel(device,
                               game_config,
                               representation,
                               load_dir=args.model_path,
                               nb_filters=args.nb_filters,
                               nb_residual_blocks=args.nb_residual_blocks)
    init_model = init_model.to(device)

    if args.output_dir is None:
        dir_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__),
                         '../../../data/self_play/'))
    else:
        dir_path = args.output_dir

    training_config = TrainingConfig(
        batch_size=args.batch_size,
        epochs=args.epochs,
        regularization_param=args.regularization_param,
        learning_rate=args.learning_rate)

    selfplay_config = SelfPlayConfig(
        nb_games=args.nb_games,
        nb_simulations=args.nb_simulations,
        max_workers=args.max_workers,
        initial_temperature=args.initial_temperature,
        tempered_steps=args.tempered_steps,
        limited_time=args.limited_time,
        str_history=args.str_history,
        verbose=args.verbose,
        display_mode=args.display_mode,
        intermediate_reward=args.intermediate_reward,
    )

    manager = Manager(device,
                      nb_iterations=args.nb_iterations,
                      selfplay_history=args.selfplay_history,
                      game_config=game_config,
                      environment=environment,
                      representation=representation,
                      save_dir=dir_path,
                      selfplay_config=selfplay_config,
                      training_config=training_config)

    manager.iterate()
