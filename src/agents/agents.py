import random
from abc import ABC, abstractmethod
from environment.quoridor_action import MoveAction, QuoridorAction


class Agent:
    """Interface for Agents
    """

    def __init__(self, player_idx: int, pos, nb_walls, target) -> None:
        self.player_idx = player_idx
        self.player_pos = pos
        self.nb_walls_placed = nb_walls
        self.target = target

    @abstractmethod
    def choose_action(self,
                      list_actions: list[QuoridorAction]) -> QuoridorAction:
        pass

    def set_position(self, player_pos):
        self.player_pos = player_pos

    def get_position(self):
        return self.player_pos


class RandomAgent(Agent):
    """Agent that only takes random actions
    """

    def choose_action(self,
                      list_actions: list[QuoridorAction]) -> QuoridorAction:
        """
        there are way more wall actions possible but I want ± 50/50 chance btw either 
        (I slightly fav moveaction as there are only 10 walls)
        """
        move_actions = [
            action for action in list_actions
            if isinstance(action, MoveAction)
        ]
        if random.random() > 0.5:
            random_idx = random.randint(0, len(move_actions) - 1)
            return move_actions[random_idx]
        else:
            random_idx = random.randint(0, len(list_actions) - 1)
            return list_actions[random_idx]
