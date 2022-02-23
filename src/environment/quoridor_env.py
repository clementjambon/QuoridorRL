import numpy as np
from environment import QuoridorState, MoveAction, QuoridorAction, WallAction, QuoridorConfig

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


class QuoridorEnv:

    def __init__(self, game_config: QuoridorConfig) -> None:
        """ Initializes a Quoridor game state

        Args:
            grid_size (int, optional): the size of the grid. Defaults to 9.
            max_walls (int, optional): the maximum number of walls a user can use. Defaults to 10.
        """
        # Set game rule variables
        self.grid_size = game_config.grid_size
        self.nb_players = 2
        self.max_walls = game_config.max_walls  # the maximum number of walls per player
        self.max_t = game_config.max_t  # the maximum number of actions before the game can be considered to a "draw"
        # player x_targets (TODO: change this to handle more players)
        self.x_targets = [self.grid_size - 1, 0]

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

    def step_from_index(self, state: QuoridorState,
                        action_idx: int) -> QuoridorState:
        # Map action from its index
        if action_idx < 0:
            print("Invalid action!")
            return

        # Move pawn action
        if action_idx < self.grid_size * self.grid_size:
            target_pos = (action_idx // self.grid_size,
                          action_idx % self.grid_size)
            # TODO: remove this in production (should not be triggered)
            if not self.can_move_pawn(state.current_player, target_pos):
                print("Cannot move player at this position!")
                return

            next_state = self.move_pawn(state.current_player, target_pos)
        # Add wall
        else:
            wall_idx = action_idx - self.grid_size * self.grid_size
            wall_direction = 0
            # Vertical wall
            if wall_idx >= (self.grid_size - 1) * (self.grid_size - 1):
                wall_direction = 1
                wall_idx -= (self.grid_size - 1) * (self.grid_size - 1)
            wall_position = (wall_idx // (self.grid_size - 1),
                             wall_idx % (self.grid_size - 1))

            # TODO: remove this in production (should not be triggered)
            if not self.can_add_wall(state.current_player, wall_position,
                                     wall_direction):
                print(
                    "Cannot add wall at this position and with this direction")
                return

            next_state = self.add_wall(state.current_player, wall_position,
                                       wall_direction)

        return next_state

    def can_move_pawn(self, state: QuoridorState,
                      target_position: tuple[int, int]) -> bool:
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

        player_idx = state.current_player

        # Make sure the other player is not standing at the target_position
        if target_position == state.player_positions[self.get_opponent(
                player_idx)]:
            return False
        player_pos = state.player_positions[player_idx]

        # Check direct moves
        for pos_offset, wall_offsets, wall_direction in DIRECT_OFFSETS:
            if target_position == add_offset(player_pos, pos_offset):
                for wall_offset in wall_offsets:
                    wall_position = add_offset(player_pos, wall_offset)
                    if is_in_bound(
                            wall_position, self.grid_size - 1
                    ) and state.walls[wall_position] == wall_direction:
                        return False
                return True

        # Check moves with hopping
        for pos_offset, opponent_offset, required_wall_offsets, forbidden_wall_offsets in INDIRECT_OFFSETS:
            if target_position == add_offset(
                    state.player_positions[player_idx],
                    pos_offset) and state.player_positions[self.get_opponent(
                        player_idx)] == add_offset(
                            state.player_positions[player_idx],
                            opponent_offset):

                found_required_wall = False
                one_in_bound = False
                for required_wall_offset, required_wall_direction in required_wall_offsets:
                    wall_position = add_offset(player_pos,
                                               required_wall_offset)

                    if is_in_bound(wall_position, self.grid_size - 1):
                        one_in_bound = True
                        if state.walls[
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
                            wall_position, self.grid_size - 1) and state.walls[
                                wall_position] == forbidden_wall_direction:
                        return False

                return True

        return False

    def move_pawn(self, state: QuoridorState,
                  target_position: tuple[int, int]) -> QuoridorState:
        """Moves a player in a provided position

        Args:
            player_idx (int): index of the player
            target_position (_type_): targeted position
        """
        player_idx = state.current_player
        state.player_positions[player_idx] = target_position
        state.current_player = self.get_opponent(player_idx)
        state.t += 1
        state.done = self.player_win(state,
                                     player_idx) or state.t >= self.max_t
        return state

    def player_win(self, state: QuoridorState, player_idx: int) -> bool:
        """Checks whether the provided player has won or not

        Args:
            player_idx (int): index of the player

        Returns:
            bool: True if the player has won, False otherwise
        """
        player_won = (state.player_positions[player_idx][0] ==
                      self.x_targets[player_idx])
        # If the corresponding player won, set the winner to its index
        state.winner = player_idx
        return player_won

    def can_add_wall(self, state: QuoridorState,
                     wall_position: tuple[int, int], direction: int) -> bool:
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

        player_idx = state.current_player
        # Make sure the player has not used all of its walls yet
        if state.nb_walls[player_idx] >= self.max_walls:
            return
        # Make sure the intersection is not already used by a wall
        if state.walls[wall_position] != -1:
            return False

        # Check potential intersections
        if direction == 0:
            # One cannot place walls if there is already a wall of the same direction in the axis-aligned adjacent intersections
            if wall_position[0] > 0 and state.walls[(wall_position[0] - 1,
                                                     wall_position[1])] == 0:
                return False
            if wall_position[0] < self.grid_size - 2 and state.walls[(
                    wall_position[0] + 1, wall_position[1])] == 0:
                return False
        if direction == 1:
            # One cannot place walls if there is already a wall of the same direction in the axis-aligned adjacent intersections
            if wall_position[1] > 0 and state.walls[(
                    wall_position[0], wall_position[1] - 1)] == 1:
                return False
            if wall_position[1] < self.grid_size - 2 and state.walls[(
                    wall_position[0], wall_position[1] + 1)] == 0:
                return False

        # Test pathfinding i.e make sure he cannot block the opponent from reaching its goal (in practice, he can block himself)
        state.walls[wall_position] = direction
        for i in range(self.nb_players):
            if not self.pathfinder.check_path(
                    state.walls, state.player_positions[i], self.x_targets[i]):
                self.walls[wall_position] = -1
                return False
        state.walls[wall_position] = -1

        return True

    def add_wall(self, state: QuoridorState, wall_position: tuple[int, int],
                 direction: int) -> QuoridorState:
        """Adds a wall requested by a specific player

        Args:
            player_idx (int): index of the player
            wall_position (_type_): position of the wall
            direction (int): direction of the wall
        """
        player_idx = state.current_player
        state.nb_walls[player_idx] += 1
        state.walls[wall_position] = direction
        state.current_player = self.get_opponent(player_idx)
        state.t += 1
        state.done = self.player_win(state,
                                     player_idx) or state.t >= self.max_t
        return state

    # Returns the set of possible actions that the current player can take
    def get_possible_actions(self,
                             state: QuoridorState) -> list[QuoridorAction]:
        """Returns a list with all the actions the current player can take

        Returns:
            list[QuoridorAction]: list of actions (either MoveAction or WallAction)
        """
        possible_actions = []

        player_pos = state.player_positions[state.current_player]

        # If the player has not used all of its walls, check the walls he can place
        # Note: in practice, this is redundant but it prevents from looping
        if state.nb_walls[state.current_player] < self.max_walls:
            for i in range(self.grid_size - 1):
                for j in range(self.grid_size - 1):
                    for direction in range(2):
                        if self.can_add_wall(state, (i, j), direction):
                            possible_actions.append(
                                WallAction((i, j), direction))

        # Check the move actions the player can perform
        # 1. direct moves
        for pos_offset, wall_offsets, wall_direction in DIRECT_OFFSETS:
            target_position = add_offset(player_pos, pos_offset)
            if is_in_bound(target_position, self.grid_size
                           ) and state.player_positions[self.get_opponent(
                               state.current_player)] != target_position:
                satisfy_walls = True
                for wall_offset in wall_offsets:
                    wall_position = add_offset(player_pos, wall_offset)
                    if is_in_bound(
                            wall_position, self.grid_size - 1
                    ) and state.walls[wall_position] == wall_direction:
                        satisfy_walls = False
                        break
                if satisfy_walls:
                    possible_actions.append(
                        MoveAction(target_position, state.current_player))

        # 1. moves with hopping
        for pos_offset, opponent_offset, required_wall_offsets, forbidden_wall_offsets in INDIRECT_OFFSETS:
            target_position = add_offset(player_pos, pos_offset)
            if is_in_bound(
                    target_position,
                    self.grid_size) and state.player_positions[
                        self.get_opponent(state.current_player)] == add_offset(
                            state.player_positions[state.current_player],
                            opponent_offset):

                found_required_wall = False
                one_in_bound = False
                for required_wall_offset, required_wall_direction in required_wall_offsets:
                    wall_position = add_offset(player_pos,
                                               required_wall_offset)

                    if is_in_bound(wall_position, self.grid_size - 1):
                        one_in_bound = True
                        if state.walls[
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
                            wall_position, self.grid_size - 1) and state.walls[
                                wall_position] == forbidden_wall_direction:
                        satisfy_walls = False
                        break

                if satisfy_walls:
                    possible_actions.append(
                        MoveAction(target_position, state.current_player))

        # Return the full list of actions
        return possible_actions
