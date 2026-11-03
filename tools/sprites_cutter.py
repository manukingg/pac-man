from pathlib import Path

from PIL import Image


SPRITE_SIZE = 16

COLUMNS = 11
ROWS = 10

OFFSET_TOP = 0
OFFSET_RIGHT = 0

CHARSET = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    "!@#$%^&*()-_=+[]{}<>?"
)


def rgb_to_hex(color: tuple[int, int, int]) -> str:
    red, green, blue = color

    return f"#{red:02X}{green:02X}{blue:02X}"


def save_xpm(
    image: Image.Image,
    output_path: Path,
) -> None:
    image = image.convert("RGBA")

    colors: list[tuple[int, int, int, int]] = []

    for y in range(image.height):
        for x in range(image.width):
            color = image.getpixel((x, y))

            if color not in colors:
                colors.append(color)

    if len(colors) > len(CHARSET):
        raise ValueError(
            "Too many colors for single-character XPM charset"
        )

    color_map = {
        color: CHARSET[index]
        for index, color in enumerate(colors)
    }

    lines = [
        "/* XPM */",
        "static char *image[] = {",
        f'"{image.width} {image.height} {len(colors)} 1",',
    ]

    for color in colors:
        character = color_map[color]

        red, green, blue, alpha = color

        if alpha == 0:
            color_value = "None"
        else:
            color_value = rgb_to_hex(
                (red, green, blue)
            )

        lines.append(
            f'"{character} c {color_value}",'
        )

    for y in range(image.height):
        row = ""

        for x in range(image.width):
            color = image.getpixel((x, y))
            row += color_map[color]

        comma = "," if y < image.height - 1 else ""
        lines.append(f'"{row}"{comma}')

    lines.append("};")

    output_path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    input_path = Path("tools/ghosts_sheet.png")
    output_dir = Path("ghosts")

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    image = Image.open(input_path)

    start_x = (
        image.width
        - OFFSET_RIGHT
        - COLUMNS * SPRITE_SIZE
    )

    start_y = OFFSET_TOP

    for row in range(ROWS):
        for column in range(COLUMNS):
            left = (
                start_x
                + column * SPRITE_SIZE
            )

            top = (
                start_y
                + row * SPRITE_SIZE
            )

            right = left + SPRITE_SIZE
            bottom = top + SPRITE_SIZE

            sprite = image.crop(
                (
                    left,
                    top,
                    right,
                    bottom,
                )
            )

            output_path = (
                output_dir
                / f"sprite_{row}_{column}.xpm"
            )

            save_xpm(
                image=sprite,
                output_path=output_path,
            )

            print(output_path)


if __name__ == "__main__":
    main()
