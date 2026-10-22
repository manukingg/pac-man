from ...models import (
    GhostModel,
    Direction,
    MazeGrid,
    GhostKind,
    GhostMode,
    Position,
    GridPosition,
    PlayerModel,
)
from .maze_navigator import MazeNavigator
from .game_layout import GameLayout

import random

CLYDE_CHASE_DISTANCE = 8
POSITION_EPSILON = 0.001


class GhostsController:
    def __init__(
        self: "GhostsController",
        maze_navigator: MazeNavigator,
    ) -> None:
        self.__maze_navigator = maze_navigator

    def update(
        self: "GhostsController",
        ghosts: list[GhostModel],
        player: PlayerModel,
        maze: MazeGrid,
        delta_time: float,
        ghosts_speed: float,
        layout: GameLayout,
    ) -> None:
        for ghost in ghosts:
            if (
                ghost.position is None
                or ghost.mode in (GhostMode.FROZEN, GhostMode.RESPAWNING)
            ):
                continue
            distance = (
                ghosts_speed
                * ghost.speed_multiplier
                * delta_time
            )
            self.__update_ghost_movement(
                ghost=ghost,
                player=player,
                maze=maze,
                distance=distance,
                layout=layout,
                ghosts=ghosts,
            )

    def initialize_ghosts_position(
        self: "GhostsController",
        ghosts: list[GhostModel],
        maze: MazeGrid,
        layout: GameLayout,
    ) -> None:

        for ghost in ghosts:
            if ghost.position is not None:
                continue
            position = layout.get_grid_position_center(
                position=ghost.grid_position
            )
            possible_directions = [
                direction
                for direction in (
                    Direction.UP,
                    Direction.DOWN,
                    Direction.LEFT,
                    Direction.RIGHT,
                )
                if self.__maze_navigator.can_move(
                    maze=maze,
                    position=ghost.grid_position,
                    direction=direction,
                )
            ]
            ghost.direction = random.choice(possible_directions)

            ghost.move_to(position)

    def __update_ghost_movement(
        self: "GhostsController",
        ghost: GhostModel,
        player: PlayerModel,
        maze: MazeGrid,
        distance: float,
        layout: GameLayout,
        ghosts: list[GhostModel],
    ) -> None:
        if ghost.position is None:
            return

        while distance > POSITION_EPSILON:
            current_cell_center = layout.get_grid_position_center(
                position=ghost.grid_position
            )
            if (
                not self.__maze_navigator.positions_equal(
                    first=ghost.position,
                    second=current_cell_center,
                )
                and self.__maze_navigator.is_moving_toward_position(
                    position=ghost.position,
                    target=current_cell_center,
                    direction=ghost.direction,
                )
            ):
                distance, reached_center = self.__move_ghost_towards(
                    ghost=ghost,
                    target=current_cell_center,
                    distance=distance,
                )
                if not reached_center:
                    return

                continue
            if self.__maze_navigator.positions_equal(
                first=ghost.position,
                second=current_cell_center,
            ):
                ghost.move_to(current_cell_center)

                available_directions = self.__get_available_directions(
                    current_cell=ghost.grid_position,
                    maze=maze,
                )

                if not available_directions:
                    ghost.direction = Direction.NONE
                    return

                if (
                    ghost.force_reverse_pending
                    and ghost.direction in available_directions
                ):
                    ghost.finish_forced_reverse()
                else:
                    if ghost.force_reverse_pending:
                        ghost.finish_forced_reverse()

                    direction = self.__choose_direction(
                        available_directions=available_directions,
                        ghost=ghost,
                        player=player,
                        maze=maze,
                        ghosts=ghosts,
                    )
                    ghost.direction = direction

            if ghost.direction == Direction.NONE:
                return

            next_cell = ghost.grid_position.moved(direction=ghost.direction)
            target = layout.get_grid_position_center(position=next_cell)
            distance, reached_target = self.__move_ghost_towards(
                ghost=ghost,
                target=target,
                distance=distance,
            )

            if not reached_target:
                return

            ghost.move_to_grid(next_cell)

    def __get_available_directions(
        self: "GhostsController",
        current_cell: GridPosition,
        maze: MazeGrid,
    ) -> list[Direction]:
        return list(
            direction
            for direction in Direction.get_all_directions()
            if self.__maze_navigator.can_move(
                maze=maze,
                position=current_cell,
                direction=direction
            )
        )

    def __choose_direction(
        self: "GhostsController",
        available_directions: list[Direction],
        ghost: GhostModel,
        player: PlayerModel,
        maze: MazeGrid,
        ghosts: list[GhostModel]
    ) -> Direction:
        reverse_direction = ghost.direction.reversed()
        if (
            reverse_direction in available_directions
            and len(available_directions) > 1
        ):
            available_directions.remove(reverse_direction)

        if ghost.mode == GhostMode.CHASE:
            final_direction = self.__choose_direction_chase(
                available_directions=available_directions,
                ghost=ghost,
                player=player,
                maze=maze,
                ghosts=ghosts,
            )

        if (
            ghost.mode == GhostMode.FRIGHTENED
            or ghost.mode == GhostMode.FRIGHTENED_WARNING
        ):
            final_direction = random.choice(available_directions)

        if final_direction is not None:
            return final_direction

        if ghost.direction in available_directions:
            return ghost.direction

        return random.choice(available_directions)

    def __move_ghost_towards(
        self: "GhostsController",
        ghost: GhostModel,
        target: Position,
        distance: float,
    ) -> tuple[float, bool]:
        if ghost.position is None:
            return distance, False

        remaining_distance = self.__maze_navigator.distance_to_target(
            position=ghost.position,
            target=target,
        )

        if remaining_distance <= POSITION_EPSILON:
            ghost.move_to(target)
            return distance, True

        step = min(distance, remaining_distance)

        ghost.move_to(
            ghost.position.moved(
                direction=ghost.direction,
                distance=step,
            )
        )

        distance -= step

        if step + POSITION_EPSILON < remaining_distance:
            return distance, False

        ghost.move_to(target)

        return distance, True

    def __choose_direction_chase(
        self: "GhostsController",
        available_directions: list[Direction],
        ghost: GhostModel,
        player: PlayerModel,
        maze: MazeGrid,
        ghosts: list[GhostModel],
    ) -> Direction | None:
        start = ghost.grid_position
        if ghost.kind == GhostKind.BLINKY:
            target = player.grid_position

            return self.__maze_navigator.find_next_direction(
                maze=maze,
                start=start,
                target=target,
                available_directions=available_directions,
            )

        elif ghost.kind == GhostKind.PINKY:
            target = self.__pinky_target(player)

            return self.__choose_direction_towards_target(
                available_directions=available_directions,
                current_position=ghost.grid_position,
                target=target,
            )

        elif ghost.kind == GhostKind.INKY:
            blinky = self.__get_ghost_by_kind(
                ghosts=ghosts,
                kind=GhostKind.BLINKY
            )

            if blinky is None:
                return None

            target = self.__inky_target(
                player=player,
                blinky=blinky
            )

            return self.__choose_direction_towards_target(
                available_directions=available_directions,
                current_position=ghost.grid_position,
                target=target,
            )

        elif ghost.kind == GhostKind.CLYDE:
            target = self.__clyde_target(
                ghost=ghost,
                player=player,
            )

            return self.__choose_direction_towards_target(
                available_directions=available_directions,
                current_position=ghost.grid_position,
                target=target,
            )

        return None

    def __pinky_target(
        self: "GhostsController",
        player: PlayerModel,
    ) -> GridPosition:
        target = player.grid_position

        if player.direction == Direction.NONE:
            return player.grid_position

        for _ in range(4):
            target = target.moved(direction=player.direction)

        return target

    def __inky_target(
        self: "GhostsController",
        player: PlayerModel,
        blinky: GhostModel,
    ) -> GridPosition:
        pivot = player.grid_position

        if player.direction != Direction.NONE:
            for _ in range(2):
                pivot = pivot.moved(direction=player.direction)

        return GridPosition(
            row=2 * pivot.row - blinky.grid_position.row,
            column=2 * pivot.column - blinky.grid_position.column,
        )

    def __clyde_target(
        self: "GhostsController",
        ghost: GhostModel,
        player: PlayerModel,
    ) -> GridPosition:
        row_distance = (
            ghost.grid_position.row
            - player.grid_position.row
        )
        column_distance = (
            ghost.grid_position.column
            - player.grid_position.column
        )

        distance_squared = (
            row_distance * row_distance
            + column_distance * column_distance
        )

        if distance_squared >= CLYDE_CHASE_DISTANCE ** 2:
            return player.grid_position

        return GridPosition(
            row=ghost.spawn_position.row + 2,
            column=ghost.spawn_position.column - 2
        )

    def __choose_direction_towards_target(
        self: "GhostsController",
        available_directions: list[Direction],
        current_position: GridPosition,
        target: GridPosition,
    ) -> Direction | None:
        direction_priority = (
            Direction.UP,
            Direction.LEFT,
            Direction.DOWN,
            Direction.RIGHT,
        )

        best_direction: Direction | None = None
        best_distance: int | None = None

        for direction in direction_priority:
            if direction not in available_directions:
                continue

            candidate = current_position.moved(direction=direction)

            row_distance = candidate.row - target.row
            column_distance = candidate.column - target.column

            distance = (row_distance * row_distance
                        + column_distance * column_distance)
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_direction = direction

        if best_direction is None:
            raise RuntimeError("No available directions for ghost")

        return best_direction

    def __get_ghost_by_kind(
        self: "GhostsController",
        ghosts: list[GhostModel],
        kind: GhostKind,
    ) -> GhostModel | None:
        for ghost in ghosts:
            if ghost.kind == kind:
                return ghost
        return None
