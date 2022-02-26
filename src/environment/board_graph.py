import math
from queue import PriorityQueue
from collections import defaultdict
import heapq as heap
from utils import tile_to_coords


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
        each player will try to place fences in such a way that his opponent has to
        take as many steps as possible to get to his goal. To achieve this, 
        the fences have to be placed so that the opponent has to move up and down the board.
        This feature calculates the minimum number of steps that have to be taken to reach the next column
        """
        parentsMap, nodeCosts = self.dijkstra(agent_pos)
        #print(nodeCosts)
        if a_target != 0:
            next_col = tile_to_coords(agent_pos, self.grid_size)[0] + 1
        else:
            next_col = tile_to_coords(agent_pos, self.grid_size)[0] - 1
        #get the tiles nb of the column
        vertices_next_col = []
        for i in range(self.grid_size):
            vertices_next_col.append(next_col * self.grid_size + i)
        #find cost  of closest tile in next col
        cost = float('inf')
        for target in vertices_next_col:
            #print(f'target : {target} cost : {nodeCosts[target]}')
            if nodeCosts[target] < cost:
                cost = nodeCosts[target]
        return cost