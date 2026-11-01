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

GHOST_RESPAWN_DURATION = 2
CLYDE_CHASE_DISTANCE = 8

POSITION_EPSILON = 0.001

SCATTER_TARGET_OFFSET = 3

ELROY_STAGE_1_RATIO = 20 / 244
ELROY_STAGE_2_RATIO = 10 / 244

ELROY_STAGE_1_SPEED_FACTOR = 1.07
ELROY_STAGE_2_SPEED_FACTOR = 1.13


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
        normal_speed_multiplier: float,
        normal_mode: GhostMode,

        layout: GameLayout,
        remaining_collectibles: int,
        initial_collectibles: int,
    ) -> None:
        elroy_stage = self.__get_elroy_stage(
            remaining=remaining_collectibles,
            initial=initial_collectibles,
        )

        for ghost in ghosts:
            speed_multiplier = ghost.speed_multiplier

            if (
                ghost.kind == GhostKind.BLINKY
                and ghost.mode in (GhostMode.CHASE, GhostMode.SCATTER)
            ):
                if elroy_stage == 1:
                    speed_multiplier *= ELROY_STAGE_1_SPEED_FACTOR

                elif elroy_stage == 2:
                    speed_multiplier *= ELROY_STAGE_2_SPEED_FACTOR

            if (
                ghost.position is None
                or ghost.mode == GhostMode.FROZEN
            ):
                continue

            if ghost.mode == GhostMode.RESPAWNING:
                ghost.update_respawn(delta_time)

                if ghost.respawn_time_remaining <= 0:
                    ghost.finish_respawn(
                        mode=normal_mode,
                        speed_multiplier=normal_speed_multiplier,
                    )

                continue

            if (
                ghost.mode == GhostMode.EATEN
                and ghost.grid_position == ghost.spawn_position
            ):
                ghost.start_respawning(
                    duration=GHOST_RESPAWN_DURATION
                )
                continue

            distance = (
                ghosts_speed
                * speed_multiplier
                * delta_time
            )

            self.__update_ghost_movement(
                ghost=ghost,
                player=player,
                maze=maze,
                distance=distance,
                layout=layout,
                ghosts=ghosts,
                elroy_stage=elroy_stage,
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
        elroy_stage: int,
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
                        elroy_stage=elroy_stage,
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
            ghost.remember_position(next_cell)

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
        ghosts: list[GhostModel],
        elroy_stage: int,
    ) -> Direction:
        final_direction: Direction | None = None

        reverse_direction = ghost.direction.reversed()

        if (
            ghost.mode != GhostMode.EATEN
            and reverse_direction in available_directions
            and len(available_directions) > 1
        ):
            available_directions.remove(reverse_direction)

        if (
            ghost.mode in (
                GhostMode.CHASE,
                GhostMode.SCATTER,
            )
            and self.__is_ghost_looping(ghost)
        ):
            escape_direction = (
                self.__choose_loop_escape_direction(
                    ghost=ghost,
                    available_directions=available_directions,
                )
            )

            if escape_direction is not None:
                ghost.recent_positions.clear()
                return escape_direction

        if ghost.mode == GhostMode.CHASE:
            final_direction = self.__choose_direction_chase(
                available_directions=available_directions,
                ghost=ghost,
                player=player,
                ghosts=ghosts,
                maze=maze,
            )

        elif ghost.mode == GhostMode.SCATTER:
            if (
                ghost.kind == GhostKind.BLINKY
                and elroy_stage > 0
            ):
                target = player.grid_position
            else:
                target = self.__get_scatter_target(
                    ghost=ghost,
                    maze=maze,
                )
            final_direction = (
                self.__choose_direction_towards_target(
                    available_directions=available_directions,
                    current_position=ghost.grid_position,
                    target=target,
                )
            )

        elif ghost.mode == GhostMode.FRIGHTENED:
            final_direction = random.choice(available_directions)

        elif ghost.mode == GhostMode.EATEN:
            final_direction = self.__maze_navigator.find_next_direction(
                maze=maze,
                start=ghost.grid_position,
                target=ghost.spawn_position,
                available_directions=available_directions
            )

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
        ghosts: list[GhostModel],
        maze: MazeGrid,
    ) -> Direction | None:
        if ghost.kind == GhostKind.BLINKY:
            return self.__maze_navigator.find_next_direction(
                maze=maze,
                start=ghost.grid_position,
                target=player.grid_position,
                available_directions=available_directions,
            )

        elif ghost.kind == GhostKind.PINKY:
            target = self.__pinky_target(player)

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

        elif ghost.kind == GhostKind.CLYDE:
            target = self.__clyde_target(
                ghost=ghost,
                player=player,
                maze=maze,
            )

        return self.__choose_direction_towards_target(
            available_directions=available_directions,
            current_position=ghost.grid_position,
            target=target,
        )

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
        maze: MazeGrid,
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

        return self.__get_scatter_target(
            ghost=ghost,
            maze=maze,
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

    def __get_scatter_target(
        self: "GhostsController",
        ghost: GhostModel,
        maze: MazeGrid,
    ) -> GridPosition:
        rows = len(maze)
        columns = len(maze[0])

        top = ghost.spawn_position.row < rows / 2
        left = ghost.spawn_position.column < columns / 2

        row = (
            -SCATTER_TARGET_OFFSET
            if top
            else rows - 1 + SCATTER_TARGET_OFFSET
        )

        column = (
            -SCATTER_TARGET_OFFSET
            if left
            else columns - 1 + SCATTER_TARGET_OFFSET
        )

        return GridPosition(
            row=row,
            column=column,
        )

    def __get_elroy_stage(
        self: "GhostsController",
        remaining: int,
        initial: int,
    ) -> int:
        if initial <= 0:
            return 0

        stage_2_limit = max(
            1,
            round(initial * ELROY_STAGE_2_RATIO)
        )

        stage_1_limit = max(
            stage_2_limit + 1,
            round(initial * ELROY_STAGE_1_RATIO)
        )

        if remaining <= stage_2_limit:
            return 2

        if remaining <= stage_1_limit:
            return 1

        return 0

    def __is_ghost_looping(
        self: "GhostsController",
        ghost: GhostModel,
    ) -> bool:
        history = ghost.recent_positions

        if len(history) < 8:
            return False

        return history[-4:] == history[-8:-4]

    def __choose_loop_escape_direction(
        self: "GhostsController",
        ghost: GhostModel,
        available_directions: list[Direction]
    ) -> Direction | None:
        loop_cells = set(ghost.recent_positions[-4:])

        escape_directions = []

        for direction in available_directions:
            candidate = ghost.grid_position.moved(direction=direction)

            if candidate not in loop_cells:
                escape_directions.append(direction)

        if not escape_directions:
            return None

        return random.choice(escape_directions)
