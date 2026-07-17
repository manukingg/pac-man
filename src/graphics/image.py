import pygame


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
