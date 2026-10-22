from .game_layout import GameLayout
from .maze_navigator import MazeNavigator
from ...animation import AnimatedSprite
from ...models import (
    Direction,
    GridPosition,
    MazeGrid,
    PlayerModel,
    Position,
)

POSITION_EPSILON = 0.001


class PlayerController:
    def __init__(
        self: "PlayerController",
        pacman_sprite: AnimatedSprite,
        maze_navigator: MazeNavigator
    ) -> None:
        self.__pacman_sprite = pacman_sprite
        self.__maze_navigator = maze_navigator

    def update(
        self: "PlayerController",
        player: PlayerModel,
        maze: MazeGrid,
        delta_time: float,
        layout: GameLayout,
        player_speed: float,
    ) -> list[GridPosition]:
        if player.position is None:
            return []

        distance = (
            player_speed
            * player.speed_multiplier
            * delta_time
        )

        reached_cells = self.__update_player_movement(
            player=player,
            maze=maze,
            distance=distance,
            layout=layout,
        )
        # !!!! TAKE ALL GRAPHICS TO RENDERER, THIS CLASS ONLY CONTROLLING !!!!
        self.__pacman_sprite.update(delta_time)
        ###################################################################
        return reached_cells

    def initialize_player_position(
        self: "PlayerController",
        player: PlayerModel,
        layout: GameLayout,
    ) -> None:
        """Initialize continuous player position from the spawn cell."""

        if player.position is not None:
            return

        position = layout.get_grid_position_center(
            position=player.grid_position,
        )

        player.move_to(position)

    def __update_player_movement(
        self: "PlayerController",
        player: PlayerModel,
        maze: MazeGrid,
        distance: float,
        layout: GameLayout,
    ) -> list[GridPosition]:
        """Move Pac-Man continuously through the maze."""
        reached_cells: list[GridPosition] = []

        if player.position is None:
            return reached_cells

        while distance > POSITION_EPSILON:
            current_cell_center = layout.get_grid_position_center(
                position=player.grid_position,
            )

            if (
                not self.__maze_navigator.positions_equal(
                    player.position,
                    current_cell_center,
                )
                and self.__is_opposite_direction(
                    first=player.direction,
                    second=player.requested_direction,
                )
            ):
                player.change_direction(player.requested_direction)

            if self.__maze_navigator.positions_equal(
                player.position,
                current_cell_center,
            ):
                player.move_to(current_cell_center)

                self.__try_change_direction(
                    player=player,
                    maze=maze,
                )

                if (
                    player.direction == Direction.NONE
                    or not self.__maze_navigator.can_move(
                        maze=maze,
                        position=player.grid_position,
                        direction=player.direction,
                    )
                ):
                    player.change_direction(Direction.NONE)
                    self.__pacman_sprite.stop()
                    return reached_cells

            if self.__maze_navigator.is_moving_toward_position(
                position=player.position,
                target=current_cell_center,
                direction=player.direction,
            ):
                distance, reached_center = self.__move_player_towards(
                    player=player,
                    target=current_cell_center,
                    distance=distance,
                )

                if not reached_center:
                    break

                continue

            if player.direction == Direction.NONE:
                self.__pacman_sprite.stop()
                return reached_cells

            target_grid_position = player.grid_position.moved(
                player.direction
            )

            target_position = layout.get_grid_position_center(
                position=target_grid_position
            )

            distance, reached_target = self.__move_player_towards(
                player=player,
                target=target_position,
                distance=distance,
            )

            if not reached_target:
                break

            player.move_to_grid(target_grid_position)
            reached_cells.append(target_grid_position)

        return reached_cells

    def __try_change_direction(
        self: "PlayerController",
        player: PlayerModel,
        maze: MazeGrid,
    ) -> None:
        """Apply requested direction when movement is possible."""

        requested_direction = player.requested_direction

        if requested_direction == Direction.NONE:
            return

        if not self.__maze_navigator.can_move(
            maze=maze,
            position=player.grid_position,
            direction=requested_direction,
        ):
            return

        player.change_direction(requested_direction)

    def __is_opposite_direction(
        self: "PlayerController",
        first: Direction,
        second: Direction,
    ) -> bool:
        return first.reversed() == second

    def __move_player_towards(
        self: "PlayerController",
        player: PlayerModel,
        target: Position,
        distance: float,
    ) -> tuple[float, bool]:
        """Helper function, returning:
         how many movement budget we have left on this frame
         and have we reached the target location"""
        if player.position is None:
            return distance, False

        remaining_distance = self.__maze_navigator.distance_to_target(
            position=player.position,
            target=target,
        )

        if remaining_distance <= POSITION_EPSILON:
            player.move_to(target)
            return distance, True

        step = min(distance, remaining_distance)

        player.move_to(
            player.position.moved(
                direction=player.direction,
                distance=step,
            )
        )

        self.__pacman_sprite.play(animation=player.direction.name.lower())

        distance -= step

        if step + POSITION_EPSILON < remaining_distance:
            return distance, False

        player.move_to(target)

        return distance, True
