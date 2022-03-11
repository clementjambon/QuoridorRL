class QuoridorConfig:

    def __init__(self,
                 grid_size: int = 9,
                 max_walls: int = 10,
                 max_t: int = 200) -> None:
        self.grid_size = grid_size
        self.max_walls = max_walls
        self.max_t = max_t
        self.nb_actions = self.grid_size * self.grid_size + 2 * (
            self.grid_size - 1) * (self.grid_size - 1)

    def description(self) -> str:
        return f"GameConfig: grid_size={self.grid_size}; max_walls={self.max_walls}; max_t={self.max_t};"
