"""Provide the main entry point for the A-maze-ing application."""

import logging
import sys
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from config import ConfigError, get_config
from maze_renderer import render_interface
from mazegen import Maze, MazeGenerator

Path("logs").mkdir(exist_ok=True)


class NoTracebackFormatter(logging.Formatter):
    """Format log exceptions without displaying their tracebacks."""

    def formatException(self, exc_info: Any) -> str:
        """Return an empty string instead of a formatted exception."""
        return ""


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # change before release

# Terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(
    NoTracebackFormatter("%(levelname)s: %(message)s")
)

# File
file_handler = logging.FileHandler("logs/maze.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s | %(levelname)s: %(message)s | %(filename)s:%(lineno)d"
    )
)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


def gen_output_file(name: str, maze: Maze) -> None:
    """Write the generated maze and its solution data to a file."""
    with open(name, "w") as f:
        msg = (
            maze.get_bitmap()
            + "\n\n"
            + str(maze.entry[0])
            + ","
            + str(maze.entry[1])
            + "\n"
            + str(maze.exit[0])
            + ","
            + str(maze.exit[1])
            + "\n"
            + maze.shortest_path()
            + "\n"
        )
        f.write(msg)


def main() -> int:
    """Run the A-maze-ing application."""
    if len(sys.argv) != 2:
        logger.info(
            f"Invalid input: {len(sys.argv)} arguments given, 2 expected."
        )
        logger.info("Use: uv run python3 a_maze_ing.py [config file]")
        return 1
    else:
        config_file = sys.argv[1]

    try:
        config = get_config(config_file)
    except ValidationError as e:
        error_msg = "Invalid configuration:"
        for error in e.errors():
            error_msg += f"\n\tat {error['loc'][0]}: \t{error['msg']}"
        logger.exception(error_msg)
        return 1
    except ConfigError as e:
        logger.exception(e)
        return 1

    maze_config = config.model_dump(
        include={"width", "height", "entry", "exit"}
    )
    mazegen_config = config.model_dump(
        include={"seed", "perfect", "algorithm"}
    )
    maze = Maze(**maze_config)
    mazegen = MazeGenerator(**mazegen_config)
    try:
        mazegen.generate(maze)
    except ValueError as e:
        logger.exception(f"Unable to generate maze: {e}")

    try:
        gen_output_file(config.output_file, maze)
    except PermissionError:
        logger.exception(
            f"Permission denied to create or modify {config.output_file}"
        )
        return 1
    except FileNotFoundError:
        logger.exception(f"Could not find {config.output_file}")
        return 1
    except IsADirectoryError:
        logger.exception("{config.output_file} is a directory")
        return 1
    except OSError:
        logger.exception("Error openning file")
        return 1

    try:
        render_interface(maze)
    except RuntimeError as error:
        logger.exception(f"Graphics error: {error}")
        return 1

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted")
        sys.exit(130)
    except Exception:
        logger.exception("Unexpected error:")
        sys.exit(2)
