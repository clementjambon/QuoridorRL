import random
import copy
from environment.quoridor_action import MoveAction, QuoridorAction
from environment.board_graph import BoardGraph
from utils import tile_to_coords, coords_to_tile
from environment.quoridor_state import QuoridorState


class Agent:
    """Interface for Agents
    """

    def __init__(self, player_idx: int, state: QuoridorState) -> None:
        self.player_idx = player_idx
        self.state = state
        self.player_pos = coords_to_tile(state.player_positions[player_idx],
                                         state.grid_size)
        self.grid_size = state.grid_size
        self.nb_walls_placed = state.nb_walls[player_idx]
        #get all vertices on last column that is the target
        target = state.x_targets[player_idx]
        self.targets = []
        for i in range(self.grid_size):
            if (target == 0):  #first col
                self.targets.append(i)
            else:  #last col
                self.targets.append(i + self.grid_size * (self.grid_size - 1))

    def choose_action(self,
                      adversary,
                      board: BoardGraph = None) -> QuoridorAction:
        return None

    #def set_position(self, player_pos: tuple[int, int]):
    #    self.player_pos = coords_to_tile(player_pos, self.grid_size)
    def set_position(self, player_pos: int):
        self.player_pos = player_pos

    def get_position(self):
        return self.player_pos

    def get_targets(self):
        return self.targets  #a list of all vertices


