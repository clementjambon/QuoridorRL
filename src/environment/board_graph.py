import math
import numpy as np
from queue import PriorityQueue
from collections import defaultdict
import heapq as heap
from utils import tile_to_coords
from utils.coords import coords_to_tile


class AdjNode:

    def __init__(self, value):
        self.vertex = value
        self.next = None

    def to_string(self) -> str:
        return self.vertex

    # always want Node to sort last relative to some other data type:
    def __lt__(self, other):
        return True

    def __gt__(self, other):
        return False


class BoardGraph:

    def __init__(self, walls):
        """
        Represent the board as a graph
        /!\ tile nb ordering by column axis
        0-9- ...-72
        |       .
        1       .
        .
        .       
        8 - ...71-80
        """
        self.grid_size = walls.shape[0] + 1
        self.v = self.grid_size * self.grid_size
        self.graph = [None] * self.v
        #reshape walls to be 9x9
        temp = np.full((self.grid_size, self.grid_size), -1)
        temp[:-1, :-1] = walls
        walls = temp
        #get full graph
        for i in range(self.v):
            coords = tile_to_coords(i, self.grid_size)
            if coords[1] != self.grid_size - 1:  #not last row
                self.add_edge(i, i + 1)
            if coords[1] != 0:  #not first row
                self.add_edge(i, i - 1)
            if coords[0] != 0:  #not first col
                self.add_edge(i, i - self.grid_size)
            if coords[0] != self.grid_size - 1:  #not last col
                self.add_edge(i, i + self.grid_size)
        #remove if there are walls
        for i in range(walls.shape[0]):
            for j in range(walls.shape[0]):
                tile = coords_to_tile((i, j), self.grid_size)
                if walls[i][j] == 0:
                    self.remove_edge(tile, tile + 1)
                    self.remove_edge(tile + self.grid_size,
                                     tile + self.grid_size + 1)
                if walls[i][j] == 1:
                    self.remove_edge(tile, tile + self.grid_size)
                    self.remove_edge(tile + 1, tile + self.grid_size + 1)

    #last arg so that we add edge twice (undirected) if adding it after initialization t(hat does it automatically)
    def add_edge(self, s: int, d: int, initialization: bool = True):
        node = AdjNode(d)
        node.next = self.graph[s]
        self.graph[s] = node  #graph[s] act as the head
        if not initialization:
            node = AdjNode(s)
            node.next = self.graph[d]
            self.graph[d] = node

    def remove_edge(self, s: int, d: int, other_dir: bool = False):
        #print(f'edge {s} - {d}')
        current = self.graph[s]
        prev = current
        while current:
            if (current.vertex == d):
                if (current.vertex == prev.vertex):  #head to remove
                    self.graph[s] = current.next
                    if not other_dir:
                        self.remove_edge(d, s, True)  #remove other direction
                    break
                else:
                    prev.next = current.next
                    if not other_dir:
                        self.remove_edge(d, s, True)  #remove other direction
                    break
            prev = current
            current = current.next

    def get_adj_list(self, vertex: int):
        temp = self.graph[vertex]
        adj_list = []
        while temp:
            adj_list.append(temp)
            temp = temp.next
        return adj_list

    def dijkstra(
        self, startingNode
    ):  #https://levelup.gitconnected.com/dijkstra-algorithm-in-python-8f0e75e3f16e
        visited = set()
        parentsMap = {}
        pq = []
        nodeCosts = defaultdict(lambda: float('inf'))
        nodeCosts[startingNode] = 0
        heap.heappush(pq, (0, startingNode))

        while pq:
            # go greedily by always extending the shorter cost nodes first
            _, node = heap.heappop(pq)
            visited.add(node)

            #for adjNode in G[node].items():
            for adjNode in self.get_adj_list(node):
                adjNode = adjNode.vertex
                if adjNode in visited: continue

                newCost = nodeCosts[node] + 1
                if nodeCosts[adjNode] > newCost:
                    parentsMap[adjNode] = node
                    nodeCosts[adjNode] = newCost
                    heap.heappush(pq, (newCost, adjNode))

        return parentsMap, nodeCosts

    def make_path(self, parent, goal):
        if goal not in parent:
            return None
        v = goal
        path = []
        while v is not None:
            path.append(v)
            if v not in parent: break  # root has null parent
            v = parent[v]
        return path[::-1]

    def print_adj_graph(self):
        for i in range(self.v):
            print("Vertex " + str(i) + ":", end="")
            adjlist = self.get_adj_list(i)
            for node in adjlist:
                print(" -> {}".format(node.to_string()), end="")
            print(" \n")

    def position_feature(self, agent_pos: int) -> int:
        """
        the simplest evaluation features is the number of columns that the pawn is away from his base line column
        if the pawn is on his base line, the value is 0. If the pawn is on the goal line, the value is 8.
        """
        coords = tile_to_coords(agent_pos, self.grid_size)
        return coords[0]  #rows and cols are strangely inversed

    def position_difference(self, max_agent_pos: int,
                            min_agent_pos: int) -> int:
        """
        This feature returns the difference between the position feature
        of the Max player and the position feature of the Min player.
        It actually indicates how good your progress is compared to the opponent’s progress.
        """
        return self.position_feature(max_agent_pos) - self.position_feature(
            min_agent_pos)

    def move_to_next_col_feature(self, agent_pos: int, a_target: int) -> int:
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
        parentsMap, nodeCosts = self.dijkstra(agent_pos)

        if a_target != 0:  #agent0
            next_col = tile_to_coords(agent_pos, self.grid_size)[0] + 1
        else:  #agent1
            next_col = tile_to_coords(agent_pos, self.grid_size)[0] - 1
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
