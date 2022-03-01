import torch
from collections import defaultdict
from math import sqrt
from copy import deepcopy, copy
import numpy as np
import time
import os

from alphazero import QuoridorRepresentation, QuoridorModel
from environment import QuoridorState, QuoridorEnv, QuoridorConfig
from utils import change_action_perspective, write_history


class ActionRecord:

    def __init__(self) -> None:
        self.N_sa = 0
        self.W_sa = 0
        self.Q_sa = 0
        self.P_sa = 0


class StateRecord:

    def __init__(self) -> None:
        self.actions = defaultdict(ActionRecord)
        # The sum over all actions expanded in this node record
        self.N_s = 0
        self.pi_s = None


class MCTS:

    def __init__(self,
                 game_config: QuoridorConfig,
                 model: QuoridorModel,
                 state_representation: QuoridorRepresentation,
                 c_puct: float = 1.25,
                 epsilon: float = 0.25,
                 dir_alpha=0.1) -> None:
        self.nb_actions = game_config.nb_actions

        self.c_puct = c_puct
        self.epsilon = epsilon
        self.dir_alpha = dir_alpha

        self.tree = defaultdict(StateRecord)
        # The current model used for evaluation
        self.model = model
        self.state_representation = state_representation

    def reset_tree(self):
        # Reset the search tree
        self.tree = defaultdict(StateRecord)

    def select_action(self,
                      environment: QuoridorEnv,
                      state: QuoridorState,
                      previous_feature_planes,
                      nb_simulations: int = 800,
                      temperature: float = 1,
                      limited_time: float = None):
        # Selects an action provided the current state

        # Don't forget to reset the tree
        self.reset_tree()

        # Compute the policy with MCTS
        policy = self.play_policy(environment,
                                  state,
                                  previous_feature_planes,
                                  nb_simulations=nb_simulations,
                                  temperature=temperature,
                                  limited_time=limited_time)

        # Return the action according to the provided policy distribution
        return change_action_perspective(
            state.current_player,
            int(np.random.choice(np.arange(self.nb_actions), p=policy)),
            grid_size=environment.grid_size), policy

    def puct_action(self,
                    environment: QuoridorEnv,
                    state: QuoridorState,
                    state_str: str,
                    is_root_state=False):
        state_record = self.tree[state_str]

        # Update action probabilities by renormalizing over valid actions
        # Just after expansion, get all possible actions
        if state_record.pi_s is not None:
            sum_p = 0
            # print(state.to_string(add_nb_walls=True, add_current_player=True))
            # print([
            #     action.to_string()
            #     for action in environment.get_possible_actions(state)
            # ])
            for action in environment.get_possible_actions(state):
                action_idx = action.to_perspective(
                    state.current_player,
                    environment.grid_size).to_index(environment.grid_size)
                # Action probabilities have already been stored in the StateRecord normally
                action_p = state_record.pi_s[action_idx]
                # Thus, update the ActionRecords accordingly
                state_record.actions[action_idx].P_sa = action_p
                sum_p += action_p
            # Normalize probabilities over valid actions only
            for action in state_record.actions.values():
                # Add a small constant to ensure that we do not divide by zero
                action.P_sa /= (sum_p + 1e-8)
            # Clear the temporary pi from the StateRecord
            state_record.pi_s = None

        best_val = -float('inf')
        best_action_idx = -1
        for action_idx, action_record in state_record.actions.items():
            P_sa = action_record.P_sa
            # If we're in the root state, apply dirichlet noise
            if is_root_state:
                # TODO: check random alpha here
                P_sa = (1.0 - self.epsilon
                        ) * P_sa + self.epsilon * np.random.dirichlet(
                            self.dir_alpha)
            val = action_record.Q_sa + self.c_puct * P_sa * sqrt(
                state_record.N_s) / (1 + action_record.N_sa)
            if val > best_val:
                best_val = val
                best_action_idx = action_idx
        if best_action_idx == -1:
            print("No best action")
        return best_action_idx


# NOTE: make sure the searched state is in canonical form

