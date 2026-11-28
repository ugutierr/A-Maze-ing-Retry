"""Provide data structures and operations for creating and solving mazes."""

import logging
from collections import deque

logger = logging.getLogger(__name__)


class Cell:
    """Represent a single cell and its walls within a maze."""

    def __init__(self, row: int, column: int) -> None:
        """Initialize a cell at the given row and column.

        Args:
            row: Zero-based row index of the cell.
            column: Zero-based column index of the cell.
        """
        self.row = row
        self.column = column
        self.north = True
        self.east = True
        self.south = True
        self.west = True
        self.visited = False
        self.logo42 = False

    def reset_cell(self) -> None:
        self.north = True
        self.east = True
        self.south = True
        self.west = True
        self.visited = False
        self.logo42 = False

    def get_bit(self) -> int:
        """Return the bitmask representing the cell's four walls.

        The bits are ordered as north, east, south, and west, with
        weights 1, 2, 4, and 8 respectively.
        """
        return self.north * 1 + self.east * 2 + self.south * 4 + self.west * 8

    def degree(self) -> int:
        """Return the number of open passages connected to the cell."""
        bit = self.get_bit()
        return 4 - sum((bit >> i) & 1 for i in range(4))


class Maze:
    """Represent a rectangular maze and its grid of cells."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
    ) -> None:
        """Initialize a maze with the given dimensions and endpoints.

        Args:
            width: Number of columns in the maze.
            height: Number of rows in the maze.
            entry: Zero-based (x, y) coordinates of the maze entrance.
            exit: Zero-based (x, y) coordinates of the maze exit.
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.grid = [
            [Cell(row, col) for col in range(self.width)]
            for row in range(self.height)
        ]
        self.entry_cell = self.grid[self.entry[1]][self.entry[0]]
        self.exit_cell = self.grid[self.exit[1]][self.exit[0]]
        self.theme = "DEFAULT"
        self.show_path = False
        self.warnings: list[str] = []

    def reset_maze(self) -> None:
        for row in self.grid:
            for cell in row:
                cell.reset_cell()
        self.warnings = []

    def get_bitmap(self) -> str:
        """Return the maze as a hexadecimal wall bitmap.

        Each cell is represented by one hexadecimal digit whose four
        least significant bits encode its north, east, south, and west
        walls.
        """
        return "\n".join(
            [
                "".join([format(cell.get_bit(), "x") for cell in row])
                for row in self.grid
            ]
        )

    def shortest_path(self) -> str:
        """Return the shortest path from the entry cell to the exit cell.

        The path is calculated using breadth-first search and returned
        as a string of direction characters: ``N``, ``E``, ``S``, and
        ``W``. Cell visitation state is reset before returning.

        Returns:
            A string containing the directions of the shortest path, or
            an empty string if the exit cannot be reached.
        """
        parent: dict[Cell, tuple[Cell, int]] = {}
        self.entry_cell.visited = True

        queue = deque([self.entry_cell])
        while queue:
            prev = queue.popleft()
            if prev == self.exit_cell:
                break
            for i, c in enumerate(self.neighbors(prev)):
                if c is None or c.visited or prev.get_bit() & (1 << i):
                    continue
                parent[c] = (prev, i)
                c.visited = True
                queue.append(c)
        if not self.exit_cell.visited:
            logger.debug("Shortest path not found")
            for row in self.grid:
                for cell in row:
                    cell.visited = False
            return ""
        current = self.exit_cell
        path = []
        while current is not self.entry_cell:
            prev, direction = parent[current]
            path.append(["N", "E", "S", "W"][direction])
            current = prev
        for row in self.grid:
            for cell in row:
                cell.visited = False

        return "".join(reversed(path))

    def north_cell(self, cell: Cell) -> Cell | None:
        """Return the cell immediately north of the given cell."""
        if cell.row == 0:
            return None
        return self.grid[cell.row - 1][cell.column]

    def south_cell(self, cell: Cell) -> Cell | None:
        """Return the cell immediately south of the given cell."""
        if cell.row == self.height - 1:
            return None
        return self.grid[cell.row + 1][cell.column]

    def west_cell(self, cell: Cell) -> Cell | None:
        """Return the cell immediately west of the given cell."""
        if cell.column == 0:
            return None
        return self.grid[cell.row][cell.column - 1]

    def east_cell(self, cell: Cell) -> Cell | None:
        """Return the cell immediately east of the given cell."""
        if cell.column == self.width - 1:
            return None
        return self.grid[cell.row][cell.column + 1]

    def neighbors(self, cell: Cell) -> list[Cell | None]:
        """Return the four neighboring cells in cardinal order.

        The returned list is ordered north, east, south, and west.
        A value is ``None`` when the cell lies on the corresponding
        maze boundary.
        """
        return [
            self.north_cell(cell),
            self.east_cell(cell),
            self.south_cell(cell),
            self.west_cell(cell),
        ]

    def remove_wall(self, cell1: Cell, cell2: Cell) -> None:
        """Remove the wall separating two neighboring cells.

        Both cells are updated so that the shared wall is removed from
        each side.

        Args:
            cell1: First cell involved in the wall removal.
            cell2: Second cell involved in the wall removal.

        Raises:
            ValueError: If the two cells are not neighboring cells.
        """
        if cell2 == self.north_cell(cell1):
            cell1.north = False
            cell2.south = False
        elif cell2 == self.east_cell(cell1):
            cell1.east = False
            cell2.west = False
        elif cell2 == self.south_cell(cell1):
            cell1.south = False
            cell2.north = False
        elif cell2 == self.west_cell(cell1):
            cell1.west = False
            cell2.east = False
        else:
            raise ValueError(
                "Cannot remove walls between non neighboring cells"
            )
