from argparse import ArgumentParser
from ast import parse
from email.policy import default


def get_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description='Parameters for all pipelines (i.e. self-play and training)'
    )

    parser.add_argument('--verbose',
                        type=bool,
                        default=False,
                        help='print logs in verbose mode')

    # ----------------------------
    # GAME CONFIG
    # ----------------------------
    game_group = parser.add_argument_group('Game config')
    game_group.add_argument('--grid_size',
                            type=int,
                            default=5,
                            help='size of the grid')
    game_group.add_argument('--max_walls',
                            type=int,
                            default=5,
                            help='maximum number of walls a player can use')

    game_group.add_argument('--max_t',
                            type=int,
                            default=50,
                            help='maximum number of time steps in a game')
    # ----------------------------
    # MODEL CONFIG
    # ----------------------------
    model_group = parser.add_argument_group('Model config')
    model_group.add_argument(
        '--time_consistency',
        type=int,
        default=8,
        help=
        'number of previous contiguous states provided as a representation to the model'
    )
    model_group.add_argument(
        '--nb_filters',
        type=int,
        default=64,
        help='number of filters used in convolutions for the model')
    model_group.add_argument(
        '--nb_residual_blocks',
        type=int,
        default=9,
        help='number of residual blocks used in the model')

    # ----------------------------
    # SELF-PLAY CONFIG
    # ----------------------------
    selfplay_group = parser.add_argument_group('Self-play config')
    selfplay_group.add_argument('--nb_games',
                                type=int,
                                default=1000,
                                help='number of games played with self-play')
    selfplay_group.add_argument(
        '--nb_simulations',
        type=int,
        default=100,
        help='number of tree search performed before taking an action')
    selfplay_group.add_argument(
        '--max_workers',
        type=int,
        default=4,
        help='number of parallel workers (DISABLED for now)')
    selfplay_group.add_argument(
        '--initial_temperature',
        type=float,
        default=1.0,
        help=
        "temperature applied for the search policy at the beginning of each self-play game (see tempered_state for the number of --tempered_states)"
    )
    selfplay_group.add_argument(
        '--tempered_steps',
        type=int,
        default=20,
        help="number of turns during which temperature is applied")
    selfplay_group.add_argument(
        '--limited_time',
        type=float,
        default=None,
        help=
        "limited time in seconds during which a full MCTS can be performed (by default None)"
    )
    selfplay_group.add_argument(
        '--intermediate_reward',
        type=bool,
        default=False,
        help="whether to use handcrafted intermediate rewards or not")
    selfplay_group.add_argument(
        '--model_path',
        type=str,
        default=None,
        help='path of the model used to generate self-plays')
    selfplay_group.add_argument(
        '--output_dir',
        type=str,
        default=None,
        help='path where self-play records will be written')
    selfplay_group.add_argument(
        '--str_history',
        type=bool,
        default=False,
        help='specifies whether to store string selfplay records or not')
    selfplay_group.add_argument(
        '--display_mode',
        type=bool,
        default=False,
        help=
        'specifies whether to display the current state of the game or nots')

    # ----------------------------
    # TRAINING CONFIG
    # ----------------------------
    training_group = parser.add_argument_group('Training Config')
    training_group.add_argument(
        '--selfplay_paths',
        nargs='+',
        default=[],
        help='path of the self-play records used for training')
    training_group.add_argument(
        '--batch_size',
        type=int,
        default=32,
        help='size of the batches used during training')
    training_group.add_argument('--epochs',
                                type=int,
                                default=100,
                                help='number of epochs used during training')
    training_group.add_argument(
        '--regularization_param',
        type=float,
        default=1e-4,
        help='L2 regularization parameter used during training')

    training_group.add_argument('--learning_rate',
                                type=float,
                                default=1e-3,
                                help='learning rate used during training')

    # ----------------------------
    # MANAGER CONFIG
    # ----------------------------
    manager_group = parser.add_argument_group('Manager Config')
    manager_group.add_argument('--nb_iterations',
                               type=int,
                               default=5,
                               help='number of selfplay/training iterations')
    manager_group.add_argument(
        '--selfplay_history',
        type=int,
        default=2,
        help='number of most recent selfplay records used for training')

    return parser