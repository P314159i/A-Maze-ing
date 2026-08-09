"""Configuration parsing for the A-Maze-ing project."""

from dataclasses import dataclass


class ConfigError(Exception):
    """Raised when configuration data is invalid."""
    pass


@dataclass(frozen=True)
class MazeConfig:
    """Store validated maze configuration values."""

    width: int
    height: int
    entry_point: tuple[int, int]
    exit_point: tuple[int, int]
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
        """Check mandatory and unsupported keys."""

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
        unknowon_keys_set: set[str] = provided - allowed
        if unknowon_keys_set:
            raise ConfigError(
                f"Unknown keys: {", ".join(sorted(unknowon_keys_set))}"
            )

    @staticmethod
    def _parse_int(value: str, key: str) -> int:
        """Convert a value to an integer."""
        try:
            return int(value)
        except ValueError as error:
            raise ConfigError(
                f"'{key}' must be an integer. but got '{value}'."
            ) from error

    @classmethod
    def _parse_positive_int(cls, value: str, key: str) -> int:
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

        x_str: str = coord[0].strip()
        y_str: str = coord[1].strip()

        if not x_str or not y_str:
            raise ConfigError(
                f"'{key}' must contain both x and y coordinates."
            )

        x: int = cls._parse_int(x_str, key)
        y: int = cls._parse_int(y_str, key)

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
        """Ensure a coordinate is inside the maze."""
        x, y = position

        if not 0 <= x < width:
            raise ConfigError(
                f"x-coordinate '{key}'[x]={x} is outside "
                f"the valid range: 0 to {width - 1}"
            )

        if not 0 <= y < height:
            raise ConfigError(
                f"y-coordinate '{key}'[y]={y} is outside "
                f"the valid range 0 to {height - 1}"
            )

    @staticmethod
    def _read_file(filename: str) -> dict[str, str]:
        """
        Read the configuration values from a file.

        Args:
            filename: Path to the configuration file (including its name).
        Returns:
            A dictionary mapping configuration keys to their values.
        Raises:
            ConfigError: If the file cannot be read or contains invalid lines.
        """

        values: dict[str, str] = {}

        try:
            with open(filename, "r") as config_file:
                for line_number, raw_line in enumerate(
                    config_file,
                    start=1,
                ):
                    line: str = raw_line.strip()

                    if not line or line.startswith("#"):
                        continue

                    key, separator, value = line.partition("=")

                    if not separator:
                        raise ConfigError(
                            f"Line {line_number}: "
                            "expected KEY=VALUE"
                        )

                    key = key.strip()
                    value = value.strip()

                    if not key:
                        raise ConfigError(
                            f"Line {line_number}: key cannot be empty"
                        )

                    if not value:
                        raise ConfigError(
                            f"Line {line_number}: value for "
                            f"'{key}' cannot be empty"
                        )

                    if key in values:
                        raise ConfigError(
                            f"Line {line_number}: "
                            f"duplicate key '{key}'"
                        )

                    values[key] = value

        except OSError as error:
            raise ConfigError(
                f"Could not read configuration file "
                f"'{filename}': {error}"
            ) from error

        return values

    @staticmethod
    def _validate_output_file(output_file: str) -> None:
        """Check the output filename."""
        if not output_file:
            raise ConfigError("OUTPUT_FILE cannot be empty")

    @classmethod
    def parse(cls, filename: str) -> MazeConfig:
        """Read and validate a configuration file.

        Args:
            filename: Path to the configuration file.

        Returns:
            Validated maze configuration.

        Raises:
            ConfigError: If the file or its contents are invalid.
        """
        values: dict[str, str] = cls._read_file(filename)

        cls._validate_keys(values)

        width: int = cls._parse_positive_int(
            values["WIDTH"],
            "WIDTH",
        )
        height: int = cls._parse_positive_int(
            values["HEIGHT"],
            "HEIGHT",
        )

        entry_point: tuple[int, int] = cls._parse_coordinate(
            values["ENTRY"], "ENTRY",
        )
        exit_point: tuple[int, int] = cls._parse_coordinate(
            values["EXIT"],
            "EXIT",
        )

        output_file: str = values["OUTPUT_FILE"].strip()

        perfect: bool = cls._parse_bool(values["PERFECT"], "PERFECT")
        seed: int | None = None

        if "SEED" in values:
            seed = cls._parse_int(values["SEED"], "SEED")

        cls._validate_output_file(output_file)
        cls._validate_position(
            entry_point,
            width,
            height,
            "ENTRY",
        )
        cls._validate_position(
            exit_point,
            width,
            height,
            "EXIT",
        )

        if entry_point == exit_point:
            raise ConfigError("ENTRY and EXIT must be different")

        return MazeConfig(
            width=width,
            height=height,
            entry_point=entry_point,
            exit_point=exit_point,
            output_file=output_file,
            perfect=perfect,
            seed=seed,
        )
