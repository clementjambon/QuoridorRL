from collections import defaultdict
import numpy as np
from tqdm import trange
from copy import deepcopy

# from utils import get_offset


class MCTSNode():

    def __init__(self,
                 env,
                 state,
                 player_idx,
                 parent=None,
                 parent_action=None,
                 depth=0):
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
        # print('initialized')
        self._untried_actions = self.untried_actions()
        self.depth = depth
        return

    def untried_actions(self):
        # print('looking for untried actions')
        self._untried_actions = self.env.get_possible_actions(self.state)
        # actions = []
        # for action in self._untried_actions:
        #     if action.type == 0:
        #         # print("untried action:" + str(action.player_pos))
        #         actions.append(action)
        # self._untried_actions = actions
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
        # print('child depth: ' + str(child_node.depth))
        return child_node

    def is_leaf(self):
        # print('depth ' + str(self.depth))
        # print("Position of PLAYER 0: " + str(self.state.player_positions[0]))
        # print("Position of PLAYER 1: " + str(self.state.player_positions[1]))
        # print(self.state.to_string() + str(self.env.is_game_over(self.state)))
        return self.env.is_game_over(self.state)

    def rollout(self):
        current_rollout_state = deepcopy(self.state)
        player = self.player_idx
        actions = []
        while not (current_rollout_state.done
                   or self.env.is_game_over(current_rollout_state)):
            # print("initial position" +
            #       str(current_rollout_state.player_positions[player]))
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
            # print("final position" +
            #       str(current_rollout_state.player_positions[player]))
            # print(current_rollout_state.x_targets[player] -
            #       current_rollout_state.player_positions[player][0])
            player = self.env.get_opponent(player)
            actions.append(action)
        # print("GAME OVER!")
        if self.env.player_win(current_rollout_state, self.player_idx):
            return 1, actions
        return -1, actions

    def backpropagate(self, result, actions):
        self._nb_visited += 1
        self._results[result] += 1
        actions.append(self.parent_action)
        # for action in actions:  # TODO: traiter les doublons ?
        #     if action in self._subtree_actions:
        #         self._subtree_actions[action] += result
        #         self._nb_actions[action] += 1
        #     else:
        #         self._subtree_actions[action] = result
        #         self._nb_actions[action] = 1
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
        # print(str(len(self._untried_actions)) + " untried actions")
        return len(self._untried_actions) == 0

    def best_child(self, c=0.1):
        # print('looking for best child')
        # print(len(self._untried_actions))
        # print(len(self.state.get_possible_actions(self.player_idx)))
        probas = [
            child.q() + c * np.sqrt((1 * np.log(self.n()) / child.n()))
            for child in self.children
        ]
        return self.children[np.argmax(probas)]

    def rollout_policy(self, possible_actions, state):
        """
        Default policy
        """
        # for action in possible_actions:
        #     if action.type == 0:
        #         offset = action.player_pos[1] - self.state.player_positions[
        #             action.player_idx][1]
        #         if (action.player_idx == 0
        #                 and offset > 0) or (action.player_idx == 1
        #                                     and offset < 0):
        #             # print(self.state.x_targets[action.player_idx] -
        #             #       self.state.player_positions[action.player_idx][0])
        #             return action
        if len(possible_actions) == 0:
            print("no possible action")
            print(state.to_string(False, True, True))
        return possible_actions[np.random.randint(len(possible_actions))]

    def _tree_policy(self):
        node = self
        while not node.is_leaf():
            # print("is not leaf, depth: " + str(node.depth))
            if not node.is_fully_expanded():
                # print('expansion')
                return node.expand()
            else:
                # print('best child')
                node = node.best_child(c=100.)
                # print(node.depth)
                # print("NO EXPANSION")
                # print("Position of PLAYER 0: " +
                #       str(node.state.player_positions[0]))
                # print("Position of PLAYER 1: " +
                #       str(node.state.player_positions[1]))
        return node

    def best_action(self):
        # print('looking for best action')
        for i in trange(100):
            node = self._tree_policy()
            # print(self.children)
            # print('tree policy done')
            # print(node.depth)
            reward, actions = node.rollout()
            # print('rollout done')
            # print(i)
            # print(self._results)
            # print('rollout done')
            node.backpropagate(reward, actions)
            # print('backpropagation done')
        # print('out for')
        # print(self.children)
        print(self._results[1])
        print(self._results[-1])
        print(self.n())
        node = self
        while len(node.children) > 0:
            print(node.depth, node.children)
            node = node.children[0]
        return self.best_child(c=0.).parent_action

    def max_depth(self):
        if len(self.children) == 0:
            return 0
        return 1 + np.max([child.max_depth() for child in self.children])
