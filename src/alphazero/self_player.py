import os
import pickle
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait, as_completed
import numpy as np
from pygame import init

from environment import QuoridorState, QuoridorConfig, QuoridorEnv
from alphazero import MCTS, QuoridorRepresentation, QuoridorModel


class SelfPlayConfig:

    def __init__(self,
                 nb_games=25000,
                 nb_simulations=200,
                 max_workers=4,
                 initial_temperature=1.0,
                 tempered_steps=20,
                 limited_time=None) -> None:
        self.nb_games = nb_games
        self.nb_simulations = nb_simulations
        self.max_workers = max_workers
        self.initial_temperature = initial_temperature
        self.tempered_steps = tempered_steps
        self.limited_time = limited_time


class SelfPlayer:

    def __init__(self, model: QuoridorModel, game_config: QuoridorConfig,
                 environment: QuoridorEnv,
                 representation: QuoridorRepresentation, save_dir: str,
                 selfplay_config: SelfPlayConfig) -> None:
        self.model = model
        # The number of games played for this iteration
        self.selfplay_config = selfplay_config
        self.nb_games = selfplay_config.nb_games
        self.nb_simulations = selfplay_config.nb_simulations
        self.max_workers = selfplay_config.max_workers

        self.game_config = game_config
        self.environment = environment
        self.representation = representation
        self.save_dir = save_dir

        self.state_buffer = []

    def clear(self):
        self.state_buffer = []

    def play_games(self):
        # Don't forget to put model in evaluation mode
        self.model.eval()
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.play_game, i)
                for i in range(self.nb_games)
            ]
            for future in as_completed(futures):
                try:
                    data = future.result()
                except Exception as exc:
                    print(f'Selfplay: generated an exception: {exc}')
                else:
                    self.state_buffer += data
        # # TODO: use multithreading to play games
        # for i in range(self.nb_games):
        #     self.play_game(i)

        return self.save_buffer()

    def play_game(self, game_idx):
        print(f"Selfplayer: playing game {game_idx}")

        # Initialize a game and MCTS
        state = QuoridorState(self.game_config)
        mcts = MCTS(self.game_config, self.model, self.representation)
        feature_planes = []
        history = []
        state_buffer = []

        # Play the game
        while not state.done:
            # Take action following MCTS
            temperature = self.selfplay_config.initial_temperature if state.t < self.selfplay_config.tempered_steps else 0.0
            # print(
            #     f"Self-player: searching state {state.to_string(add_nb_walls=True, add_current_player=True)} with temperate {temperature}"
            # )
            action, policy = mcts.select_action(
                self.environment,
                state,
                feature_planes,
                nb_simulations=self.nb_simulations,
                temperature=temperature,
                limited_time=self.selfplay_config.limited_time)

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
            # print(
            #     f"Selfplayer: reached state {state.to_string(add_nb_walls=True, add_current_player=True)}, terminal state: {state.done}"
            # )

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

        print(
            f"SelfPlayer: completed one self-play game won by {state.winner}")

        for player, state_planes, policy in history:
            state_buffer.append(
                (game_idx, state_planes, policy,
                 np.float32(reward) if player == 0 else np.float32(reward *
                                                                   -1.0)))
        return state_buffer

    def save_buffer(self):
        buffer_str = self.model.to_string(
        ) + f"-g{self.nb_games}-s{self.nb_simulations}.pkl"
        full_path = os.path.join(self.save_dir, buffer_str)
        with open(full_path, "wb") as handle:
            pickle.dump(self.state_buffer,
                        handle,
                        protocol=pickle.HIGHEST_PROTOCOL)
        return full_path