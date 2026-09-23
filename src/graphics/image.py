from typing import Protocol
import sys


Color = tuple[int, int, int]


class Image(Protocol):
    @property
    def width(self: "Image") -> int:
        pass

    @property
    def height(self: "Image") -> int:
        return self._surface.get_height()

    @property
    def size(self: "Image") -> tuple[int, int]:
        return self._surface.get_size()

    def fill(self: "Image", color: Color) -> None:
        """Fill the whole image by writing directly to its pixel buffer."""

        bytes_per_pixel = self._surface.get_bytesize()
        pitch = self._surface.get_pitch()

        pixel = self._surface.map_rgb(color)

        pixel_bytes = pixel.to_bytes(
            bytes_per_pixel,
            byteorder=sys.byteorder,
        )

        row = pixel_bytes * self.width

        buffer = self._surface.get_buffer()
        view = memoryview(buffer)

        for y in range(self.height):
            start = y * pitch
            end = start + len(row)

            view[start:end] = row

        view.release()

    def get_at(self: "Image", x: int, y: int) -> Color:
        pixel = self._surface.get_at((x, y))
        return pixel.r, pixel.g, pixel.b

    def blit(self: "Image", source: "Image", coords: tuple[int, int]) -> None:
        self._surface.blit(source._surface, coords)

    def set_at(self: "Image", coords: tuple[int, int], color: Color) -> None:
        self._surface.set_at(coords, color)
