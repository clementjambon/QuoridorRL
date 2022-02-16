# Basic union-find structure with parents flattening for O(1) queries
class UnionFind:

    def __init__(self, nb_elements: int) -> None:
        self.parents = [i for i in range(nb_elements)]

    def find(self, i) -> int:
        # Perform flattening if necessary
        if self.parents[i] != i:
            self.parents[i] = self.find(self.parents[i])
        return self.parents[i]

    def union(self, i, j) -> None:
        root_i = self.find(i)
        root_j = self.find(j)
        # If they are not already in the same CC, connect them
        if root_i != root_j:
            self.parents[root_j] = root_i
