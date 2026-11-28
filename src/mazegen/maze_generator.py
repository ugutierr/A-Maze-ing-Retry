"""Provide maze generation algorithms and their configuration types."""

import random
from enum import Enum

from mazegen.maze import Cell, Maze


class AlgorithmType(str, Enum):
    """Represent the maze generation algorithms supported."""

    DFS = "DFS"
    PRIM = "PRIM"
    PACMAN = "PACMAN"


class MazeGenerator:
    """Generate mazes using configurable generation algorithms."""

    def __init__(
        self, seed: None | str, perfect: bool, algorithm: AlgorithmType
    ) -> None:
        """Initialize a maze generator.

        Args:
            seed: Optional seed used to initialize the random number
                generator.
            perfect: Whether the generated maze must be a perfect maze.
            algorithm: Algorithm to use for maze generation.
        """
        self.seed = seed
        self.perfect = perfect
        self.algorithm = algorithm

    def generate(self, maze: Maze) -> None:
        """Generate a maze using the configured algorithm.

        The random number generator is initialized with the configured
        seed before generation starts. The selected algorithm must be
        compatible with the requested maze type.

        Args:
            maze: Maze instance to generate.

        Raises:
            ValueError: If the configured algorithm is incompatible with
                the requested maze type or if the maze is too small for
                the required 42 pattern.
        """
        maze.reset_maze()
        random.seed(self.seed)
        try:
            self._gen_42logo(maze)
        except ValueError as e:
            maze.warnings.append(str(e))
        match (self.perfect, self.algorithm):
            case (True, AlgorithmType.DFS):
                self._dfs_generator(maze)
            case (True, AlgorithmType.PRIM):
                self._prim_generator(maze)
            case (False, AlgorithmType.PACMAN):
                self._pacman_generator(maze)
            case _:
                raise ValueError(
                    f"Algorithm {self.algorithm} cannot generate a "
                    f"{'perfect' if self.perfect else 'non-perfect'} maze"
                )

    def _gen_42logo(self, maze: Maze) -> None:
        """Mark the cells occupied by the centered 42 pattern.

        The pattern is centered in the maze and marked using the
        ``logo42`` attribute of each affected cell. The center cell
        itself is excluded from the pattern.

        Args:
            maze: Maze in which the 42 pattern is placed.

        Raises:
            ValueError: If the maze is too small to contain the pattern.
        """
        pattern: tuple[str, ...] = (
            "#...###",
            "#.....#",
            "###.###",
            "..#.#..",
            "..#.###",
        )

        pattern_height: int = len(pattern)
        pattern_width: int = len(pattern[0])

        center_x: int = maze.width // 2
        center_y: int = maze.height // 2

        start_x: int = center_x - pattern_width // 2
        start_y: int = center_y - pattern_height // 2

        if (
            start_x < 0
            or start_y < 0
            or start_x + pattern_width > maze.width
            or start_y + pattern_height > maze.height
            or maze.height < 7
            or maze.width < 9
        ):
            raise ValueError("Maze is too small to display the 42 pattern.")

        for pattern_row, line in enumerate(pattern):
            for pattern_column, value in enumerate(line):
                if value != "#":
                    continue

                column: int = start_x + pattern_column
                row: int = start_y + pattern_row

                if column == center_x and row == center_y:
                    continue

                maze.grid[row][column].logo42 = True

    def _dfs_generator(self, maze: Maze) -> None:
        """Generate a perfect maze using depth-first search.

        A randomized depth-first search is used to remove walls while
        avoiding cells marked as part of the 42 pattern.
        """
        start = random.choice(
            [c for row in maze.grid for c in row if not c.logo42]
        )
        start.visited = True
        stack = [start]
        while stack:
            nbrs = [
                cell
                for cell in maze.neighbors(stack[-1])
                if cell is not None and not cell.visited and not cell.logo42
            ]
            if not nbrs:
                stack.pop()
            else:
                next = random.choice(nbrs)
                next.visited = True
                maze.remove_wall(stack[-1], next)
                stack.append(next)
        for row in maze.grid:
            for cell in row:
                cell.visited = False

    def _prim_generator(self, maze: Maze) -> None:
        """Generate a perfect maze using a randomized Prim's algorithm.

        The algorithm maintains a collection of candidate connections
        between visited and unvisited cells and randomly selects from
        those connections while avoiding the 42 pattern.
        """
        start = random.choice(
            [c for row in maze.grid for c in row if not c.logo42]
        )
        start.visited = True
        stack = [
            (cell, start)
            for cell in maze.neighbors(start)
            if cell is not None and not cell.visited and not cell.logo42
        ]
        while stack:
            next = random.choice(stack)
            next[0].visited = True
            maze.remove_wall(*next)
            stack += [
                (cell, next[0])
                for cell in maze.neighbors(next[0])
                if cell is not None
            ]
            stack = [
                tup
                for tup in stack
                if not tup[0].visited and not tup[0].logo42
            ]
        for row in maze.grid:
            for cell in row:
                cell.visited = False

    def _pacman_generator(self, maze: Maze) -> None:
        """Generate a non-perfect maze with additional open corridors.

        The maze is first generated using depth-first search. Mandatory
        corridors are then opened around the maze perimeter and center.
        Finally, selected dead ends are opened to produce a less
        constrained, non-perfect maze while preserving the 42 pattern.
        """
        self._dfs_generator(maze)
        x = maze.width // 2
        y = maze.height // 2
        mandatory_corridors: list[tuple[Cell, Cell]] = [
            (maze.grid[0][0], maze.grid[0][1]),
            (maze.grid[0][0], maze.grid[1][0]),
            (maze.grid[maze.height - 1][0], maze.grid[maze.height - 2][0]),
            (maze.grid[maze.height - 1][0], maze.grid[maze.height - 1][1]),
            (
                maze.grid[maze.height - 1][maze.width - 1],
                maze.grid[maze.height - 2][maze.width - 1],
            ),
            (
                maze.grid[maze.height - 1][maze.width - 1],
                maze.grid[maze.height - 1][maze.width - 2],
            ),
            (maze.grid[0][maze.width - 1], maze.grid[0][maze.width - 2]),
            (maze.grid[0][maze.width - 1], maze.grid[1][maze.width - 1]),
            (maze.grid[y][x], maze.grid[y + 1][x]),
            (maze.grid[y][x], maze.grid[y - 1][x]),
        ]
        for cell1, cell2 in mandatory_corridors:
            maze.remove_wall(cell1, cell2)
        dead_ends = [
            cell
            for row in maze.grid
            for cell in row
            if not cell.logo42 and cell.degree() == 1
        ]
        while dead_ends:
            dead_end = random.choice(dead_ends)
            nbrs = [
                cell
                for i, cell in enumerate(maze.neighbors(dead_end))
                if cell is not None
                and not cell.logo42
                and dead_end.get_bit() & 1 << i
            ]
            if nbrs:
                maze.remove_wall(dead_end, random.choice(nbrs))
            dead_ends.remove(dead_end)
