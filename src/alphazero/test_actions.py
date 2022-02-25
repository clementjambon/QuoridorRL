import sys
import os

# Required to properly append path (this sets the root folder to /src)
sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from environment import MoveAction, WallAction
from utils import change_action_perspective

if __name__ == "__main__":

    grid_size = 5

    # action = MoveAction((1, 1), 0)
    for i in range(grid_size):
        for j in range(grid_size):
            action = MoveAction((i, j), 1)
            action_idx = action.to_index(grid_size=grid_size)
            intermediate_action = action.to_perspective(1, grid_size=grid_size)
            intermediate_idx = intermediate_action.to_index(
                grid_size=grid_size)
            revert_idx = change_action_perspective(1,
                                                   intermediate_idx,
                                                   grid_size=grid_size)
            if action_idx != revert_idx:
                print(i, j, action_idx, intermediate_action.wall_position,
                      intermediate_idx, revert_idx)
