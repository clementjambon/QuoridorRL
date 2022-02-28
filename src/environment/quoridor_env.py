from platform import node
import numpy as np
from environment.quoridor_action import MoveAction, WallAction, QuoridorAction
from environment.quoridor_state import QuoridorState, QuoridorStateHeuristicsAgents, QuoridorStateRandomAgents
from environment.board_graph import BoardGraph
from utils.coords import coords_to_tile, tile_to_coords

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
        self.state = QuoridorStateHeuristicsAgents(self.grid_size,
                                                   self.max_walls)

    def play(self):
        #get current player as an Agent obj
        if self.current_player == 0:
            current_agent = self.state.agent0
        else:
            current_agent = self.state.agent1
        #get the board as a Graph object for easier path search
        board_graph = BoardGraph(self.state.walls)
        #test
        #self.add_wall_graph((7, 7), 1, board_graph)
        #self.add_wall_graph((2, 2), 1, board_graph)
        #self.add_wall_graph((0, 3), 0, board_graph)
        #print(self.state.walls.T)
        #board_graph.print_adj_graph()
        #if not ok:
        #self.helper_test(70, board_graph)
        #    ok = self.add_wall_graph((0, 2), 0, board_graph)
        board_graph.move_to_next_col_feature(current_agent.get_position(),
                                             current_agent.get_targets()[0])
        #choose action this method depends on the type of Agents used
        action = current_agent.choose_action(
            self.state.get_possible_actions(self.current_player), board_graph)

        #execute chosen action

        if isinstance(action, MoveAction):
            self.move_pawn(action.get_pos())
        else:
            self.add_wall_graph(action.get_pos(), action.get_dir(),
                                board_graph)

        # Update current player is already done when action is executed

    def add_wall_graph(self, target_position, direction: int,
                       board_graph: BoardGraph) -> bool:
        action_ok = super().add_wall(target_position, direction)
        if action_ok:
            node_pos = coords_to_tile(target_position, self.state.grid_size)
            if direction == 0:  #horizontal wall
                board_graph.remove_edge(node_pos, node_pos + 1)
                board_graph.remove_edge(node_pos + self.grid_size,
                                        node_pos + self.grid_size + 1)
            else:  #vertical wall
                board_graph.remove_edge(node_pos, node_pos + self.grid_size)
                board_graph.remove_edge(node_pos + 1,
                                        node_pos + 1 + self.grid_size)
            return True
        return False

    def helper_test(self, node_pos, board_graph):
        #Test
        nodes = [
            node_pos, node_pos + 1, node_pos + self.grid_size,
            node_pos + self.grid_size + 1
        ]
        for i in nodes:
            print("Vertex " + str(i) + ":", end="")
            adjlist = board_graph.get_adj_list(i)
            for node in adjlist:
                print(" -> {}".format(node.to_string()), end="")
            print(" \n")
