import pygame


Color = tuple[int, int, int]


class Image:
    """Abstract image representation."""
    def __init__(self: "Image", surface: pygame.Surface) -> None:
        self._surface = surface

    @property
    def width(self: "Image") -> int:
        return self._surface.get_width()

    @property
    def height(self: "Image") -> int:
        return self._surface.get_height()

    @property
    def size(self: "Image") -> tuple[int, int]:
        return self._surface.get_size()
    
    def fill(self: "Image", color: Color) -> None:
        self._surface.fill(color)

    def get_at(self: "Image", x: int, y: int) -> Color:
        pixel = self._surface.get_at((x, y))
        return pixel.r, pixel.g, pixel.b

    def blit(self: "Image", source: "Image", coords: tuple[int, int]) -> None:
        self._surface.blit(source._surface, coords)

    def set_at(self: "Image", )