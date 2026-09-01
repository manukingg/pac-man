import pygame


Color = tuple[int, int, int]


class PygameImage:
    """Abstract image representation."""
    def __init__(self: "PygameImage", surface: pygame.Surface) -> None:
        self._surface = surface

    @property
    def width(self: "PygameImage") -> int:
        return self._surface.get_width()

    @property
    def height(self: "PygameImage") -> int:
        return self._surface.get_height()

    @property
    def size(self: "PygameImage") -> tuple[int, int]:
        return self._surface.get_size()

    def fill(self: "PygameImage", color: Color) -> None:
        self._surface.fill(color)

    def get_at(self: "PygameImage", x: int, y: int) -> Color:
        pixel = self._surface.get_at((x, y))
        return pixel.r, pixel.g, pixel.b

    def blit(
        self: "PygameImage",
        source: "PygameImage",
        coords: tuple[int, int]
    ) -> None:
        self._surface.blit(source._surface, coords)

    def set_at(
        self: "PygameImage",
        coords: tuple[int, int],
        color: Color
    ) -> None:
        self._surface.set_at(coords, color)
