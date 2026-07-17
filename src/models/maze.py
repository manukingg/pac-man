from enum import IntFlag
from typing import TypeAlias


class Wall(IntFlag):
    """Walls surrounding one maze cell."""

    NONE = 0
    NORTH = 1 << 0  # 1
    EAST = 1 << 1   # 2
    SOUTH = 1 << 2  # 4
    WEST = 1 << 3   # 8


MazeGrid: TypeAlias = list[list[Wall]]
