from ...models import (
    Direction,
    GridPosition,
    MazeGrid,
    Wall,
    Position
)

from collections import deque

POSITION_EPSILON = 0.001


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

    def positions_equal(
        self: "MazeNavigator",
        first: Position,
        second: Position,
    ) -> bool:
        """Compare positions using floating-point tolerance."""

        return (
            abs(first.x - second.x) <= POSITION_EPSILON
            and abs(first.y - second.y) <= POSITION_EPSILON
        )

    def distance_to_target(
        self: "MazeNavigator",
        position: Position,
        target: Position,
    ) -> float:
        """Return axis-aligned distance to the target."""

        return (
            abs(target.x - position.x)
            + abs(target.y - position.y)
        )

    def find_next_direction(
        self: "MazeNavigator",
        maze: MazeGrid,
        start: GridPosition,
        target: GridPosition,
        available_directions: list[Direction],
    ) -> Direction | None:
        if start == target:
            return None

        queue: deque[tuple[GridPosition, Direction]] = deque()

        visited: set[GridPosition] = {start}
        for direction in available_directions:
            next_position = start.moved(direction=direction)

            if next_position in visited:
                continue

            if next_position == target:
                return direction

            visited.add(next_position)

            queue.append((next_position, direction))

        while queue:
            current_position, first_direction = queue.popleft()

            for direction in Direction.get_all_directions():
                if not self.can_move(
                    maze=maze,
                    position=current_position,
                    direction=direction,
                ):
                    continue

                next_position = current_position.moved(direction=direction)

                if next_position in visited:
                    continue

                if next_position == target:
                    return first_direction

                visited.add(next_position)

                queue.append((next_position, first_direction))

        return None

    def is_moving_toward_position(
        self: "MazeNavigator",
        position: Position,
        target: Position,
        direction: Direction,
    ) -> bool:
        if direction == Direction.LEFT:
            return position.x > target.x

        if direction == Direction.RIGHT:
            return position.x < target.x

        if direction == Direction.UP:
            return position.y > target.y

        if direction == Direction.DOWN:
            return position.y < target.y

        return False
