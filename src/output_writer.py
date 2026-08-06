from config_parser import MazeConfig, ConfigParser


def write_output(
    config: MazeConfig,
    maze: list[list[int]],
    solved_path: str,
) -> None:
    with open(config.output_file, "w") as output_file:
        for row in maze:
            hexa_row: str = ""

            for cell in hexa_row:
                hexa_cell: str = format(cell, "x")
                hexa_row += hexa_cell

            output_file.write(hexa_row)
            output_file.write("\n")

    print(f"{config.entry}      #   entry (x,y)")
    print(f"{config.exit}       #   exit (x,y)")
    print(solved_path)


if __name__ == "__main__":
    print("hi")
    # res=[10, 13]
    # print("my num is 0x{0:02x}{1:02x}".format(res[0],res[1]))

