from dataclasses import dataclass


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
        missing: frozenset[str] = cls.REQUIRED_KEYS - provided

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

    @classmethod
    def _parse_str_to_positive_int(cls, value: str, key: str) -> int:
        "Convert a value to a postitive integer"
        num: int = cls._parse_int(value, key)
        if num <= 0:
            raise ConfigError(f"'{key}' must be greater than zero")
        return num

    @classmethod
    def _parse_coordinate(
        cls,
        value: str,
        key: str,
    ) -> tuple[int, int]:
        """Convert a value such as '3,5' to a coordinate tuple."""
        coord: list[str] = value.split(",")

        if len(coord) != 2:
            raise ConfigError(
                f"'{key}' must use the format x,y, got '{value}'"
            )

        x: int = cls._parse_int(coord[0].strip(), key)
        y: int = cls._parse_int(coord[0].strip(), key)

        return x, y

    @staticmethod
    def _parse_bool(value: str, key: str) -> bool:
        if value == "True":
            return True
        if value == "False":
            return False
        raise ConfigError(
            f"'{key}' must be 'True' or 'False', but got: '{value}'"
        )

    @staticmethod
    def _validate_position(
        position: tuple[int, int],
        width: int,
        height: int,
        key: str,
    ) -> None:
        x, y = position
        if not (0 <= x < width and 0 <= y < height):
            raise ConfigError(
                f"'{key}' position is '{position}'. it's out of bound."
                f"Valid bounds for the maze: {width}x{height}"
            )

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
    def _clean_lines(lines: list[str]) -> list[str]:
        """Strip whitespace and comments from the configuration lines.

        Args:
            lines: List of strings representing the lines in the config file.
        Returns:
            A list of strings with whitespace stripped and comments removed.
        """
        cleaned_lines: list[str] = []
        for line in lines:
            trimmed_line: str = line.strip()
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

    @classmethod
    def parse_file(cls, filename: str) -> MazeConfig:
        raw_lines: list[str] = cls._read_file(filename)
        cleaned_lines: list[str] = cls._clean_lines(raw_lines)
        keyvalues: dict[str, str] = cls._parse_lines(cleaned_lines)

        cls._validate_keys(keyvalues)
        width: int = cls._parse_str_to_positive_int(
            keyvalues["WIDTH"],
            "WIDTH",
        )

        height: int = cls._parse_str_to_positive_int(
            keyvalues["HEIGHT"],
            "HEIGHT",
        )

        entry_point: tuple[int, int] = cls._parse_coordinate(
            keyvalues["Entry"],
            "Entry",
        )

        exit_point: tuple[int, int] = cls._parse_coordinate(
                    keyvalues["EXIT"],
                    "EXIT",
        )

        perfect: bool = cls._parse_bool(
            keyvalues["PERFECT"],
            "PERFECT",
        )

        cls._validate_position(entry_point, width, height, "ENTRY")
        cls._validate_position(exit_point, width, height, "EXIT")

        if entry_point == exit_point:
            raise ConfigError("ENTRY and EXIT cannot be the same.")

        seed: int | None = None
        if "SEED" in keyvalues:
            seed = cls._parse_int(keyvalues["SEED"], "SEED")

        return MazeConfig(
            width=width,
            height=height,
            entry=entry_point,
            exit=exit_point,
            output_file=keyvalues["OUTPUT_FILE"],
            perfect=perfect,
            seed=seed
        )