# Feature_planes provide the already computed feature_planes

    def search(self, environment: QuoridorEnv, state: QuoridorState,
               init_feature_planes):
        # TODO: filter valid actions!

        feature_planes = deepcopy(init_feature_planes)
        explored_branches = []
        branch_value = 0.0
        # history = []
        # last_state_t = 0

        # Search the tree
        # TODO: deal with None cases
        while True:
            if state is None:
                # THIS SHOULD NOT HAPPEN
                print("MCTS: search ended with None state!")
                print(history)
                # print(last_state_t)
                # write_history(
                #     os.path.abspath(
                #         os.path.join(os.path.dirname(__file__),
                #                      '../../data/test.txt')), history)
                # exit()
                break

            if state.done:
                if state.winner == -1:
                    branch_value = 0.0
                else:
                    if state.winner == state.current_player:
                        # In practice, this should not happen!
                        branch_value = 1.0
                    else:
                        branch_value = -1.0
                break

            state_str = state.to_string(add_nb_walls=True,
                                        add_current_player=True)
            # history.append(
            #     state.to_string(add_nb_walls=True, add_current_player=True))
            # last_state_t = state.t
            #print(f"Searching {state_str} with depth {len(feature_planes)}")
            current_feature_plane = self.state_representation.generate_instant_planes(
                state)
            feature_planes.append(current_feature_plane)

            # If the searched state is not in the tree, EXPAND
            if state_str not in self.tree:
                state_planes = self.state_representation.generate_state_planes(
                    state, feature_planes)
                p, v = self.model(
                    state_planes.unsqueeze(0).to(self.model.device))
                p = p[0]
                self.tree[state_str].pi_s = p
                branch_value = v
                break

            # Otherwise, select and iterate
            action_idx = self.puct_action(environment, state, state_str)

            # Get next_state after taking action
            state = environment.step_from_index(
                state,
                change_action_perspective(state.current_player, action_idx,
                                          environment.grid_size))

            # Track (state, action pairs)
            explored_branches.append((state_str, action_idx))

        # print(f"Backing up {len(explored_branches)} branches")

        # Backup values
        # NOTE: add virtual loss when adding multithreading!
        for state_str, action_idx in reversed(explored_branches):
            # NOTE: make sure to reverse the propagated value!
            branch_value *= -1.0

            current_state_record = self.tree[state_str]
            current_action_record = current_state_record.actions[action_idx]
            current_state_record.N_s += 1
            current_action_record.N_sa += 1
            current_action_record.W_sa += branch_value
            current_action_record.Q_sa = current_action_record.W_sa / current_action_record.N_sa

    # Returns the play policy by running nb_simulations
    def play_policy(self,
                    environment: QuoridorEnv,
                    state: QuoridorState,
                    previous_feature_planes,
                    nb_simulations: int = 800,
                    temperature: float = 1,
                    limited_time: float = None):

        start_time = time.time()

        # Perform nb_simulations (or stopped when the provided time is elapsed)
        for i in range(nb_simulations):
            if limited_time is not None and time.time(
            ) - start_time > limited_time:
                break

            # NOTE: deepcopy the state before performing a state, otherwise, it will be modified!
            init_state = deepcopy(state)
            # print(
            #     f"MCTS: searching state {init_state.to_string(add_nb_walls=True, add_current_player=True)}"
            # )
            self.search(environment, init_state, previous_feature_planes)
            # if (i + 1) % (nb_simulations // 10) == 0:
            #     print(
            #         f'Performed {i+1} simulations out of {nb_simulations} ({(i+1)/(nb_simulations)*100}%)'
            #     )

        state_str = state.to_string(add_nb_walls=True, add_current_player=True)
        state_record = self.tree[state_str]

        # Collect policy from state_record
        policy = np.zeros(self.nb_actions)
        for i, action in state_record.actions.items():
            policy[i] = action.P_sa

        # If the temperature is zero, it is equivalent to returning the best action (i.e. deterministic policy)
        if temperature == 0:
            best_action = np.argmax(policy)
            policy = np.zeros(self.nb_actions, dtype=np.float32)
            policy[best_action] = 1.0
            return policy
        else:
            policy = np.power(policy, 1.0 / temperature, dtype=np.float32)
            policy /= np.sum(policy)
            return policy
