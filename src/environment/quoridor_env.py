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

    def __init__(self, grid_size=9) -> None:
        super().__init__()

        # create a Quoridor state
        self.grid_size = grid_size
        self.state = QuoridorState(self.grid_size)
        self.current_player = 0
        self.done = False

    def move_pawn(self, target_position) -> bool:
        if self.state.can_move_player(self.current_player, target_position):
            # Move player
            self.state.move_player(self.current_player, target_position)
            # Test winning move
            self.done = self.state.player_win(self.current_player)
            # Update current player
            self.current_player = (self.current_player + 1) % NB_PLAYERS

        else:
            print(
                f"QuoridorEnv: cannot move player {self.current_player} to target position {target_position}"
            )

    def add_wall(self, target_position, direction: int) -> bool:
        if self.state.can_place_wall(self.current_player, target_position,
                                     direction):
            # Move player
            self.state.place_wall(self.current_player, target_position,
                                  direction)
            # Test winning move
            self.done = self.state.player_win(self.current_player)
            # Update current player
            self.current_player = (self.current_player + 1) % NB_PLAYERS

        else:
            print(
                f"QuoridorEnv: cannot place wall for player {self.current_player} to target position {target_position} and direction {direction}"
            )
