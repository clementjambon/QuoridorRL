import os
import pickle
from concurrent.futures import ThreadPoolExecutor, wait
import numpy as np

from environment import QuoridorState, QuoridorConfig, QuoridorEnv
from alphazero import MCTS, QuoridorRepresentation, QuoridorModel


class SelfPlayConfig:

    def __init__(self,
                 nb_games=25000,
                 nb_simulations=200,
                 max_workers=4) -> None:
        self.nb_games = nb_games
        self.nb_simulations = nb_simulations
        self.max_workers = max_workers


class SelfPlayer:

    def __init__(self, model: QuoridorModel, game_config: QuoridorConfig,
                 environment: QuoridorEnv,
                 representation: QuoridorRepresentation, save_dir: str,
                 selfplay_config: SelfPlayConfig) -> None:
        self.model = model
        # The number of games played for this iteration
        self.nb_games = selfplay_config.nb_games
        self.nb_simulations = selfplay_config.nb_simulations
        self.max_workers = selfplay_config.max_workers

        self.game_config = game_config
        self.environment = environment
        self.representation = representation
        self.save_dir = save_dir

        # Initialize the MCTS module
        self.mcts = MCTS(self.game_config, self.model, self.representation)

        self.state_buffer = []

    def clear(self):
        self.state_buffer = []

    def play_games(self):
        # Don't forget to put model in evaluation mode
        self.model.eval()
        # Use multithreading to play games
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            tasks = {
                executor.submit(self.play_game, i)
                for i in range(self.nb_games)
            }
        wait(tasks)
        return self.save_buffer()

    def play_game(self, game_idx):
        print(f"Playing game {game_idx}")

        # Initialize a game
        state = QuoridorState(self.game_config)
        feature_planes = []
        history = []

        # Play the game
        while not state.done:
            # Take action following MCTS
            # TODO: add dynamic temperature behaviour
            action, policy = self.mcts.select_action(
                self.environment,
                state,
                feature_planes,
                nb_simulations=self.nb_simulations)

            # TODO: make actions invariant as well !!!!!!!!!!!!!!!!

            # Compute state planes
            current_feature_planes = self.representation.generate_instant_planes(
                state)
            feature_planes.append(current_feature_planes)
            current_state_planes = self.representation.generate_state_planes(
                state, feature_planes)

            history.append(
                (state.current_player, current_state_planes, policy))

            # Follow the selected action
            state = self.environment.step_from_index(state, action_idx=action)
            print(
                f"Reached state {state.to_string()}, terminal state: {state.done}"
            )

        # Add the game reward and create a state buffer

        # Draw
        if state.winner == -1:
            reward = 0.0
        # Player 0 won
        elif state.winner == 0:
            reward = 1.0
        # Player 1 won
        else:
            reward = -1.0

        print(f"Completed one self-play game won by {state.winner}")

        for player, state_planes, policy in history:
            self.state_buffer.append(
                (game_idx, state_planes, policy,
                 np.float32(reward) if player == 0 else np.float32(reward *
                                                                   -1.0)))

    def save_buffer(self):
        buffer_str = self.model.to_string(
        ) + f"-g{self.nb_games}-s{self.nb_simulations}.pkl"
        full_path = os.path.join(self.save_dir, buffer_str)
        with open(full_path, "wb") as handle:
            pickle.dump(self.state_buffer,
                        handle,
                        protocol=pickle.HIGHEST_PROTOCOL)
        return full_path