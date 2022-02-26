import random
from environment.quoridor_action import MoveAction, QuoridorAction
from environment.board_graph import BoardGraph
from utils import convert_poscoord_to_posnodenb


class Agent:
    """Interface for Agents
    """

    def __init__(self, player_idx: int, pos, nb_walls, target,
                 grid_size: int) -> None:
        self.player_idx = player_idx

        coords = [
            pos[1], pos[0]
        ]  #strangely player positions rows and columns are inversed when passed from state
        self.player_pos = convert_poscoord_to_posnodenb(coords, grid_size)
        self.grid_size = grid_size
        self.nb_walls_placed = nb_walls
        #get all vertices on last column that is the target
        self.targets = []
        for i in range(grid_size):
            self.targets.append(target + i * grid_size)

    def choose_action(self,
                      list_actions: list[QuoridorAction],
                      board: BoardGraph = None) -> QuoridorAction:
        return None

    def set_position(self, player_pos: tuple[int, int]):
        self.player_pos = convert_poscoord_to_posnodenb(
            player_pos, self.grid_size)

    def get_position(self):
        return self.player_pos

    def get_targets(self):
        return self.targets  #a list of all vertices


class RandomAgent(Agent):
    """Agent that only takes random actions
    """

    def choose_action(self,
                      list_actions: list[QuoridorAction],
                      board: BoardGraph = None) -> QuoridorAction:
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


class HeuristicAgent(Agent):
    """Agent that makes choices based on heuristics
    """

    def choose_action(self,
                      list_actions: list[QuoridorAction],
                      board: BoardGraph = None) -> QuoridorAction:
        """
        board has to be passed as argument
        """
        move_actions = [
            action for action in list_actions
            if isinstance(action, MoveAction)
        ]
        if len(move_actions) == len(list_actions):
            #ie no more walls available
            #search for shortest path to target
            parentsMap, nodeCosts = board.dijkstra(self.get_position())
            closest_target = None
            cost = float('inf')
            for target in self.get_targets():
                if nodeCosts[target] < cost:
                    cost = nodeCosts[target]
                    closest_target = target
            path = board.make_path(parentsMap, closest_target)
            return path[1]  #path[0] is the current position
        else:
            if random.random() > 0.5:
                random_idx = random.randint(0, len(move_actions) - 1)
                return move_actions[random_idx]
            else:
                random_idx = random.randint(0, len(list_actions) - 1)
                return list_actions[random_idx]
