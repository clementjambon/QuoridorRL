from argparse import ArgumentParser
from ast import parse
from email.policy import default


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Collect game data from self-play.')

    # ----------------------------
    # GAME_CONFIG
    # ----------------------------
    parser.add_argument('--grid_size',
                        type=int,
                        default=5,
                        help='the size of the grid')
    parser.add_argument('--max_walls',
                        type=int,
                        default=5,
                        help='the maximum number of walls a player can use')

    parser.add_argument('--max_t',
                        type=int,
                        default=100,
                        help='the maximum number of time steps in a game')
    # ----------------------------
    # SELF-PLAY CONFIG
    # ----------------------------

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

    # ----------------------------
    # TRAINING CONFIG
    # ----------------------------
    parser.add_argument('--selfplay_paths', nargs='+', default=[])
    parser.add_argument('--batch_size',
                        type=int,
                        default=32,
                        help='the size of the batches used during training')
    parser.add_argument('--epochs',
                        type=int,
                        default=100,
                        help='the number of epochs used during training')
    parser.add_argument(
        '--regularization_param',
        type=float,
        default=1e-4,
        help='the L2 regularization parameter used during training')

    parser.add_argument('--learning_rate',
                        type=float,
                        default=1e-4,
                        help='the learning rate used during training')

    return parser