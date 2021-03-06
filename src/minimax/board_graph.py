import numpy as np
import heapq as heap
from queue import PriorityQueue
from collections import defaultdict
from utils import tile_to_coords, coords_to_tile


class AdjNode:

    def __init__(self, value):
        self.vertex = value
        self.next = None

    def to_string(self) -> str:
        return self.vertex

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
        #reshape walls because walls.shape is missing a dim to rpz all board tiles
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
        self, starting_node: int
    ):  #https://levelup.gitconnected.com/dijkstra-algorithm-in-python-8f0e75e3f16e
        visited = set()
        parents_map = {}
        pq = []
        node_costs = defaultdict(lambda: float('inf'))
        node_costs[starting_node] = 0
        heap.heappush(pq, (0, starting_node))
        while pq:
            # go greedily by always extending the shorter cost nodes first
            _, node = heap.heappop(pq)
            visited.add(node)
            #for adjNode in G[node].items():
            for adjNode in self.get_adj_list(node):
                adjNode = adjNode.vertex
                if adjNode in visited: continue

                newCost = node_costs[node] + 1
                if node_costs[adjNode] > newCost:
                    parents_map[adjNode] = node
                    node_costs[adjNode] = newCost
                    heap.heappush(pq, (newCost, adjNode))

        return parents_map, node_costs

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
