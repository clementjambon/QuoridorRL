from collections import defaultdict
from math import sqrt
import numpy as np


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


class MTCS:

    def __init__(self,
                 model,
                 nb_actions,
                 c_puct: float = 1.25,
                 epsilon: float = 0.25,
                 dir_alpha=0.03) -> None:
        self.nb_actions = nb_actions

        self.c_puct = c_puct

        self.tree = defaultdict(StateRecord)
        # The current model used for evaluation
        self.model = model

    def puct_action(self, state_str):
        state_record = self.tree[state_str]
        # TODO: add Dirichlet noise for root state
        best_val = -float('inf')
        best_action = -1
        for action, action_record in state_record.actions.items():
            val = action_record.Q_sa + self.c_puct * action_record.P_sa * sqrt(
                state_record.N_s) / (1 + action_record.N_sa)
            if val > best_val:
                best_val = val
                best_action = action

        return best_action


# NOTE: make sure the searched state is in canonical form

    def search(self, state):
        # TODO: filter valid actions!

        state_str = state.to_string()

        # If the searched state is not in the tree, EXPAND
        if state_str not in self.tree:
            p, v = self.model(state.to_model())
            self.tree[state_str].pi_s = p
            return v

        current_state_record = self.tree[state_str]

        # Otherwise, select and iterate
        a = self.puct_action(state_str)
        current_action_record = current_state_record[a]

        # TODO: get next_state after taking action (in canonical form i.e. not depending on the orientation of the board)
        next_state = None
        # Search the next state
        v = self.search(next_state)
        # NOTE: make sure to reverse the propagated value!
        v = -v

        # Backup values
        # NOTE: add virtual loss when adding multithreading!
        current_state_record.N_s += 1
        current_action_record.N_sa += 1
        current_action_record.W_sa += v
        current_action_record.Q_sa = current_action_record.W_sa / current_action_record.N_sa

        # Return the value
        return v

    # Returns the play policy by running nb_simulations
    def play_policy(self,
                    state,
                    nb_simulations: int = 1600,
                    temperature: float = 1):

        # Perform nb_simulations
        for _ in range(nb_simulations):
            self.search(state)

        state_str = state.to_string()
        state_record = self.tree[state_str]
        # If the temperature is zero, it is equivalent to returning the best action (i.e. deterministic policy)
        if temperature == 0:
            best_action = np.argmax(state_record.pi_s)
            policy = np.zeros(self.nb_actions)
            policy[best_action] = 1.0
            return policy
        else:
            policy = np.power(policy, 1.0 / temperature)
            policy /= np.sum(policy)
            return policy