class RandomAgent(Agent):
    """Agent that only takes random actions
    """

    def choose_action(self,
                      adversary: Agent,
                      board: BoardGraph = None) -> QuoridorAction:
        """
        there are way more wall actions possible but I want ± 50/50 chance btw either 
        (I slightly fav moveaction as there are only 10 walls)
        """
        list_actions = self.state.get_possible_actions(self.player_idx)
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
    """
    Agent that makes choices based on heuristics
    """

    def choose_action(self,
                      adversary: Agent,
                      board: BoardGraph = None) -> QuoridorAction:
        """
        board has to be passed as argument for this agent
        """
        list_actions = self.state.get_possible_actions(self.player_idx)

        move_actions = [
            action for action in list_actions
            if isinstance(action, MoveAction)
        ]
        #no more walls available
        #search for shortest path to target
        if len(move_actions) == len(list_actions):
            best_move = self.move_to_target(board)
            return best_move
        #minimax to choose next move
        else:
            best_score = float('-inf')
            best_move = None
            test = True
            for action in list_actions:

                #apply action to get possible board
                #do a copy of the state to apply action on it without altering real current state of the board
                real_pos_agent = self.get_position()
                board_next_move = BoardGraph(
                    self.state.walls)  #copy of current board
                state_next = copy.copy(self.state)
                if test:
                    print(state_next)
                    print(self.state)
                    test = False
                self.helper_apply_action(action, board_next_move, state_next)

                score = self.minimax(
                    adversary, board_next_move, state_next, False, 0
                )  #next move is the opponent since we we are currently trying our move

                #undo move action
                self.set_position(real_pos_agent)

                if score > best_score:
                    best_score = score
                    best_move = action
            return best_move

    def move_to_target(self, board: BoardGraph) -> MoveAction:
        """
        Use Dijkstra algorithm to find best move to reach target
        """
        #print(self.get_position())
        parentsMap, nodeCosts = board.dijkstra(self.get_position())
        closest_target = None
        cost = float('inf')
        for target in self.get_targets():
            if nodeCosts[target] < cost:
                cost = nodeCosts[target]
                closest_target = target
        path = board.make_path(parentsMap, closest_target)
        #convert vertex nb to coords
        path_coords = tile_to_coords(path[1], self.grid_size)
        best_move = MoveAction(path_coords, self.player_idx)
        return best_move  #path[0] is the current position

    def position_feature(self) -> int:
        """
        the simplest evaluation features is the number of columns that the pawn is away from his base line column
        if the pawn is on his base line, the value is 0. If the pawn is on the goal line, the value is 8.
        """
        coords = tile_to_coords(self.get_position(), self.grid_size)
        if self.player_idx == 0:
            return coords[0]  #rows and cols are strangely inversed
        else:
            return self.grid_size - 1 - coords[0]

    def position_difference(self, adversary: Agent) -> int:
        """
        This feature returns the difference between the position feature
        of the Max player and the position feature of the Min player.
        It actually indicates how good your progress is compared to the opponent’s progress.
        """
        return self.position_feature() - adversary.position_feature()

    def move_to_next_col_feature(self, board: BoardGraph) -> int:
        """
        2 features can be derived : 
        • MINIMIZE nb of moves to next for current player (attacking move)
        • MAXIMIZE nb of moves for adversary player (defensive)
        each player will try to place fences in such a way that his opponent has to
        take as many steps as possible to get to his goal. To achieve this, 
        the fences have to be placed so that the opponent has to move up and down the board.
        This feature calculates the minimum number of steps that have to be taken to reach the next column
        A small amount of steps has to give a higher evaluation. 
        So the number of steps, of the Max player to the next column, 
        is raised by the power of −1.

        """
        parentsMap, nodeCosts = board.dijkstra(self.get_position())

        if self.player_idx == 0:
            next_col = tile_to_coords(self.get_position(),
                                      self.grid_size)[0] + 1
        else:
            next_col = tile_to_coords(self.get_position(),
                                      self.grid_size)[0] - 1
        #get the tiles nb of the column
        vertices_next_col = []
        for i in range(self.grid_size):
            vertices_next_col.append(next_col * self.grid_size + i)
        #find cost  of closest tile in next col
        cost = float('inf')
        for target in vertices_next_col:
            if nodeCosts[target] < cost:
                cost = nodeCosts[target]
        return pow(cost, -1)

    def minimax(self, adversary: Agent, board: BoardGraph,
                state: QuoridorState, is_maximizing: bool, depth: int):
        """
        the search depth of the MiniMax algorithm was set at 2.
        """
        if depth == 2:
            f1 = self.position_feature()  #position_feat
            f2 = self.position_difference(adversary)  #position_difference
            f3 = self.move_to_next_col_feature(board)  #min_Mymove_next_col
            f4 = adversary.move_to_next_col_feature(
                board)  #max_Advmove_next_col
            score = f1 + f2 + f3 - f4
            return score

        if is_maximizing:
            best_score = float('-inf')
            list_actions = state.get_possible_actions(
                self.player_idx)  #maximizing = current player
            for action in list_actions:
                real_pos_agent = self.get_position()
                board_next_move = BoardGraph(
                    state.walls)  #copy of current board
                state_next = copy.copy(state)
                self.helper_apply_action(action, board_next_move, state_next)
                score = self.minimax(adversary, board_next_move, state_next,
                                     False, depth + 1)
                self.set_position(real_pos_agent)
                best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            list_actions = state.get_possible_actions(
                adversary.player_idx)  #maximizing = current player
            for action in list_actions:
                real_pos_agent = adversary.get_position()
                board_next_move = BoardGraph(
                    state.walls)  #copy of current board
                state_next = copy.copy(state)
                self.helper_apply_action(action, board_next_move, state_next)
                score = adversary.minimax(self, board_next_move, state_next,
                                          True, depth + 1)
                adversary.set_position(real_pos_agent)
                best_score = min(score, best_score)
            return best_score

    def helper_apply_action(self, action: QuoridorAction, board: BoardGraph,
                            state: QuoridorState):
        if isinstance(action, MoveAction):
            self.set_position(coords_to_tile(action.get_pos(), self.grid_size))
            state.move_player(self.player_idx, action.get_pos())
        else:
            board.add_wall_graph(action.get_pos(), action.get_dir(), True)
            state.add_wall(self.player_idx, action.get_pos(), action.get_dir())
