import numpy as np

from environment.quoridor_state import QuoridorState

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

    def move_pawn(self, target_position) -> bool:
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
            # Add wall
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

    def act(self, action):
        """If permitted, execute action
        
        Args:
            action (QuoridorAction): action to execute
            
        Returns:
            QuoridorState: resulting state
        """
        if action.type == 0:
            self.move_pawn(action.player_pos)
        else:
            self.add_wall(action.wall_position, action.wall_direction)
        return self.state

    def player_win(self, player_idx: int) -> bool:
        """Checks whether the provided player has won or not

        Args:
            player_idx (int): index of the player

        Returns:
            bool: True if the player has won, False otherwise
        """
        return self.state.player_win(player_idx)

    def is_game_over(self) -> bool:
        """Checks whether a player has won or not
        
        Returns:
            bool: True is the game is over, False otherwise
        """
        return self.state.is_game_over()
