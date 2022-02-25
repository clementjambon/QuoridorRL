import numpy as np
from environment.quoridor_action import MoveAction, QuoridorAction, WallAction
import copy

from utils import add_offset, is_in_bound
from utils import PathFinder

# Offsets are defined as (pos_offset, wall_offsets, wall_direction)
DIRECT_OFFSETS = [((-1, 0), [(-1, 0), (-1, -1)], 1),
                  ((1, 0), [(0, 0), (0, -1)], 1),
                  ((0, -1), [(0, -1), (-1, -1)], 0),
                  ((0, 1), [(0, 0), (-1, 0)], 0)]

# Indirect offsets are defined as (pos_offset, opponent_offset, required_wall_offsets, forbidden_wall_offsets)
# # where wall_offset = (wall_pos_offset, wall_direction)
INDIRECT_OFFSETS = [
    # Used for hopping over pawn without blocking wall
    ((-2, 0), (-1, 0), [], [((-2, 0), 1), ((-2, -1), 1)]),
    ((2, 0), (1, 0), [], [((1, 0), 1), ((1, -1), 1)]),
    ((0, -2), (0, -1), [], [((0, -2), 0), ((-1, -2), 0)]),
    ((0, 2), (0, 1), [], [((0, 1), 0), ((-1, 1), 0)]),
    # Used when there is a blocking wall
    ((-1, -1), (-1, 0), [((-2, 0), 1), ((-2, -1), 1)], [((-1, -1), 0),
                                                        ((-1, -1), 1),
                                                        ((-1, 0), 1)]),
    ((-1, -1), (0, -1), [((0, -2), 0), ((-1, -2), 0)], [((-1, -1), 1),
                                                        ((-1, -1), 0),
                                                        ((0, -1), 0)]),
    ((1, -1), (0, -1), [((0, -2), 0), ((-1, -2), 0)], [((-1, -1), 0),
                                                       ((0, -1), 0),
                                                       ((0, -1), 1)]),
    ((1, -1), (1, 0), [((1, 0), 1), ((1, -1), 1)], [
        ((0, -1), 1),
        ((0, 0), 1),
        ((0, -1), 0),
    ]),
    ((1, 1), (1, 0), [((1, 0), 1), ((1, -1), 1)], [((0, -1), 1), ((0, 0), 1),
                                                   ((0, 0), 0)]),
    ((1, 1), (0, 1), [((-1, 1), 0), ((0, 1), 0)], [((-1, 0), 0), ((0, 0), 0),
                                                   ((0, 0), 1)]),
    ((-1, 1), (0, 1), [((-1, 1), 0), ((0, 1), 0)], [((-1, 0), 0), ((0, 0), 0),
                                                    ((-1, 0), 1)]),
    ((-1, 1), (-1, 0), [((-2, 0), 1), ((-2, -1), 1)], [((-1, 0), 0),
                                                       ((-1, -1), 1),
                                                       ((-1, 0), 1)])
]


