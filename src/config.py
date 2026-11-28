"""Provide configuration models and utilities."""

from pathlib import Path
from typing import Annotated, Any, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from mazegen import AlgorithmType


class ConfigError(RuntimeError):
    """Raised when a configuration file cannot be loaded or validated."""


NonNegativeInt = Annotated[int, Field(ge=0)]


class Config(BaseModel):
    """Represent and validate the application configuration."""

    model_config = ConfigDict(extra="forbid")
    width: Annotated[int, Field(ge=1, le=200)]
    height: Annotated[int, Field(ge=1, le=200)]
    entry: tuple[NonNegativeInt, NonNegativeInt]
    exit: tuple[NonNegativeInt, NonNegativeInt]
    output_file: str
    perfect: bool
    seed: None | str = None
    algorithm: AlgorithmType | None = None

    @field_validator("entry", "exit", mode="before")
    @classmethod
    def parse_point(cls, value: Any) -> Any:
        """Parse a point from a comma-separated string."""
        if isinstance(value, str):
            return tuple(map(int, value.split(",")))
        return value

    @field_validator("output_file", mode="before")
    @classmethod
    def parse_output_file(cls, value: Any) -> Any:
        """Convert an empty output file value to None."""
        if value == "":
            return None
        return value

    @field_validator("seed", mode="before")
    @classmethod
    def parse_seed(cls, value: Any) -> Any:
        """Convert an empty seed value to None."""
        if isinstance(value, str) and value == "":
            return None
        return value

    @field_validator("algorithm", mode="before")
    @classmethod
    def parse_word(cls, value: Any) -> Any:
        """Normalize configuration words to uppercase."""
        if isinstance(value, str):
            if value == "":
                return None
            return value.upper()
        return value

    @model_validator(mode="after")
    def check_algorithm(self) -> Self:
        """Validate and set the maze generation algorithm."""
        if self.algorithm is None:
            self.algorithm = (
                AlgorithmType.DFS if self.perfect else AlgorithmType.PACMAN
            )
        if self.perfect and self.algorithm == AlgorithmType.PACMAN:
            raise ValueError(
                "Incompatible requirements, PACMAN like and pefect maze"
            )
        if not self.perfect and self.algorithm != AlgorithmType.PACMAN:
            raise ValueError(
                f"Incompatible requirements, {self.algorithm.name} "
                f"and a non-perfect maze"
            )
        return self

    @model_validator(mode="after")
    def check_endpoints(self) -> Self:
        """Validate the maze entry and exit coordinates."""
        if self.entry == self.exit:
            raise ValueError("Entry and exit cannot be the same cell")
        for cell in (self.entry, self.exit):
            if cell[0] >= self.width or cell[1] >= self.height:
                raise ValueError(
                    f"{'Entry' if cell == self.entry else 'Exit'}"
                    + " must have x and y coordinates"
                    + " less than width and height respectively"
                )
        return self


def parse_file(file_path: Path) -> dict[str, str]:
    ret_dict: dict[str, str] = {}
    with open(file_path, "r", encoding="utf-8") as file:
        for i, line in enumerate(file):
            clean_line = line.split("#")[0]
            if clean_line.strip() == "":
                continue
            key_value = clean_line.split("=")
            if len(key_value) != 2:
                raise ValueError(
                    f"Expected 'KEY = VALUE #COMMENT' structure in line {i}"
                )
            key = key_value[0].strip()
            value = key_value[1].strip()
            if key in ret_dict.keys():
                raise ValueError(f"Duplicated key: {key!r}")
            ret_dict[key] = value
    return ret_dict


def load_config(config_file: str) -> dict[str, str]:
    """Load and validate configuration values from a configuration file."""
    required_keys = {
        "width",
        "height",
        "entry",
        "exit",
        "output_file",
        "perfect",
    }

    optional_keys = {
        "seed",
        "algorithm",
    }
    path = Path(config_file)

    if not path.exists():
        raise ConfigError(f"Configuration file not found: {path}")

    if not path.is_file():
        raise ConfigError(f"Configuration path is not a file: {path}")

    try:
        config = parse_file(path)

    except ValueError as e:
        raise ConfigError(str(e)) from e
    except PermissionError as e:
        raise ConfigError(
            f"Cannot read configuration file (permission denied): {path}"
        ) from e
    except UnicodeDecodeError as e:
        raise ConfigError(
            f"Cannot read configuration file (invalid UTF-8): {path}"
        ) from e
    except OSError as e:
        raise ConfigError(
            f"Cannot read configuration file: {path}: {e}"
        ) from e

    normilized = {}
    for key, value in config.items():
        normilized_key = key.lower()
        if normilized_key in normilized:
            raise ConfigError(f"Duplicate configuration key: {key!r}")
        normilized[normilized_key] = value

    missing = required_keys - normilized.keys()
    if missing:
        raise ConfigError(
            f"Missing configuration variables: {', '.join(sorted(missing))}"
        )

    unrecognised = normilized.keys() - (required_keys | optional_keys)
    if unrecognised:
        raise ConfigError(
            "Unrecognised configuration variables: "
            f"{', '.join(sorted(unrecognised))}"
        )

    return normilized


def get_config(config_file: str) -> Config:
    """Load and return the validated application configuration."""
    config_dic = load_config(config_file)
    config = Config.model_validate(config_dic)
    return config
