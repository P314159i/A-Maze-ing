import typing
import sys


# # mandatory keys
# WIDTH=20
# HEIGHT=18
# ENTRY=0,0
# EXIT=19,17
# OUTPUT_FILE=maze.txt
# PERFECT=False

# # optional keys
# SEED=42
# # ALGORITHM=??
# # DISPLAY_MODE=???


from dataclasses import dataclass


class ConfigError(Exception):
    """Raised when configuration data is invalid."""
    pass

@dataclass(frozen=True)
class MazeConfig:
    """Store validated maze configuration values."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None


if __name__ == "__main__":
    # testing datamodel
    config = MazeConfig(
        width=20,
        height=18,
        entry=(0, 0),
        exit=(19, 17),
        output_file="maze.txt",
        perfect=False,
        seed=42,
    )
    print(config)

    #testing ConfigError
    try:
        raise ConfigError("Testing config error")
    except ConfigError as error:
        print(error)



