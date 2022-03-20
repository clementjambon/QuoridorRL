import os
import pickle
import numpy as np
import pygame as pg

from environment import QuoridorState, QuoridorConfig, QuoridorEnv
from alphazero import MCTS, QuoridorRepresentation, QuoridorModel

from interactive import INNER_CELL_SIZE, EMPTY_CELL_COLOR, PAWN_0_COLOR, PAWN_1_COLOR, SIZE, WALL_THICKNESS, FPS, WALL_COLOR
from interactive import draw_gui, draw_board, draw_state, init_surfaces


class SelfPlayConfig:
    def __init__(self,
                 nb_games=25000,
                 nb_simulations=200,
                 max_workers=4,
                 initial_temperature=1.0,
                 tempered_steps=20,
                 limited_time=None,
                 str_history=False,
                 verbose=False,
                 display_mode=False,
                 intermediate_reward=False) -> None:
        self.nb_games = nb_games
        self.nb_simulations = nb_simulations
        self.max_workers = max_workers
        self.initial_temperature = initial_temperature
        self.tempered_steps = tempered_steps
        self.limited_time = limited_time
        self.str_history = str_history
        self.verbose = verbose
        self.display_mode = display_mode
        self.intermediate_reward = intermediate_reward

    def description(self) -> str:
        return f"SelfPlayConfig: nb_games={self.nb_games}; nb_simulations(MCTS):{self.nb_simulations}; max_workers(NOT WORKING)={self.max_workers}; inital_temperature={self.initial_temperature}; tempered_steps={self.tempered_steps}; limited_time={self.limited_time}; intermediate_reward={self.intermediate_reward}"


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
        self.str_history = []

        if self.selfplay_config.display_mode:
            pg.init()

            self.screen = pg.display.set_mode(SIZE, pg.SCALED)
            pg.display.set_caption("QuoridorRL - State Visualization")

            self.background, self.cell, self.pawn_0, self.pawn_1, self.horizontal_wall, self.vertical_wall = init_surfaces(
                self.screen)

            # Display the background
            self.screen.blit(self.background, (0, 0))
            pg.display.flip()

            clock = pg.time.Clock()

    def clear(self):
        self.state_buffer = []
        self.str_history = []

    def play_games(self):
        print("###################################")
        print(f"SelfPlayer starting {self.nb_games} with:")
        print(self.selfplay_config.description())
        print(self.game_config.description())
        print(self.model.description())
        print(self.representation.description())
        print("###################################")
        # Don't forget to put model in evaluation mode
        self.model.eval()
        # TODO: use multithreading to play games
        for i in range(self.nb_games):
            self.play_game(i)

        if self.selfplay_config.display_mode:
            pg.quit()

        if self.selfplay_config.str_history:
            self.save_str_history()
        return self.save_buffer()

    def play_game(self, game_idx):
        print(f"Selfplayer: playing game {game_idx}")

        # Initialize a game and MCTS
        state = QuoridorState(self.game_config)
        mcts = MCTS(self.game_config, self.model, self.representation)
        feature_planes = []
        history = []

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
                limited_time=self.selfplay_config.limited_time,
                intermediate_reward=self.selfplay_config.intermediate_reward)

            # Compute state planes
            current_feature_planes = self.representation.generate_instant_planes(
                state)
            feature_planes.append(current_feature_planes)
            current_state_planes = self.representation.generate_state_planes(
                state, feature_planes)

            history.append(
                (state.current_player, current_state_planes, policy))

            self.str_history.append(state.to_string())

            # Follow the selected action
            state = self.environment.step_from_index(state, action_idx=action)
            if self.selfplay_config.verbose:
                print(
                    f"Selfplayer: reached state {state.to_string(add_nb_walls=True, add_current_player=True)}, terminal state: {state.done}"
                )
                print(
                    f"After this step, intermediate reward is {self.environment.get_intermediate_reward(state, self.environment.get_opponent(state.current_player))}"
                )

            if self.selfplay_config.display_mode:
                self.screen.blit(self.background, (0, 0))
                draw_board(self.screen, self.game_config, self.cell)
                draw_state(self.screen, self.game_config, state, self.pawn_0,
                           self.pawn_1, self.horizontal_wall,
                           self.vertical_wall, False)
                draw_gui(self.screen, self.game_config, state, 0, state.done)
                pg.display.flip()

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

    def save_str_history(self):
        buffer_str = self.model.to_string(
        ) + f"-g{self.nb_games}-s{self.nb_simulations}.txt"
        full_path = os.path.join(self.save_dir, buffer_str)
        with open(full_path, 'w') as handle:
            for state_str in self.str_history:
                handle.write(f"{state_str}\n")
