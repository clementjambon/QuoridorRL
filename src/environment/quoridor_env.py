from platform import node
import numpy as np
from environment.quoridor_action import MoveAction, WallAction, QuoridorAction
from environment.quoridor_state import QuoridorState
from environment.board_graph import BoardGraph
from agents.agents import Agent, RandomAgent, HeuristicAgent
from utils.coords import coords_to_tile

# ----------------------------
# ENVIRONMENT VARIABLES
# ----------------------------

NB_PLAYERS = 2


# ----------------------------
# ENVIRONMENT CLASS
# ----------------------------
class QuoridorEnv:

    def __init__(self, grid_size=9, max_walls=10) -> None:
        super().__init__()

        # create a Quoridor state
        self.grid_size = grid_size
        self.max_walls = max_walls
        self.state = QuoridorState(self.grid_size, self.max_walls)
        self.current_player = 0
        self.done = False

    def move_pawn(self, target_position: tuple[int, int]) -> bool:
        """If permitted, move the current player to the provided position

        Args:
            target_position (tuple[int, int]): targeted position

        Returns:
            bool: True if the action was taken, False otherwise
        """
        if self.state.can_move_player(self.current_player, target_position):
            # Move player
            self.state.move_player(self.current_player, target_position)
            # Test winning move
            self.done = self.state.player_win(self.current_player)
            # Update current player
            self.current_player = (self.current_player + 1) % NB_PLAYERS

            return True

        else:
            print(
                f"QuoridorEnv: cannot move player {self.current_player} to target position {target_position}"
            )

            return False

    def add_wall(self, target_position, direction: int) -> bool:
        """If permitted, adds a wall at the provided location

        Args:
            target_position (_type_): targeted wall location
            direction (int): wall direction

        Returns:
            bool: True if the action was taken, False otherwise
        """

        if self.state.can_add_wall(self.current_player, target_position,
                                   direction):
            # Move player
            self.state.add_wall(self.current_player, target_position,
                                direction)
            # Test winning move
            self.done = self.state.player_win(self.current_player)
            # Update current player
            self.current_player = (self.current_player + 1) % NB_PLAYERS

            return True

        else:
            print(
                f"QuoridorEnv: cannot place wall for player {self.current_player} to target position {target_position} and direction {direction}"
            )

            return False


class QuoridorEnvAgents(QuoridorEnv):

    def __init__(self, grid_size=9, max_walls=10) -> None:
        super().__init__(grid_size, max_walls)
        # uncomment for a game between 2 agents taht only make random choices
        #self.state = QuoridorStateRandomAgents(self.grid_size, self.max_walls)
        #self.state = QuoridorStateHeuristicsAgents(self.grid_size,
        #                                           self.max_walls)

        self.agent0 = HeuristicAgent(0, self.state)
        self.agent1 = HeuristicAgent(1, self.state)

    def play(self):
        #get current player as an Agent obj
        if self.current_player == 0:
            current_agent = self.agent0
            adversary = self.agent1
        else:
            current_agent = self.agent1
            adversary = self.agent0
        #get the board as a Graph object for easier path search
        board_graph = BoardGraph(self.state.walls)

        #choose action this method depends on the type of Agents used
        action = current_agent.choose_action(adversary, board_graph)

        #execute chosen action
        if isinstance(action, MoveAction):
            self.move_pawn(action.get_pos())
        else:
            action_ok = self.add_wall(action.get_pos(), action.get_dir())
            board_graph.add_wall_graph(action.get_pos(), action.get_dir(),
                                       action_ok)

        # Update current player is already done when action is executed

    def move_pawn(self, target_position: tuple[int, int]) -> bool:
        action_ok = super().move_pawn(target_position)
        if action_ok:
            if (self.current_player == 1
                ):  #we already updated current_player in super()
                self.agent0.set_position(
                    coords_to_tile(target_position, self.grid_size))
            else:
                self.agent1.set_position(
                    coords_to_tile(target_position, self.grid_size))
            return True
        return False

    def add_wall(self, target_position, direction: int) -> bool:
        action_ok = super().add_wall(target_position, direction)
        if action_ok:
            if (self.current_player == 0):
                self.agent0.nb_walls_placed += 1
            else:
                self.agent1.nb_walls_placed += 1
            return True
        return False
