*This project has been created as part of the 42 curriculum by ugutierr, cdiaz-to.*

# A-Maze-ing

## Description

**A-Maze-ing** is a maze generation and visualization project developed as part of the 42 curriculum.

The goal of the project is to generate mazes according to a configurable set of parameters, save the generated maze and its solution to an output file, and display it through an interactive graphical interface using MiniLibX.

The project is divided into two main responsibilities:

- **Maze generation and configuration**

  - Configuration file parsing and validation.
  - Maze data structures.
  - Maze generation algorithms.
  - Perfect and non-perfect maze generation.
  - 42 logo generation inside the maze.
  - Shortest-path calculation.
  - Output file generation.

- **Rendering and interaction**

  - MiniLibX window management.
  - Maze rendering using XPM assets.
  - Maze information panel.
  - Dog animations.
  - Shortest-path visualization.
  - Multiple visual themes.
  - Interactive maze regeneration.

The application is launched with a configuration file:

```bash
uv run python3 a_maze_ing.py config.txt
```

The program reads the configuration, validates it, generates the maze, writes the requested output file and opens the graphical interface.

The main entry point performs the complete pipeline: configuration loading, maze creation, generation, output generation and window initialization.

---

## Features

- Configurable maze width and height.
- Configurable entrance and exit.
- Reproducible generation through an optional seed.
- Perfect mazes.
- Non-perfect "Pacman-like" mazes.
- DFS maze generation.
- Randomized Prim maze generation.
- Pacman-style maze generation.
- Centered `42` pattern.
- Shortest-path calculation using Breadth-First Search.
- Hexadecimal bitmap output.
- Interactive graphical visualization.
- Automatic dog animation following the shortest path.
- Exit animation.
- Animated information-panel dog.
- Four visual themes:
  - Classic
  - Fire
  - Ocean
  - Cyber
- Maze regeneration from the graphical interface.
- Optional shortest-path display.

The available generator types are `DFS`, `PRIM` and `PACMAN`.

---

## Requirements

The project uses:

