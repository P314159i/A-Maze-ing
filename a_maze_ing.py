import sys
from config_parser import ConfigError, MazeConfig, ConfigParser


def get_config_file_name()-> str:
    if len(sys.argv) != 2:
        raise ConfigError(
            "Usage: python3 a_maze_ing.py <config_file.txt>"
        )
    return "txt"



def main()-> int:
    try:
        filename: str = get_config_file_name()
        # config: MazeConfig = parse(filename
    except ConfigError as error:
        print(f"Condiguration error: {error}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
