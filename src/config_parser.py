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


class ConfigParser:
    """Read, Parse, and validate a maze configuration file."""

    @staticmethod
    def _read_file(filename: str) -> list[str]:
        """
        Read the configuration file and return its lines.

        Args:
            filename: Path to the configuration file (including its name).
        Returns:
            A list of strings, each representing a line in the config file.
        Raises:
            ConfigError: If the file cannot be read.
        """
        try:
            with open(filename, "r") as config_file:
                return config_file.readlines()
        except OSError as error:
                raise ConfigError(
                    f"Configuration file '{filename}': {error}."
                    ) from error

    @staticmethod
    def _strip_whitespace_and_comments(lines: list[str]) -> list[str]:
        """Strip whitespace and comments from the configuration lines.

        Args:
            lines: List of strings representing the lines in the config file.
        Returns:
            A list of strings with whitespace stripped and comments removed.
        """
        cleaned_lines: list[str] = []
        for line in lines:
            trimmed_line: str= line.strip()
            if line.startswith("#") or not trimmed_line:
                continue
            cleaned_lines.append(trimmed_line)

        return cleaned_lines


# if __name__ == "__main__":
    # testing datamodel
    # config = MazeConfig(
    #     width=20,
    #     height=18,
    #     entry=(0, 0),
    #     exit=(19, 17),
    #     output_file="maze.txt",
    #     perfect=False,
    #     seed=42,
    # )
    # print(config)

    #testing ConfigError
    # try:
    #     raise ConfigError("Testing config error")
    # except ConfigError as error:
    #     print(error)

    #test reading file
    # print(ConfigParser._read_file("../config.txt"))
    # print(ConfigParser._read_file("../wrong_config.txt"))
    # lines = [
    #     "# mandatory keys\n",
    #     "WIDTH=20\n",
    #     "\n",
    #     " HEIGHT=18 \n",
    # ]
    # print(ConfigParser._strip_whitespace_and_comments(lines))
