"""
You are given a 2-d matrix where each cell consists of either /, \, or an empty space. Write an algorithm that determines into how many regions the slashes divide the space.

For example, suppose the input for a three-by-six grid is the following:

\    /
 \  /
  \/
Considering the edges of the matrix as boundaries, this divides the grid into three triangles, so you should return 3.
"""

class RegionCounter:
    def __init__(self, grid):
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0
        self.grid = grid
        self.visited = set()
        self.expanded_grid = [[0] * (3 * self.cols) for _ in range(3 * self.rows)]
        self._expand_grid()
    
    def _expand_grid(self):
        """Expands each cell into a 3x3 block for better region tracking."""
        for r in range(self.rows):
            for c in range(self.cols):
                base_r, base_c = r * 3, c * 3
                if self.grid[r][c] == '/':
                    self.expanded_grid[base_r][base_c + 2] = 1
                    self.expanded_grid[base_r + 1][base_c + 1] = 1
                    self.expanded_grid[base_r + 2][base_c] = 1
                elif self.grid[r][c] == '\\':
                    self.expanded_grid[base_r][base_c] = 1
                    self.expanded_grid[base_r + 1][base_c + 1] = 1
                    self.expanded_grid[base_r + 2][base_c + 2] = 1
    
    def _dfs(self, r, c):
        """Standard DFS traversal to explore a region."""
        if (r < 0 or c < 0 or r >= 3 * self.rows or c >= 3 * self.cols or 
            self.expanded_grid[r][c] == 1 or (r, c) in self.visited):
            return
        self.visited.add((r, c))
        
        # Move in all 4 directions
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            self._dfs(r + dr, c + dc)
    
    def count_regions(self):
        regions = 0
        for r in range(3 * self.rows):
            for c in range(3 * self.cols):
                if (r, c) not in self.visited and self.expanded_grid[r][c] == 0:
                    self._dfs(r, c)
                    regions += 1
        return regions

# Example usage
grid = [
    "\\    /",
    " \\  / ",
    "  \\/  "
]
counter = RegionCounter(grid)
print(counter.count_regions())  # Expected Output: 3