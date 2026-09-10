"""Common game model types."""

from dataclasses import dataclass
from enum import Enum, auto


class Direction(Enum):
    """Possible movement directions."""

    NONE = (0, 0)
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


@dataclass(slots=True)
class Position:
    x: float
    y: float

    def moved(
        self: "Position",
        direction: Direction,
        distance: float,
    ) -> "Position":
        """Return a position moved by the given distance."""

        x_offset, y_offset = direction.value

        return Position(
            x=self.x + x_offset * distance,
            y=self.y + y_offset * distance,
        )


@dataclass(slots=True)
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
