from collections import defaultdict
import numpy as np
from tqdm import trange
from copy import deepcopy


class MCTSNode():
    """
    Implement a node to perform Monte-Carlo Tree Search
    """

    def __init__(self,
                 env,
                 state,
                 player_idx,
                 parent=None,
                 parent_action=None,
                 depth=0,
                 iterations=1000):
        self.env = env
        self.state = state
        self.player_idx = player_idx
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._nb_visited = 0
        self._results = defaultdict(int)
        self._results[1] = 0
        self._results[-1] = 0
        self._outcome_parent_action = 0
        self._nb_parent_action = 0
        self._untried_actions = self.untried_actions()
        self.depth = depth
        self.it = iterations
        return

    def untried_actions(self):
        self._untried_actions = self.env.get_possible_actions(self.state)
        return self._untried_actions

    def q(self):
        winning = self._results[1]
        loosing = self._results[-1]
        q_mc = -1 * (winning - loosing) / self.n()
        q_amaf = -1 * self._outcome_parent_action / self._nb_parent_action
        beta = np.sqrt(1000.0 / (3 * self.n() + 1000.0))
        return (1 - beta) * q_mc + beta * q_amaf

    def n(self):
        return self._nb_visited

    def expand(self):
        action = self._untried_actions.pop()
        next_state = self.env.act(self.state, action)
        child_node = MCTSNode(self.env,
                              next_state,
                              self.env.get_opponent(self.player_idx),
                              parent=self,
                              parent_action=action,
                              depth=self.depth + 1)
        self.children.append(child_node)
        return child_node

    def is_leaf(self):
        return self.env.is_game_over(self.state)

    def rollout(self):
        current_rollout_state = deepcopy(self.state)
        player = self.player_idx
        actions = []
        while not (current_rollout_state.done
                   or self.env.is_game_over(current_rollout_state)):
            possible_actions = self.env.get_possible_actions(
                current_rollout_state)
            actions = []
            for action in possible_actions:
                if action.type == 0:
                    actions.append(action)
            possible_actions = actions
            action = self.rollout_policy(possible_actions,
                                         current_rollout_state)
            current_rollout_state = self.env.actNoCopy(current_rollout_state,
                                                       action)
            player = self.env.get_opponent(player)
            actions.append(action)
        if self.env.player_win(current_rollout_state, self.player_idx):
            return 1, actions
        return -1, actions

    def backpropagate(self, result, actions):
        self._nb_visited += 1
        self._results[result] += 1
        actions.append(self.parent_action)
        if self.parent:
            nb = 0
            for action in actions:
                if action == self.parent_action:
                    nb += 1
            if nb > 0:
                self._outcome_parent_action += result
                self._nb_parent_action += nb
            self.parent.backpropagate(-1 * result, actions)

    def is_fully_expanded(self):
        return len(self._untried_actions) == 0

    def best_child(self, c=0.1):
        probas = [
            child.q() + c * np.sqrt((1 * np.log(self.n()) / child.n()))
            for child in self.children
        ]
        return self.children[np.argmax(probas)]

    def rollout_policy(self, possible_actions, state):
        """
        Default policy
        """
        if len(possible_actions) == 0:
            print("no possible action")
            print(state.to_string(False, True, True))
        return possible_actions[np.random.randint(len(possible_actions))]

    def _tree_policy(self):
        node = self
        while not node.is_leaf():
            if not node.is_fully_expanded():
                return node.expand()
            else:
                node = node.best_child(c=100.)
        return node

    def best_action(self):
        for i in trange(self.it):
            node = self._tree_policy()
            reward, actions = node.rollout()
            node.backpropagate(reward, actions)
        node = self
        while len(node.children) > 0:
            node = node.children[0]
        return self.best_child(c=0.).parent_action

    def max_depth(self):
        if len(self.children) == 0:
            return 0
        return 1 + np.max([child.max_depth() for child in self.children])
