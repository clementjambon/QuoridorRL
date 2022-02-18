from queue import PriorityQueue
import numpy as np
from utils import is_in_bound


class PathFinder:

    def __init__(self, grid_size: int) -> None:
        self.grid_size = grid_size

    def get_neighbours(self, walls, pos):
        neighbours = []
        # TODO: clean that!
        if pos[0] > 0:
            wall_1 = (pos[0] - 1, pos[1] - 1)
            wall_2 = (pos[0] - 1, pos[1])
            if (walls[wall_1] != 1 if is_in_bound(wall_1, self.grid_size - 1)
                    else True) and (walls[wall_2] != 1 if is_in_bound(
                        wall_2, self.grid_size - 1) else True):
                neighbours.append((pos[0] - 1, pos[1]))

        if pos[1] > 0:
            wall_1 = (pos[0] - 1, pos[1] - 1)
            wall_2 = (pos[0], pos[1] - 1)
            if (walls[wall_1] != 0 if is_in_bound(wall_1, self.grid_size - 1)
                    else True) and (walls[wall_2] != 0 if is_in_bound(
                        wall_2, self.grid_size - 1) else True):
                neighbours.append((pos[0], pos[1] - 1))

        if pos[0] < self.grid_size - 1:
            wall_1 = (pos[0], pos[1] - 1)
            wall_2 = (pos[0], pos[1])
            if (walls[wall_1] != 1 if is_in_bound(wall_1, self.grid_size - 1)
                    else True) and (walls[wall_2] != 1 if is_in_bound(
                        wall_2, self.grid_size - 1) else True):
                neighbours.append((pos[0] + 1, pos[1]))

        if pos[1] < self.grid_size - 1:
            wall_1 = (pos[0] - 1, pos[1])
            wall_2 = (pos[0], pos[1])
            print(wall_1)
            print(wall_2)
            if (walls[wall_1] != 0 if is_in_bound(wall_1, self.grid_size - 1)
                    else True) and (walls[wall_2] != 0 if is_in_bound(
                        wall_2, self.grid_size - 1) else True):
                neighbours.append((pos[0], pos[1] + 1))

        return neighbours

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # TODO: handle mutliple dimensions (i.e remove x_target and add other heuristics)
    def check_path(self, walls, player_pos, x_target) -> bool:
        seen = np.zeros((self.grid_size, self.grid_size), dtype=np.uint8)
        unseen = PriorityQueue()
        unseen.put((0, player_pos))
        while not unseen.empty():
            _, current_pos = unseen.get()
            # Mark current_pos as "seen"
            seen[current_pos] = 1
            neighbours = self.get_neighbours(walls, current_pos)
            # print(f'{current_pos} - {self.get_neighbours(walls, current_pos)}')
            for neighbour in neighbours:
                if seen[neighbour] != 1:
                    if neighbour[0] == x_target:
                        print(
                            f"PathFinder: path found from {player_pos} to {neighbour}"
                        )
                        return True
                    else:
                        cost = self.manhattan_distance(
                            player_pos,
                            neighbour) + abs(neighbour[0] - x_target)
                        unseen.put((cost, neighbour))
        print(
            f"PathFinder: path NOT found from {player_pos} to {x_target} x_target"
        )
        return False
