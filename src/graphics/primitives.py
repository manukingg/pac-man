from src.graphics.pygame_wrapper import Color, GraphicsBackend
from src.graphics.image import Image


def draw_line(
    graphics: GraphicsBackend,
    image: Image,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: Color,
) -> None:
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    error = dx - dy
    x = x0
    y = y0

    while True:
        graphics.put_pixel(image, x, y, color)

        if x == x1 and y == y1:
            break

        double_error = 2 * error
        if double_error > -dy:
            error -= dy
            x += sx

        if double_error < dx:
            error += dx
            y += sy


def draw_rect(
    graphics: GraphicsBackend,
    image: Image,
    x: int,
    y: int,
    width: int,
    height: int,
    color: Color,
) -> None:
    for current_y in range(y, y + height):
        for current_x in range(x, x + width):
            graphics.put_pixel(image, current_x, current_y, color)