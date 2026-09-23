from pathlib import Path

from PIL import Image


def rgb_to_hex(color: tuple[int, int, int]) -> str:
    red, green, blue = color
    return f"#{red:02X}{green:02X}{blue:02X}"


def main() -> None:
    source = Path("assets/pacman-up/3.png")
    target = Path("assets/pacman-up/3.xpm")

    image = Image.open(source).convert("RGBA")

    width, height = image.size

    colors: dict[tuple[int, int, int, int], str] = {}
    symbols: list[str] = []

    charset = (
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz"
        "0123456789"
        "!@#$%^&*()-_=+[]{}<>?"
    )

    for pixel in image.getdata():
        if pixel not in colors:
            symbol = charset[len(colors)]
            colors[pixel] = symbol
            symbols.append(symbol)

    with target.open("w") as file:
        file.write("/* XPM */\n")
        file.write("static char *image[] = {\n")

        file.write(
            f'"{width} {height} {len(colors)} 1",\n'
        )

        for color, symbol in colors.items():
            red, green, blue, alpha = color

            if alpha == 0:
                value = "None"
            else:
                value = rgb_to_hex(
                    (red, green, blue)
                )

            file.write(
                f'"{symbol} c {value}",\n'
            )

        pixels = list(image.getdata())

        for y in range(height):
            row = ""

            for x in range(width):
                pixel = pixels[y * width + x]
                row += colors[pixel]

            comma = "," if y < height - 1 else ""

            file.write(
                f'"{row}"{comma}\n'
            )

        file.write("};\n")

    print(f"Converted: {source} -> {target}")


if __name__ == "__main__":
    main()