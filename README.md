# QuoridorRL
*an INF581 project by Nathan Pollet, Rebecca Jaubert, Laura Minkova, Erwan Umlil and Clément Jambon*

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


