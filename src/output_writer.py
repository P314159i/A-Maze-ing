from src.config_parser import MazeConfig, ConfigParser, ConfigError


class OutputError(Exception):
    pass


class OutputWriter:
    @staticmethod
    def write_output(
        config: MazeConfig,
        maze: list[list[int]],
        solved_path: str,
    ) -> None:
        try:
            with open(config.output_file, "w") as output_file:
                for row in maze:
                    hexa_row: str = ""

                    for cell in row:
                        hexa_cell: str = format(cell, "x")
                        hexa_row += hexa_cell

                    output_file.write(hexa_row)
                    output_file.write("\n")

                output_file.write("\n")
                output_file.write(
                    f"{config.entry[0]},{config.entry[1]}       # entry (x,y)\n"
                    f"{config.exit[0]},{config.exit[1]}       # exit (x,y)\n"
                )
                output_file.write(f"{solved_path}\n")

        except OSError as error:
            raise OutputError(
                f"Could not write output file '{config.output_file}': {error}"
            ) from error
