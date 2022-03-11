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
            if (walls[wall_1] != 0 if is_in_bound(wall_1, self.grid_size - 1)
                    else True) and (walls[wall_2] != 0 if is_in_bound(
                        wall_2, self.grid_size - 1) else True):
                neighbours.append((pos[0], pos[1] + 1))

        return neighbours

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # TODO: handle mutliple dimensions (i.e remove x_target and add other heuristics)
    def check_path(self, walls, player_pos, x_target) -> bool:
        # Holding the shortest valid paths
        g_scores = float('inf') * np.ones((self.grid_size, self.grid_size))

        open_queue = PriorityQueue()
        open_set = set()
        # Add (s_start, h(s_start)) to the priority queue
        open_queue.put((abs(player_pos[0] - x_target), player_pos))
        open_set.add(player_pos)
        # and 0 g-score at starting position
        g_scores[player_pos] = 0
        while not open_queue.empty():
            _, current_pos = open_queue.get()

            # Get neighbours
            neighbours = self.get_neighbours(walls, current_pos)
            # print(f'{current_pos} - {self.get_neighbours(walls, current_pos)}')
            for neighbour in neighbours:
                # Compute tentative g_score (+1 in manhattan distance)
                tentative_g_score = g_scores[current_pos] + 1
                if tentative_g_score < g_scores[neighbour]:
                    # If the path improves, update it
                    g_scores[neighbour] = tentative_g_score
                    if neighbour[0] == x_target:
                        return True
                    else:
                        if neighbour not in open_set:
                            open_queue.put(
                                (tentative_g_score +
                                 abs(player_pos[0] - x_target), neighbour))
                            open_set.add(neighbour)
        # print(
        #     f"PathFinder: path NOT found from {player_pos} to {x_target} x_target"
        # )
        return False
