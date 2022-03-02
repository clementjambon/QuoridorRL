# QuoridorRL: solving a two-player strategy game with reinforcement learning
*an INF581 project*

This repository provides an environment for the two-player zero-sum Quoridor game and several implementations of agents targeting human-level control (namely [Heuristic agent](#heuristic-agent), [MC-RAVE agent](#mc-rave-agent) and [AlphaZero agent](#alphazero-agent)).

## Table of contents
* [Getting started](#getting-started)
* [Environment](#environment)
* [Interactive version](#interactive-version)
* [Heuristic agent](#heuristic-agent)
* [MC-RAVE agent](#mc-rave-agent)
* [AlphaZero agent](#alphazero-agent)
    * [Self-play](#self-play)
    * [Training](#training)
    * [Manager](#manager)
    * [GUI](#gui)

## Getting started
In order to set up the project, please use a virtual environment that can be created and activated with
```bash
python3 -m venv .venv
source ./.venv/bin/activate
```
Then, install the required libraries with
```bash
pip3 install -r requirements.txt
```

**Note:** the project uses `yapf` in order to format python code. Automatic formatting and lynting is already configured for `VSCode` (including "format on save").

## Environment

The game environement is provided as a class `QuoridorEnv` located in `src/environment/quoridor_env.py` which leverages the rule-embedding class `QuoridorState` located in `src/environment/quoridor_state.py`. 

The state of the game in intrinsically described by the location in the grid of the two (*0* and *1* indexed) players, the number of walls they have each already placed and a 2D grid of wall positions. In this latter grid, `-1` stands for empty, `0` for an horizontal wall (x-aligned) and `1` for a vertical wall (y-aligned).

## Interactive version
In order to visualize and try the game, an interactive version based on `pygame` is provided and can be run with
```bash
cd src/interactive
python3 game_io.py
```

The parameters of the interactive version can be tuned with the constants provided in `src/interactive/io_constants.py`.

States stored as strings in a file can be visualized thanks to
```bash
cd src/interactive
python3 display_states.py [STATE_STRINGS_PATH]
```
To transition from one state to another, press `space`

## Heuristic agent
Two AI agents can play against each other making choices based on a Minimax search. Go on the heuristic branch to try it. The mouse has to be clicked on the window to tell the agent to make a move.  
/!\ not yet working so not yet merged on the main branch: Heuristic Branch
```bash
cd src/interactive
python3 game_agents.py
```

## MC-RAVE agent
The *MC-RAVE* agent can be experimented by generating a self-play game based on MC-RAVE algorithm, by running
```bash
cd src/mc-rave
python3 main.py
```

## AlphaZero agent
The *AlphaZero* agent can be trained by generating successively self-play games with previous models and training the new model by sampling experiences from those self-play games. To this extent, we provide two dedicated pipelines (namely the **self-play pipeline** and the **training pipeline**) which can be executed independently or successively using the overall **manager pipeline**

### Self-play
Self-play games can be generated using a pre-existing model by running
```bash 
cd src/alphazero/pipeline
python3 selfplay_pipeline.py

optional arguments:
  -h, --help            show help message and exit

Game config:
  --grid_size GRID_SIZE
                        size of the grid
  --max_walls MAX_WALLS
                        maximum number of walls a player can use
  --max_t MAX_T         maximum number of time steps in a game

Model config:
  --time_consistency TIME_CONSISTENCY
                        number of previous contiguous states provided as a
                        representation to the model
  --nb_filters NB_FILTERS
                        number of filters used in convolutions for the model
  --nb_residual_blocks NB_RESIDUAL_BLOCKS
                        number of residual blocks used in the model

Self-play config:
  --nb_games NB_GAMES   number of games played with self-play
  --nb_simulations NB_SIMULATIONS
                        number of tree search performed before taking an
                        action
  --initial_temperature INITIAL_TEMPERATURE
                        temperature applied for the search policy at the
                        beginning of each self-play game (see tempered_state
                        for the number of --tempered_states)
  --tempered_steps TEMPERED_STEPS
                        number of turns during which temperature is applied
  --limited_time LIMITED_TIME
                        limited time in seconds during which a full MCTS can
                        be performed (by default None)
  --max_workers MAX_WORKERS
                        number of parallel workers (DISABLED for now)
  --model_path MODEL_PATH
                        path of the model used to generate self-plays
  --output_dir OUTPUT_DIR
                        path where self-play records will be written
```


### Training
A network can be loaded and trained from a set of self-play games thanks to
```bash
cd src/alphazero/pipeline
python3 training_pipeline.py

optional arguments:
  -h, --help            show help message and exit

Game config:
  --grid_size GRID_SIZE
                        size of the grid
  --max_walls MAX_WALLS
                        maximum number of walls a player can use
  --max_t MAX_T         maximum number of time steps in a game

Model config:
  --time_consistency TIME_CONSISTENCY
                        number of previous contiguous states provided as a
                        representation to the model
  --nb_filters NB_FILTERS
                        number of filters used in convolutions for the model
  --nb_residual_blocks NB_RESIDUAL_BLOCKS
                        number of residual blocks used in the model

Training Config:
  --model_path MODEL_PATH
                        path of the model to train
  --selfplay_paths SELFPLAY_PATHS [SELFPLAY_PATHS ...]
                        path of the self-play records used for training
  --batch_size BATCH_SIZE
                        size of the batches used during training
  --epochs EPOCHS       number of epochs used during training
  --regularization_param REGULARIZATION_PARAM
                        L2 regularization parameter used during training
  --learning_rate LEARNING_RATE
                        learning rate used during training
  --output_dir OUTPUT_DIR
                        path where self-play records will be written
```

### Manager
The whole pipeline can be run using the **manager pipeline**
```bash
cd src/alphazero/pipeline
python3 manager_pipeline.py

optional arguments:
  -h, --help            show help message and exit

Game config:
  --grid_size GRID_SIZE
                        size of the grid
  --max_walls MAX_WALLS
                        maximum number of walls a player can use
  --max_t MAX_T         maximum number of time steps in a game

Model config:
  --time_consistency TIME_CONSISTENCY
                        number of previous contiguous states provided as a
                        representation to the model
  --nb_filters NB_FILTERS
                        number of filters used in convolutions for the model
  --nb_residual_blocks NB_RESIDUAL_BLOCKS
                        number of residual blocks used in the model

Self-play config:
  --nb_games NB_GAMES   number of games played with self-play
  --nb_simulations NB_SIMULATIONS
                        number of tree search performed before taking an
                        action
  --initial_temperature INITIAL_TEMPERATURE
                        temperature applied for the search policy at the
                        beginning of each self-play game (see tempered_state
                        for the number of --tempered_states)
  --tempered_steps TEMPERED_STEPS
                        number of turns during which temperature is applied
  --limited_time LIMITED_TIME
                        limited time in seconds during which a full MCTS can
                        be performed (by default None)
  --max_workers MAX_WORKERS
                        number of parallel workers (DISABLED for now)
  --model_path MODEL_PATH
                        path of the model used to generate self-plays
  --output_dir OUTPUT_DIR
                        path where self-play records will be written

Training Config:
  --selfplay_paths SELFPLAY_PATHS [SELFPLAY_PATHS ...]
                        path of the self-play records used for training
  --batch_size BATCH_SIZE
                        size of the batches used during training
  --epochs EPOCHS       number of epochs used during training
  --regularization_param REGULARIZATION_PARAM
                        L2 regularization parameter used during training
  --learning_rate LEARNING_RATE
                        learning rate used during training

Manager Config:
  --nb_iterations NB_ITERATIONS
                        number of selfplay/training iterations
  --selfplay_history SELFPLAY_HISTORY
                        number of most recent selfplay records used for
                        training
```

### GUI
Trained models can be played against using the above-mentioned GUI with
```bash
cd src/alphazero/pipeline
python3 model_io.py [--model_path MODEL_PATH]
```
