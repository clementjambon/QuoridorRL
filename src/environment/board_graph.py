import math
from queue import PriorityQueue
from collections import defaultdict
import heapq as heap


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
        0-1- ...-8
        |       .
        9       .
        .
        .       71
        72- ...-80
        """
        self.grid_size = walls.shape[0] + 1
        self.v = self.grid_size * self.grid_size
        self.graph = [None] * self.v
        for i in range(self.v):
            if (i % self.grid_size != self.grid_size - 1):  #not last column
                if (not self.is_there_wall(walls, i, i + 1)):
                    self.add_edge(i, i + 1)
            if (i % self.grid_size != 0):  #not first column
                if (not self.is_there_wall(walls, i, i - 1)):
                    self.add_edge(i, i - 1)
            if (i >= self.grid_size):  #not first row
                if (not self.is_there_wall(walls, i, i - self.grid_size)):
                    self.add_edge(i, i - self.grid_size)
            if (i < self.v - self.grid_size):  #not last row
                if (not self.is_there_wall(walls, i, i + self.grid_size)):
                    self.add_edge(i, i + self.grid_size)

    def is_there_wall(self, walls, u: int, v: int) -> bool:
        #walls is a 8x8 array bc last column and row can't have a wall (row because we place a wall "under the row")
        if (u % self.grid_size >= self.grid_size - 1) or (
                v % self.grid_size >= self.grid_size - 1
        ) or (v >= self.v - self.grid_size) or (u >= self.v - self.grid_size):
            return False
        if (walls[math.floor(u / self.grid_size)][u % self.grid_size] !=
                -1) or (walls[math.floor(
                    v / self.grid_size)][v % self.grid_size] != -1):
            return True
        return False

    #last arg so that we add edge twice (undirected) if adding it after initialization t(hat does it automatically)
    def add_edge(self, s: int, d: int, initialization: bool = True):
        node = AdjNode(d)
        node.next = self.graph[s]
        self.graph[s] = node  #graph[s] act as the head
        if not initialization:
            node = AdjNode(s)
            node.next = self.graph[d]
            self.graph[d] = node

    def remove_edge(self, s: int, d: int):
        current = self.graph[s]
        prev = current
        while current:
            if (current.vertex == d):
                if (current.vertex == prev.vertex):  #head to remove
                    self.graph[s] = current.next
                    self.remove_edge(d, s)  #remove other direction
                    break
                else:
                    prev.next = current.next
                    self.remove_edge(d, s)  #remove other direction
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