- Python **3.13 or newer**.
- [uv](https://docs.astral.sh/uv/) for dependency and environment management.
- MiniLibX through the provided local wheel.
- Pydantic for configuration validation.
- python-dotenv for reading configuration files.

The Python project metadata requires Python `>=3.13` and declares `mlx`, `pydantic` and `python-dotenv` as dependencies. The MiniLibX dependency is supplied locally in `lib/`.

---

## Instructions

### 1. Install the dependencies

Make sure Python 3.13+ and `uv` are installed.

From the project root:

```bash
uv sync
```

This creates/synchronizes the project's virtual environment using `pyproject.toml` and `uv.lock`.

Development dependencies include:

- `pytest`
- `flake8`
- `mypy`



### 2. Create a configuration file

Copy the example configuration:

```bash
cp config.example.txt config.txt
```

Then edit `config.txt` according to the desired maze.

Example:

```text
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=
ALGORITHM=
```

The provided example uses a 20×15 maze, with `(0,0)` as the entrance and `(19,14)` as the exit.

### 3. Run the project

```bash
uv run python3 a_maze_ing.py config.txt
```

The program expects exactly one command-line argument: the configuration file.

The generated maze is written to the file specified by `OUTPUT_FILE`. The output contains:

1. The hexadecimal maze bitmap.
2. The entrance coordinates.
3. The exit coordinates.
4. The shortest path.



---

## Configuration File

The configuration file follows a `.env`/dotenv-style format using `KEY=VALUE` entries.

### Complete format

```text
WIDTH=<integer>
HEIGHT=<integer>
ENTRY=<x>,<y>
EXIT=<x>,<y>
OUTPUT_FILE=<path>
PERFECT=<True|False>
SEED=<string>
ALGORITHM=<DFS|PRIM|PACMAN>
```

### Parameters

| Parameter     | Required | Description                                                |
| ------------- | -------- | ---------------------------------------------------------- |
| `WIDTH`       | Yes      | Maze width. Valid range: `11`–`1000`.                      |
| `HEIGHT`      | Yes      | Maze height. Valid range: `9`–`1000`.                      |
| `ENTRY`       | Yes      | Entrance coordinates in `x,y` format.                      |
| `EXIT`        | Yes      | Exit coordinates in `x,y` format.                          |
| `OUTPUT_FILE` | Yes      | File where the generated maze and solution are written.    |
| `PERFECT`     | Yes      | `True` for a perfect maze, `False` for a non-perfect maze. |
| `SEED`        | No       | Optional seed for reproducible generation.                 |
| `ALGORITHM`   | No       | `DFS`, `PRIM` or `PACMAN`.                                 |

These are the complete required and optional configuration keys implemented by the parser.

### Configuration rules

`ENTRY` and `EXIT`:

- Must be inside the maze.
- Cannot refer to the same cell.
- Coordinates are zero-based.

The parser also normalizes `ALGORITHM` to uppercase, and an empty algorithm is treated as unspecified.

If `ALGORITHM` is omitted:

- `PERFECT=True` → `DFS` is selected.
- `PERFECT=False` → `PACMAN` is selected.

`PACMAN` is only valid for non-perfect mazes, while `DFS` and `PRIM` are used for perfect mazes.

### Example: perfect maze

```text
WIDTH=40
HEIGHT=30
ENTRY=0,0
EXIT=39,29
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=DFS
```

### Example: non-perfect maze

```text
WIDTH=40
HEIGHT=30
ENTRY=0,0
EXIT=39,29
OUTPUT_FILE=maze.txt
PERFECT=False
SEED=42
ALGORITHM=PACMAN
```

---

## Maze Generation Algorithm

### Primary algorithm: Randomized Depth-First Search

The main algorithm chosen for perfect maze generation is **randomized Depth-First Search (DFS)**, also known as the recursive-backtracking approach.

The implementation uses an explicit stack rather than Python recursion:

1. Select a random starting cell.
2. Mark it as visited.
3. Add it to a stack.
4. Look for unvisited neighboring cells.
5. Randomly select one of them.
6. Remove the wall between the current cell and the selected neighbor.
7. Push the neighbor onto the stack.
8. If no unvisited neighbor is available, backtrack by popping the stack.
9. Continue until the stack is empty.

The implementation explicitly uses a stack and randomly chooses among available neighbors. Cells belonging to the `42` pattern are excluded from the generation process.

### Why DFS?

DFS was chosen as the main algorithm because it fits the requirements of a **perfect maze** particularly well:

- It naturally creates a connected maze.
- It produces a maze without cycles.
- Every reachable cell has a unique path from every other reachable cell.
- The implementation is relatively simple to understand and maintain.
- An explicit stack avoids recursion-depth problems for large mazes.
- Random neighbor selection provides different mazes when different seeds are used.

The algorithm is also easy to integrate with the project's `Cell`/`Maze` representation because generation consists primarily of selecting neighboring cells and removing the wall between them.

### Other implemented algorithms

The project also contains a randomized **Prim** implementation for perfect mazes. It maintains a collection of candidate connections between visited and unvisited cells and randomly selects connections until the maze is complete.

For non-perfect mazes, the project implements a **Pacman-like algorithm**. It first generates a DFS maze and then opens additional corridors, including mandatory perimeter/central corridors and selected dead ends. This creates additional paths and therefore a non-perfect maze.

---

## The 42 Pattern

The generated maze contains a centered `42` pattern.

The pattern is represented internally as:

```text
#...###
#.....#
###.###
..#.#..
..#.###
```

It is centered according to the maze dimensions and the cells belonging to the pattern are marked so that the generation algorithms do not use them as normal maze cells.

The generator checks that the maze is large enough to contain the pattern before generation starts.

---

## Maze Representation and Solution

Each maze cell stores its four walls:

- North
- East
- South
- West

The four walls are encoded as a four-bit mask:

```text
North = 1
East  = 2
South = 4
West  = 8
```

This allows every cell to be represented by a single hexadecimal digit in the output bitmap.

For example, the maze can be exported as rows of hexadecimal characters, where each character represents the wall configuration of one cell.

### Shortest path

The shortest path from the entrance to the exit is calculated independently from maze generation using **Breadth-First Search (BFS)**.

BFS keeps track of each cell's parent and reconstructs the path once the exit has been reached. The resulting path is represented using:

```text
N E S W
```



This separation between generation and solving makes the maze data structure reusable: the same `Maze` object can be generated, solved, exported and rendered without coupling these responsibilities together.

---

## Rendering and Interaction

The graphical interface is implemented with MiniLibX.

The renderer manages:

- Window creation.
- Maze layout and scaling.
- Textures and XPM assets.
- Maze walls and floor.
- Entrance and exit.
- The 42 pattern.
- Information panel.
- Dog sprites.
- Animations.
- Keyboard events.



### Keyboard controls

| Key   | Action                           |
| ----- | -------------------------------- |
| `ESC` | Close the application            |
| `R`   | Regenerate the maze              |
| `P`   | Toggle the shortest-path display |
| `C`   | Change visual theme              |
| `A`   | Start/restart the maze animation |

These key bindings are defined directly in the `Window` class.

### Themes

Four themes are available:

- **Classic**
- **Fire**
- **Ocean**
- **Cyber**

The themes can change the floor, walls, 42 logo, border and side-panel appearance.

### Animations

The maze includes a dog that follows the calculated shortest path from the entrance to the exit.

The animation maintains its own state, including:

- Current dog position.
- Direction.
- Path index.
- Trail.
- Exit animation frame.
- Panel animation state.



When the dog reaches the exit, the exit animation is triggered and the panel dog starts its end sequence.

---

## Reusable Code

One of the main design goals was to keep the maze-generation logic independent from the graphical interface.

### `src/mazegen/maze.py`

The `Maze` and `Cell` classes provide reusable operations for:

- Representing cells.
- Representing walls.
- Finding neighboring cells.
- Removing walls.
- Exporting the maze bitmap.
- Solving the maze.

This module does not depend on the renderer.

### `src/mazegen/maze_generator.py`

`MazeGenerator` provides a reusable generation interface:

```python
generator = MazeGenerator(
    seed=seed,
    perfect=perfect,
    algorithm=algorithm,
)

generator.generate(maze)
```

The generator can therefore be reused by another interface or application without changing the underlying maze representation.

The algorithms are isolated into individual methods, making it possible to add another generation algorithm without redesigning the `Maze` class.

### `src/config.py`

The configuration model is reusable because parsing, normalization and validation are separated from the application entry point. Pydantic is used to validate the resulting configuration.

### `src/render/`

The rendering code is also separated from generation. The `Window` receives a `Maze`, a `MazeGenerator` and a validated configuration rather than being responsible for creating or parsing them.

This separation allows the generation package to be reused independently of the MiniLibX interface.

---

## Team and Project Management

### Team

| Team member  | Role                            | Main responsibilities                                                                                                        |
| ------------ | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **ugutierr** | Maze generation & configuration | Maze data model, generation algorithms, 42 pattern, configuration parsing and validation, maze solving and output generation |
| **cdiaz-to** | Rendering & UI                  | MiniLibX window, graphical rendering, textures, framebuffer, bitmap font, animations, themes and user interaction            |

The division of responsibilities follows the architecture of the project: generation/configuration is separated from rendering, with the two parts communicating through the `Maze`, `MazeGenerator` and `Config` objects.

### Planning

The initial plan was to split the project into two major areas:

1. Implement the maze engine and all configuration-related functionality.
2. Implement the graphical interface on top of the generated maze.

This division allowed both members to work mostly independently and reduced the amount of code that needed to be changed simultaneously.

The final project evolved beyond the basic requirements by adding:

- Multiple generation algorithms.
- A non-perfect Pacman-like mode.
- Shortest-path visualization.
- Dog animations.
- Multiple themes.
- A reusable framebuffer abstraction.
- A bitmap font rendered directly into the frame.

### What worked well

- The separation between maze generation and rendering reduced coupling.
- The `Maze` class provides a common interface between the generator and renderer.
- Configuration validation catches invalid parameters before generation begins.
- Using a seed makes maze generation reproducible.
- The renderer can regenerate a maze without having to recreate the entire application.
- The use of an off-screen framebuffer allows the renderer to compose a complete frame before displaying it, reducing flickering.

### What could be improved

Potential improvements for a future iteration include:

- Increasing automated test coverage for the generation algorithms and renderer.
- Adding dedicated tests for maze connectivity and perfect-maze properties.
- Improving documentation of the internal rendering architecture.
- Making the set of rendering themes configurable rather than hard-coded.
- Adding a clearer abstraction for generation algorithms if more algorithms are added in the future.
- Improving the separation between application-level logging and library-level logging.

---

## Tools

The project uses the following tools and technologies:

- **Python 3.13+** — main programming language.
- **MiniLibX** — graphical window and rendering.
- **uv** — Python environment and dependency management.
- **Pydantic** — configuration validation.
- **python-dotenv** — configuration file parsing.
- **pytest** — automated testing.
- **mypy** — static type checking.
- **flake8** — code quality and style checks.
- **Git** — version control and team collaboration.

The development dependencies and project dependencies are declared in `pyproject.toml`.

---

## AI Usage

AI was used as a **development and documentation assistant**, not as a replacement for understanding or implementing the project.

For this project documentation, ChatGPT was used to:

- Review the existing project structure and source files.
- Help organize the README according to the 42 project requirements.
- Explain and document the implemented maze-generation algorithms.
- Document the configuration format and validation rules.
- Organize the description of the team's responsibilities.
- Improve the clarity and structure of the technical documentation.

The implementation itself should be considered the team's work. In particular, the maze generation and configuration/parsing work was developed by **ugutierr**, while the rendering and graphical interface were developed by **cdiaz-to**.

---

## Resources

### Maze generation

- [Wikipedia — Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Wikipedia — Depth-first search](https://en.wikipedia.org/wiki/Depth-first_search)
- [Wikipedia — Prim's algorithm](https://en.wikipedia.org/wiki/Prim%27s_algorithm)
- [Wikipedia — Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)

These references are useful for understanding the algorithms used by the maze generator and the BFS-based shortest-path solver.

### MiniLibX

- 42 MiniLibX documentation and guides available through the 42 curriculum resources.
- MiniLibX source and documentation provided with the project environment.

### Python

- [Python Documentation](https://docs.python.org/3/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [uv Documentation](https://docs.astral.sh/uv/)
- [pytest Documentation](https://docs.pytest.org/)

### Bitmap font

The project includes a small bitmap font generated from **DejaVu Sans Mono Bold**. The source code documents the font and its license directly.

---

## License

This project is distributed under the **MIT License**.

Copyright © 2026 **ugutierr** and **cdiaz-to**.

