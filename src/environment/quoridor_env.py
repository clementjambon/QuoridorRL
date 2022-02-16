import numpy as np

from environment.quoridor_state import QuoridorState

# ----------------------------
# ENVIRONMENT VARIABLES
# ----------------------------

GRID_SIZE = 9
NB_PLAYERS = 2


# ----------------------------
# ENVIRONMENT CLASS
# ----------------------------
class QuoridorEnv:

    def __init__(self) -> None:
        super().__init__()

        # create a Quoridor state
        self.state = QuoridorState(GRID_SIZE)
        self.current_player = 0
        self.done = False

    # Return the value of done after taking action
    def move_pawn(self, target_position):
        if self.state.can_move_player(self.current_player, target_position):
            # Move player
            self.state.move_player(self.current_player, target_position)
            # Test winning move
            self.done = self.state.player_win(self.current_player)
            # Update current player
            self.current_player = (self.current_player + 1) % NB_PLAYERS

            return self.done
        else:
            print(
                f"QuoridorEnv: cannot move player {self.current_player} to target position {target_position}"
            )

    # Return the value of done after taking action
    def add_wall(self, target_position, direction: int):
        if self.state.can_place_wall(self.current_player, target_position,
                                     direction):
            # Move player
            self.state.place_wall(self.current_player, target_position,
                                  direction)
            # Test winning move
            self.done = self.state.player_win(self.current_player)
            # Update current player
            self.current_player = (self.current_player + 1) % NB_PLAYERS

            return self.done
        else:
            print(
                f"QuoridorEnv: cannot place wall for player {self.current_player} to target position {target_position} and direction {direction}"
            )
