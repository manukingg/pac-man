from ...models import Direction, GridPosition, MazeGrid, Wall


class MazeNavigator:
    def can_move(
        self: "MazeNavigator",
        maze: MazeGrid,
        position: GridPosition,
        direction: Direction,
    ) -> bool:
        """Return whether movement from the cell is possible."""

        if direction == Direction.NONE:
            return False

        target_position = position.moved(direction)

        if not (
            0 <= target_position.row < len(maze)
            and 0 <= target_position.column < len(maze[0])
        ):
            return False

        wall_by_direction = {
            Direction.UP: Wall.NORTH,
            Direction.DOWN: Wall.SOUTH,
            Direction.LEFT: Wall.WEST,
            Direction.RIGHT: Wall.EAST,
        }

        wall = wall_by_direction[direction]
        cell = maze[position.row][position.column]

        return not bool(cell & wall)
