import numpy as np
from environment import QuoridorState, QuoridorConfig


class QuoridorRepresentation:

    # The current state representation has the following feature planes (repeated time_consitency times)
    # - P0 pawn (2D one-hot encoding)
    # - P1 pawn (2D one-hot encoding)
    # - Wall (where 0 stands for nothing, 1 horizontal wall, 2 vertical wall) (2D padded with 0 on the last column)
    # Additional constant valued planes are
    # - Player colour (0 for P0, 1 for P1)
    # - Number of available walls

    def __init__(self,
                 game_config: QuoridorConfig,
                 time_consistency: int = 8) -> None:
        self.max_walls = game_config.max_walls
        self.grid_size = game_config.grid_size
        self.time_consistency = time_consistency
        # The number of channels is given by the description above
        self.nb_features = 3
        self.nb_constants = 2
        self.nb_channels = self.time_consistency * self.nb_features + self.nb_constants

    # Generates instantaneous planes (i.e without time consistency)
    def generate_instant_planes(self, state: QuoridorState):
        feature_planes = np.zeros((3, self.grid_size, self.grid_size))

        # Set player positions
        for i, pos in enumerate(state.player_positions):
            feature_planes[i, pos[0], pos[1]] = 1.0

        # Set walls
        feature_planes[2, :self.grid_size - 1, :self.grid_size -
                       1] = state.walls + np.ones(
                           (self.grid_size - 1, self.grid_size - 1))

        return feature_planes

    # Generates full set of planes given pre-computed state planes (i.e pads with zero if not enough feature planes and adds constant valued planes)
    def generate_state_planes(self, current_state: QuoridorState,
                              feature_planes: list[np.ndarray]):
        # First, get the most recent feature planes
        nb_recent_features = min(self.time_consistency, len(feature_planes))
        recent_feature_planes = feature_planes[-nb_recent_features]

        state_planes = np.zeros(
            (self.nb_channels, self.grid_size, self.grid_size))

        # If some are missing, they are padded with 0
        count = 0
        for i in range(self.time_consistency - nb_recent_features,
                       self.time_consistency):
            state_planes[i * self.nb_features:(i + 1) *
                         self.nb_features] = recent_feature_planes[count]
            count += 1

        # Add constant-valued features
        # - Player colour
        state_planes[
            self.time_consistency *
            self.nb_features] = current_state.current_player * np.ones(
                (self.grid_size, self.grid_size))
        # - Player number of available walls
        state_planes[self.time_consistency * self.nb_features + 1] = (
            self.max_walls -
            current_state.nb_walls[current_state.current_player]) * np.ones(
                (self.grid_size, self.grid_size))

        # Rotate (180°=2x90°) w.r.t. the current player
        # TODO: check rotation axes!
        return np.rot90(state_planes, k=2, axes=(1, 2))
