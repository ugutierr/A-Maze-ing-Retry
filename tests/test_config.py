from typing import Any

import pytest
from pydantic import ValidationError

from config import Config


@pytest.mark.parametrize(
    "args",
    [
        ((0, 0, "0, 0", "1, 1", "maze_test.txt", True, None, None, None)),
        ((9, 9, "0, 0", "1, 1", "maze_test.txt", True, None, None, None)),
        ((10, 9, "0, 0", "1, 1", "maze_test.txt", True, None, None, None)),
        ((11, 8, "0, 0", "1, 1", "maze_test.txt", True, None, None, None)),
        ((11, 9, "9, 11", "1, 1", "maze_test.txt", True, None, None, None)),
        ((15, 15, "1, 1", "1, 1", "maze_test.txt", True, None, None, None)),
        ((15, 15, "0, 1", "", "maze_test.txt", True, None, None, None)),
        ((15, 15, "0, 1", "1, 1", "", True, None, None, None)),
        ((15, 15, "0, 1", "1, 1", "lskdjf", True, None, None, None)),
        ((0, 15, "0, 1", "1, 1", "True", True, None, None, None)),
        ((-15, 15, "0, 1", "1, 1", "True", True, None, None, None)),
        ((15, 15, "0, 1", "1, 1", "True", True, None, None, None)),
        ((15, 15, "0, 1", "1, 1", "True", True, None, None, None)),
        ((20, 15, "0, 0", "20, 1", "maze_test.txt", True, None, None, None)),
        (
            (
                20,
                15,
                "0, 0",
                "1, 1",
                "maze_test.txt",
                True,
                None,
                "PACMAN",
                None,
            )
        ),
        (
            (
                20,
                15,
                "0, 0",
                "1, 1",
                "maze_test.txt",
                False,
                None,
                "DFS",
                None,
            )
        ),
        (
            (
                20,
                15,
                "0, 0",
                "15, 1",
                "maze_test.txt",
                False,
                None,
                "DFS",
                None,
            )
        ),
        (
            (
                20,
                15,
                "0, 0",
                "15, 1",
                "maze_test.txt",
                False,
                None,
                "PRIM",
                None,
            )
        ),
    ],
)
def test_invalid_config(
    args: tuple[Any],
) -> None:
    kw = (
        "width",
        "height",
        "entry",
        "exit",
        "output_file",
        "perfect",
        "seed",
        "algortithm",
        "display_mode",
    )
    with pytest.raises(ValidationError):
        Config(**{key: value for key, value in zip(kw, args)})