class QuoridorState:

    def __init__(self, grid_size: int = 9, max_walls: int = 10) -> None:
        """ Initializes a Quoridor game state

        Args:
            grid_size (int, optional): the size of the grid. Defaults to 9.
            max_walls (int, optional): the maximum number of walls a user can use. Defaults to 10.
        """

        self.grid_size = grid_size

        # TODO: "de-hardcode" this! (for a 4 player game)
        self.nb_players = 2
        self.max_walls = max_walls  # the maximum number of walls per player

        # player positions
        self.player_positions = [(0, self.grid_size // 2),
                                 (self.grid_size - 1, self.grid_size // 2)]
        # player x_targets (TODO: change this to handle more players)
        self.x_targets = [self.grid_size - 1, 0]

        # number of already placed walls for a given player
        self.nb_walls = [0, 0]

        # (grid_size - 1)x(grid_size - 1) 2d int8 array to store the wall positions at intersections
        # -1 stands for empty
        # 0 stands for a wall along x
        # 1 stands for a wall along y
        self.walls = np.full((self.grid_size - 1, self.grid_size - 1),
                             -1,
                             dtype=np.int8)

        # initialize the pathfinder used to check valid wall placement
        self.pathfinder = PathFinder(self.grid_size)

    def get_opponent(self, player_idx: int) -> int:
        """Returns the opponent of the provided player

        Args:
            player_idx (int): index of the player

        Returns:
            int: index of its opponent
        """
        return (player_idx + 1) % self.nb_players

    def can_move_player(self, player_idx: int, target_position) -> bool:
        """Checks that a given player can move in a provided position

        Args:
            player_idx (int): index of the player
            target_position (_type_): targeted position

        Returns:
            bool: True if the move is valid, False otherwise
        """
        # Make sure the target position is in bound
        if not is_in_bound(target_position, self.grid_size):
            return False

        # Make sure the other player is not standing at the target_position
        if target_position == self.player_positions[self.get_opponent(
                player_idx)]:
            return False
        player_pos = self.player_positions[player_idx]

        # Check direct moves
        for pos_offset, wall_offsets, wall_direction in DIRECT_OFFSETS:
            if target_position == add_offset(player_pos, pos_offset):
                for wall_offset in wall_offsets:
                    wall_position = add_offset(player_pos, wall_offset)
                    if is_in_bound(
                            wall_position, self.grid_size -
                            1) and self.walls[wall_position] == wall_direction:
                        return False
                return True

        # Check moves with hopping
        for pos_offset, opponent_offset, required_wall_offsets, forbidden_wall_offsets in INDIRECT_OFFSETS:
            if target_position == add_offset(
                    self.player_positions[player_idx],
                    pos_offset) and self.player_positions[self.get_opponent(
                        player_idx)] == add_offset(
                            self.player_positions[player_idx],
                            opponent_offset):

                found_required_wall = False
                one_in_bound = False
                for required_wall_offset, required_wall_direction in required_wall_offsets:
                    wall_position = add_offset(player_pos,
                                               required_wall_offset)

                    if is_in_bound(wall_position, self.grid_size - 1):
                        one_in_bound = True
                        if self.walls[
                                wall_position] == required_wall_direction:
                            found_required_wall = True
                            break
                        else:
                            return False
                if one_in_bound and not found_required_wall:
                    return False

                for forbidden_wall_offset, forbidden_wall_direction in forbidden_wall_offsets:
                    wall_position = add_offset(player_pos,
                                               forbidden_wall_offset)
                    if is_in_bound(
                            wall_position, self.grid_size - 1) and self.walls[
                                wall_position] == forbidden_wall_direction:
                        return False

                return True

        return False

    def move_player(self, player_idx: int, target_position) -> None:
        """Moves a player in a provided position

        Args:
            player_idx (int): index of the player
            target_position (_type_): targeted position
        """
        # print("target: " + str(target_position))
        self.player_positions[player_idx] = target_position
        # print("final position" + str(self.player_positions[player_idx]))

    def player_win(self, player_idx: int) -> bool:
        """Checks whether the provided player has won or not

        Args:
            player_idx (int): index of the player

        Returns:
            bool: True if the player has won, False otherwise
        """
        return (
            self.player_positions[player_idx][0] == self.x_targets[player_idx])

    def is_game_over(self) -> bool:
        """Checks whether a player has won or not
        
        Returns:
            bool: True is the game is over, False otherwise
        """
        over = False
        for i in range(self.nb_players):
            over = over or self.player_win(i)
        return over

    def can_add_wall(self, player_idx: int, wall_position,
                     direction: int) -> bool:
        """Checks that a given player can add a wall

        Args:
            player_idx (int): index of the player
            wall_position (_type_): position of the wall
            direction (int): direction of the wall

        Returns:
            bool: True if the wall can be added, False otherwise
        """
        # Make sure the target position is in bound
        if not is_in_bound(wall_position, self.grid_size - 1):
            return False
        # Make sure the player has not used all of its walls yet
        if self.nb_walls[player_idx] >= self.max_walls:
            return
        # Make sure the intersection is not already used by a wall
        if self.walls[wall_position] != -1:
            return False

        # Check potential intersections
        if direction == 0:
            # One cannot place walls if there is already a wall of the same direction in the axis-aligned adjacent intersections
            if wall_position[0] > 0 and self.walls[(wall_position[0] - 1,
                                                    wall_position[1])] == 0:
                return False
            if wall_position[0] < self.grid_size - 2 and self.walls[(
                    wall_position[0] + 1, wall_position[1])] == 0:
                return False
        if direction == 1:
            # One cannot place walls if there is already a wall of the same direction in the axis-aligned adjacent intersections
            if wall_position[1] > 0 and self.walls[(
                    wall_position[0], wall_position[1] - 1)] == 1:
                return False
            if wall_position[1] < self.grid_size - 2 and self.walls[(
                    wall_position[0], wall_position[1] + 1)] == 0:
                return False

        # Test pathfinding i.e make sure he cannot block the opponent from reaching its goal (in practice, he can block himself)
        self.walls[wall_position] = direction
        for i in range(self.nb_players):
            if not self.pathfinder.check_path(
                    self.walls, self.player_positions[i], self.x_targets[i]):
                self.walls[wall_position] = -1
                return False
        self.walls[wall_position] = -1

        return True

    def add_wall(self, player_idx: int, wall_position, direction: int) -> None:
        """Adds a wall requested by a specific player

        Args:
            player_idx (int): index of the player
            wall_position (_type_): position of the wall
            direction (int): direction of the wall
        """
        self.nb_walls[player_idx] += 1
        self.walls[wall_position] = direction

    # Returns the set of possible actions that the requested player can take
    def get_possible_actions(self, player_idx: int):
        """Returns a list with all the actions a player can take

        Args:
            player_idx (int): index of the player

        Returns:
            list[QuoridorAction]: list of actions (either MoveAction or WallAction)
        """
        # print('get possible actions')
        possible_actions = []

        player_pos = self.player_positions[player_idx]

        # If the player has not used all of its walls, check the walls he can place
        # Note: in practice, this is redundant but it prevents from looping
        if self.nb_walls[player_idx] < self.max_walls:
            for i in range(self.grid_size - 1):
                for j in range(self.grid_size - 1):
                    for direction in range(2):
                        if self.can_add_wall(player_idx, (i, j), direction):
                            possible_actions.append(
                                WallAction((i, j), direction))

        # Check the move actions the player can perform
        # 1. direct moves
        for pos_offset, wall_offsets, wall_direction in DIRECT_OFFSETS:
            target_position = add_offset(player_pos, pos_offset)
            if is_in_bound(
                    target_position, self.grid_size) and self.player_positions[
                        self.get_opponent(player_idx)] != target_position:
                satisfy_walls = True
                for wall_offset in wall_offsets:
                    wall_position = add_offset(player_pos, wall_offset)
                    if is_in_bound(
                            wall_position, self.grid_size -
                            1) and self.walls[wall_position] == wall_direction:
                        satisfy_walls = False
                        break
                if satisfy_walls:
                    possible_actions.append(
                        MoveAction(target_position, player_idx))

        # 1. moves with hopping
        for pos_offset, opponent_offset, required_wall_offsets, forbidden_wall_offsets in INDIRECT_OFFSETS:
            target_position = add_offset(player_pos, pos_offset)
            if is_in_bound(target_position,
                           self.grid_size) and self.player_positions[
                               self.get_opponent(player_idx)] == add_offset(
                                   self.player_positions[player_idx],
                                   opponent_offset):

                found_required_wall = False
                one_in_bound = False
                for required_wall_offset, required_wall_direction in required_wall_offsets:
                    wall_position = add_offset(player_pos,
                                               required_wall_offset)

                    if is_in_bound(wall_position, self.grid_size - 1):
                        one_in_bound = True
                        if self.walls[
                                wall_position] == required_wall_direction:
                            found_required_wall = True
                            break
                        else:
                            break
                if one_in_bound and not found_required_wall:
                    break

                satisfy_walls = True
                for forbidden_wall_offset, forbidden_wall_direction in forbidden_wall_offsets:
                    wall_position = add_offset(player_pos,
                                               forbidden_wall_offset)
                    if is_in_bound(
                            wall_position, self.grid_size - 1) and self.walls[
                                wall_position] == forbidden_wall_direction:
                        satisfy_walls = False
                        break

                if satisfy_walls:
                    possible_actions.append(
                        MoveAction(target_position, player_idx))

        # Return the full list of actions
        return possible_actions

    def act(self, action, player_idx):
        """If permitted, execute action
        
        Args:
            action (QuoridorAction): permitted action to execute
            player_idx (int): player index
            
        Returns:
            QuoridorState: resulting state
        """
        current_state = copy.deepcopy(self)
        if action.type == 0:
            if current_state.can_move_player(player_idx, action.player_pos):
                # Move player
                # print("moving")
                current_state.move_player(player_idx, action.player_pos)
        else:
            if current_state.can_add_wall(player_idx, action.wall_position,
                                          action.wall_direction):
                # Add wall
                current_state.add_wall(player_idx, action.wall_position,
                                       action.wall_direction)
        # print("final position" +
        #       str(current_state.player_positions[player_idx]))
        return current_state
