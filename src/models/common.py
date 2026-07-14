"""Common game model types."""

from dataclasses import dataclass
from enum import Enum, auto


class Direction(Enum):
    """Possible movement directions."""

    NONE = auto()
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


@dataclass(frozen=True, slots=True)
class GridPosition:
    """Position inside the maze grid."""

    row: int
    column: int

    def moved(self: "GridPosition", direction: Direction) -> "GridPosition":
        """Return a neighboring position in the given direction."""

        offsets: dict[Direction, tuple[int, int]] = {
            Direction.NONE: (0, 0),
            Direction.UP: (-1, 0),
            Direction.DOWN: (1, 0),
            Direction.LEFT: (0, -1),
            Direction.RIGHT: (0, 1),
        }

        row_offset, column_offset = offsets[direction]

        return GridPosition(
            row=self.row + row_offset,
            column=self.column + column_offset,
        )
