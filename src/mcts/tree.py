import numpy as np
from collections import defaultdict
from tqdm import trange


class MCTSNode():

    def __init__(self,
                 state,
                 player_idx,
                 parent=None,
                 parent_action=None,
                 depth=0):
        self.state = state
        self.player_idx = player_idx
        self.parent = parent
        self.parent_action = parent_action
        self.children = []
        self._nb_visited = 0
        self._results = defaultdict(int)
        self._results[1] = 0
        self._results[-1] = 0
        # print('initialized')
        self._untried_actions = self.untried_actions()
        self.depth = depth
        return

    def untried_actions(self):
        # print('looking for untried actions')
        self._untried_actions = self.state.get_possible_actions(
            self.player_idx)
        return self._untried_actions

    def q(self):
        winning = self._results[1]
        loosing = self._results[-1]
        return winning - loosing

    def n(self):
        return self._nb_visited

    def expand(self):
        action = self._untried_actions.pop()
        next_state = self.state.act(action, self.player_idx)
        child_node = MCTSNode(next_state,
                              next_state.get_opponent(self.player_idx),
                              parent=self,
                              parent_action=action,
                              depth=self.depth + 1)
        self.children.append(child_node)
        print('child depth: ' + str(child_node.depth))
        return child_node

    def is_leaf(self):
        return self.state.is_game_over()

    def rollout(self):
        current_rollout_state = self.state
        player = self.player_idx
        while not current_rollout_state.is_game_over():
            possible_actions = current_rollout_state.get_possible_actions(
                player)
            action = self.rollout_policy(possible_actions)
            current_rollout_state = self.state.act(action, player)
            player = self.state.get_opponent(player)
        if current_rollout_state.player_win(self.player_idx):
            return 1
        return -1

    def backpropagate(self, result):
        self._nb_visited += 1
        self._results[result] += 1
        if self.parent:
            self.parent.backpropagate(-1 * result)

    def is_fully_expanded(self):
        return len(self._untried_actions) == 0

    def best_child(self, c=0.1):
        print('looking for best child')
        print(len(self._untried_actions))
        print(len(self.state.get_possible_actions(self.player_idx)))
        probas = [(child.q() / child.n()) + c * np.sqrt(
            (2 * np.log(self.n()) / child.n())) for child in self.children]
        return self.children[np.argmax(probas)]

    def rollout_policy(self, possible_actions):
        return possible_actions[np.random.randint(len(possible_actions))]

    def _tree_policy(self):
        node = self
        while not node.is_leaf():
            print("is not leaf, depth: " + str(node.depth))
            if not node.is_fully_expanded():
                print('expansion')
                return node.expand()
            else:
                print('leaf!')
                node = node.best_child()
        return node

    def best_action(self):
        print('looking for best action')
        for i in trange(1):
            node = self._tree_policy()
            print(self.children)
            print('tree policy done')
            print(node.depth)
            reward = node.rollout()
            print('rollout done')
            print(i)
            print(self._results)
            # print('rollout done')
            node.backpropagate(reward)
            # print('backpropagation done')
        print('out for')
        print(self.children)
        return self.best_child(c=0.).parent_action
