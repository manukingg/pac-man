from typing import Protocol


class Image(Protocol):
    @property
    def width(self: "Image") -> int:
        pass

    @property
    def height(self: "Image") -> int:
        pass
