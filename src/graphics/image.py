from typing import Protocol


class Image(Protocol):
    """Abstract image representation."""

    width: int
    height: int
