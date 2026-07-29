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
from wsgiref.validate import ErrorWrapper


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

    REQUIRED_KEYS: frozenset[str] = frozenset(
        {
            "WIDTH",
            "HEIGHT",
            "ENTRY",
            "EXIT",
            "OUTPUT_FILE",
            "PERFECT",
        }
    )

    OPTIONAL_KEYS: frozenset[str] = frozenset(
        {
            "SEED",
        }
    )

    @classmethod
    def _validate_keys(cls, config_kv: dict[str, str]) -> None:
        provided: set[str] = set(config_kv)
        missing: set[str] = set(config_kv) - provided

        if missing:
            raise ConfigError(
                f"config file is missing mandatory keys: "
                f"{", ".join(missing)}"
            )

        allowed: frozenset[str] = (
            cls.REQUIRED_KEYS | cls.OPTIONAL_KEYS
        )
        not_knowon_set: set[str] = provided - allowed
        if not_knowon_set:
            raise ConfigError(
                f"Unknown keys: {", ".join(missing)}"
            )

    @staticmethod
    def _parse_int(value: str, key: str) -> int:
        try:
            return int(value)
        except ValueError as error:
            raise ConfigError(
                f"'{key}' must be an integer. but got '{value}'."
            ) from error

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

    @staticmethod
    def _parse_lines(lines: list[str]) -> dict[str, str]:
        keyvalues: dict[str, str] = {}
        for line_num, line in enumerate(lines, start=1):
            key, sep, value = line.partition("=")

            if not sep:
                raise ConfigError(
                    f"Line {line_num}: expected: key=value."
                    f"Please make sure the config file is correct."
                )

            key = key.strip()
            value = value.strip()

            if not key or not value:
                raise ConfigError(
                    f"Line {line_num}: key and value cannot be empty."
                )
            if key in keyvalues:
                raise ConfigError(
                    f"Line {line_num}: key '{key}' is duplicate."
                     f"Keys must be unique."
                )
            keyvalues[key] = value

        return keyvalues


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
