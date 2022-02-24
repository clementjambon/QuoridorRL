import numpy as np
from environment.quoridor_state import QuoridorState


class AdjNode:

    def __init__(self, value):
        self.vertex = value
        self.next = None

    def to_string(self) -> str:
        return self.vertex


class BoardGraph:

    def __init__(self, qState: QuoridorState):
        """
        Represent the board as a graph
        0-1- ...-8
        |       .
        9       .
        .
        .       71
        72- ...-80
        """
        self.grid_size = qState.grid_size
        self.v = self.grid_size * self.grid_size
        self.graph = [None] * self.v
        self.qState = qState
        for i in range(self.v):
            if i % self.grid_size != self.grid_size - 1:  #not last column
                self.add_edge(i, i + 1)
            if i % self.grid_size != 0:  #not first column
                self.add_edge(i, i - 1)
            if i >= self.grid_size:  #not first row
                self.add_edge(i, i - self.grid_size)
            if i < self.v - self.grid_size:  #not last row
                self.add_edge(i, i + self.grid_size)

    #last arg so that we add edge twice (undirected) if adding it after initialization that does it automatically
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

    def print_adj_graph(self):
        for i in range(self.v):
            print("Vertex " + str(i) + ":", end="")
            adjlist = self.get_adj_list(i)
            for node in adjlist:
                print(" -> {}".format(node.to_string()), end="")
            print(" \n")
