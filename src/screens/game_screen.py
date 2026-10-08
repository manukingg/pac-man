from ..animation import AnimatedSprite
from ..graphics import (
    Image,
    GraphicsEvent,
    EventType,
    Key,
    GraphicsBackend
)
from ..models import (
    AppState,
    Direction,
    GridPosition,
    MazeGrid,
    PlayerModel,
    Position,
    Wall,
)

from .screen import Screen


Color = tuple[int, int, int]
WallSegment = tuple[int, int, int, int]

POSITION_EPSILON = 0.001
PELLET_COLOR: Color = (255, 220, 180)


class GameScreen(Screen):
    """Render and control the current game session."""

    _BACKGROUND_COLOR: Color = (0, 0, 0)
    _WALL_COLOR: Color = (32, 88, 255)
    _ERROR_COLOR: Color = (255, 64, 64)

    def __init__(
        self: "GameScreen",
        pacman_sprite: AnimatedSprite,
    ) -> None:
        self.__pacman_sprite = pacman_sprite
        self.__maze_image: Image | None = None
        self.__pellet_image: Image | None = None

        self.__cell_size: int | None = None
        self.__offset_x: int | None = None
        self.__offset_y: int | None = None

        self.__hud_height: int | None = None
        self.__player_size: int | None = None
        self.__player_speed: float | None = None
        self.__pellet_size: int | None = None
        self.__prepared_player_size: int | None = None
        self.__big_pellet_size: int | None = None

        self.__padding: int | None = None
        self.__error_font_size: int | None = None

    def handle_event(
        self: "GameScreen",
        event: GraphicsEvent,
        state: AppState,
        change_resolution: bool | None = None
    ) -> str | None:
        """Handle gameplay input."""

        if change_resolution:
            self.__error_font_size = None
            self.__player_speed = None
            self.__player_size = None
            self.__prepared_player_size = None
            self.__pellet_size = None
            self.__big_pellet_size = None
            self.__padding = None
            self.__hud_height = None
            self.__pellet_image = None
            return

        if event.type != EventType.KEY_DOWN:
            return

        if event.key == Key.ESCAPE:
            return "quit"

        game_state = state.game_state

        if game_state is None:
            return

        direction_by_key = {
            Key.UP: Direction.UP,
            Key.W: Direction.UP,
            Key.DOWN: Direction.DOWN,
            Key.S: Direction.DOWN,
            Key.LEFT: Direction.LEFT,
            Key.A: Direction.LEFT,
            Key.RIGHT: Direction.RIGHT,
            Key.D: Direction.RIGHT,
        }

        direction = direction_by_key.get(event.key)

        if direction is None:
            return

        game_state.player.request_move(direction)

    def update(
        self: "GameScreen",
        delta_time: float,
        state: AppState,
    ) -> None:
        """Update the current game session."""

        game_state = state.game_state

        if game_state is None:
            return

        player = game_state.player

        if player.position is None:
            return

        if self.__cell_size is None:
            return

        self.__update_player_movement(
            player=player,
            maze=game_state.maze,
            delta_time=delta_time,
            pellets=game_state.pellets
        )

        self.__pacman_sprite.update(delta_time)

    def render(
        self: "GameScreen",
        display: GraphicsBackend,
        image: Image,
        state: AppState,
    ) -> None:
        """Render the current game session."""

        display.clear(
            image=image,
            color=self._BACKGROUND_COLOR,
        )

        game_state = state.game_state

        if game_state is None:
            self.__render_error(
                display=display,
                image=image,
                text="GAME STATE IS NOT INITIALIZED",
            )
            return

        maze = game_state.maze

        if not maze or not maze[0]:
            self.__render_error(
                display=display,
                image=image,
                text="MAZE IS EMPTY",
            )
            return

        self.__initialize_layout(
            image=image,
            maze=maze,
        )

        self.__ensure_pacman_scale(display)
        self.__ensure_pellet_image(display)

        self.__render_cached_maze(
            display=display,
            image=image,
            maze=maze,
        )

        self.__initialize_player_position(player=game_state.player)

        self.__render_pellets(
            display=display,
            image=image,
            pellets=game_state.pellets,
        )

        self.__render_pacman(
            display=display,
            image=image,
            player=game_state.player,
        )

    def __initialize_layout(
        self: "GameScreen",
        image: Image,
        maze: MazeGrid,
    ) -> None:
        row_count = len(maze)
        column_count = len(maze[0])

        old_cell_size = self.__cell_size
        old_pellet_size = self.__pellet_size

        self.__calculate_screen_metrics(image)

        self.__cell_size = self.__calculate_cell_size(
            image_width=image.width,
            image_height=image.height,
            row_count=row_count,
            column_count=column_count,
        )

        self.__calculate_game_metrics()

        if self.__cell_size != old_cell_size:
            self.__maze_image = None

        if self.__pellet_size != old_pellet_size:
            self.__pellet_image = None

        maze_width, maze_height = self.__get_maze_size(
            column_count=column_count,
            row_count=row_count,
            cell_size=self.__cell_size,
        )

        self.__offset_x, self.__offset_y = self.__get_offsets(
            image=image,
            maze_width=maze_width,
            maze_height=maze_height,
        )

    def __calculate_screen_metrics(
        self: "GameScreen",
        image: Image,
    ) -> None:
        shortest_side = min(
            image.width,
            image.height,
        )

        self.__padding = max(12, round(shortest_side * 0.025))

        self.__hud_height = max(60, round(image.height * 0.12))

        self.__error_font_size = max(2, round(shortest_side / 400))

    def __calculate_cell_size(
        self: "GameScreen",
        image_width: int,
        image_height: int,
        row_count: int,
        column_count: int,
    ) -> int:
        available_width = image_width - self.__padding * 2

        available_height = (
            image_height - self.__padding * 2 - self.__hud_height)

        cell_width = available_width // column_count

        cell_height = available_height // row_count

        return min(cell_width, cell_height)

    def __calculate_game_metrics(self: "GameScreen") -> None:
        if self.__cell_size is None:
            return

        self.__player_size = max(8, round(self.__cell_size * 0.72))

        self.__pellet_size = max(2, round(self.__cell_size * 0.16))

        self.__big_pellet_size = max(4, round(self.__cell_size * 0.38))

        self.__player_speed = self.__cell_size * 2.5

    def __render_pellets(
        self: "GameScreen",
        display: GraphicsBackend,
        image: Image,
        pellets: set[GridPosition],
    ) -> None:
        """Render all remaining pellets."""
        if self.__pellet_image is None:
            return

        if self.__pellet_size is None:
            return

        for grid_position in pellets:
            center = self.__get_grid_position_center(
                grid_position
            )

            x = int(
                center.x - self.__pellet_size / 2
            )

            y = int(
                center.y - self.__pellet_size / 2
            )

            display.put_image(
                target=image,
                source=self.__pellet_image,
                x=x,
                y=y,
            )

    def __initialize_player_position(
        self: "GameScreen",
        player: PlayerModel,
    ) -> None:
        """Initialize continuous player position from the spawn cell."""

        if player.position is not None:
            return

        position = self.__get_grid_position_center(
            player.grid_position
        )

        player.move_to(position)

    def __update_player_movement(
        self: "GameScreen",
        player: PlayerModel,
        maze: MazeGrid,
        delta_time: float,
        pellets: set[GridPosition]
    ) -> None:
        """Move Pac-Man continuously through the maze."""

        if player.position is None:
            return

        distance = (
            self.__player_speed
            * player.speed_multiplier
            * delta_time
        )

        while distance > POSITION_EPSILON:
            current_cell_center = self.__get_grid_position_center(
                player.grid_position
            )

            if (
                not self.__positions_equal(
                    player.position,
                    current_cell_center,
                )
                and self.__is_opposite_direction(
                    first=player.direction,
                    second=player.requested_direction,
                )
            ):
                player.change_direction(player.requested_direction)

            if self.__positions_equal(
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
                    or not self.__can_move(
                        maze=maze,
                        position=player.grid_position,
                        direction=player.direction,
                    )
                ):
                    player.change_direction(Direction.NONE)
                    self.__pacman_sprite.stop()
                    return

            if self.__is_moving_toward_position(
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
                return

            target_grid_position = player.grid_position.moved(
                player.direction
            )

            target_position = self.__get_grid_position_center(
                target_grid_position
            )

            distance, reached_target = self.__move_player_towards(
                player=player,
                target=target_position,
                distance=distance,
            )

            if not reached_target:
                break

            player.move_to_grid(target_grid_position)

            if target_grid_position in pellets:
                pellets.remove(target_grid_position)

    def __try_change_direction(
        self: "GameScreen",
        player: PlayerModel,
        maze: MazeGrid,
    ) -> None:
        """Apply requested direction when movement is possible."""

        requested_direction = player.requested_direction

        if requested_direction == Direction.NONE:
            return

        if not self.__can_move(
            maze=maze,
            position=player.grid_position,
            direction=requested_direction,
        ):
            return

        player.change_direction(requested_direction)

    def __can_move(
        self: "GameScreen",
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

    def __is_opposite_direction(
        self: "GameScreen",
        first: Direction,
        second: Direction,
    ) -> bool:
        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }

        return opposite_directions.get(first) == second

    def __is_moving_toward_position(
        self: "GameScreen",
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

    def __move_player_towards(
        self: "GameScreen",
        player: PlayerModel,
        target: Position,
        distance: float,
    ) -> tuple[float, bool]:
        """Helper function, returning:
         how many movement budget we have left on this frame
         and have we reached the target location"""
        if player.position is None:
            return distance, False

        remaining_distance = self.__distance_to_target(
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

    def __render_pacman(
        self: "GameScreen",
        display: GraphicsBackend,
        image: Image,
        player: PlayerModel,
    ) -> None:
        """Render Pac-Man using his continuous position."""

        if player.position is None:
            return

        player_x = int(
            player.position.x - self.__player_size / 2
        )

        player_y = int(
            player.position.y - self.__player_size / 2
        )
        scale = (self.__player_size, self.__player_size)
        display.put_image(
            target=image,
            source=self.__pacman_sprite.current_image,
            x=player_x,
            y=player_y,
            scale=scale,
        )

    def __get_grid_position_center(
        self: "GameScreen",
        position: GridPosition,
    ) -> Position:
        """Return the screen-space center of a maze cell."""

        if (
            self.__cell_size is None
            or self.__offset_x is None
            or self.__offset_y is None
        ):
            raise RuntimeError(
                "Maze layout is not initialized"
            )

        return Position(
            x=(
                self.__offset_x
                + position.column * self.__cell_size
                + self.__cell_size / 2
            ),
            y=(
                self.__offset_y
                + position.row * self.__cell_size
                + self.__cell_size / 2
            ),
        )

    def __distance_to_target(
        self: "GameScreen",
        position: Position,
        target: Position,
    ) -> float:
        """Return axis-aligned distance to the target."""

        return (
            abs(target.x - position.x)
            + abs(target.y - position.y)
        )

    def __positions_equal(
        self: "GameScreen",
        first: Position,
        second: Position,
    ) -> bool:
        """Compare positions using floating-point tolerance."""

        return (
            abs(first.x - second.x) <= POSITION_EPSILON
            and abs(first.y - second.y) <= POSITION_EPSILON
        )

    def __render_cached_maze(
        self: "GameScreen",
        display: GraphicsBackend,
        image: Image,
        maze: MazeGrid,
    ) -> None:
        if (
            self.__cell_size is None or
            self.__offset_x is None or
            self.__offset_y is None
        ):
            return

        if self.__maze_image is None:
            self.__maze_image = display.new_image(
                image.width,
                image.height
            )

            display.clear(
                image=self.__maze_image,
                color=self._BACKGROUND_COLOR
            )

            self.__render_maze(
                display=display,
                image=self.__maze_image,
                maze=maze,
                cell_size=self.__cell_size,
                offset_x=self.__offset_x,
                offset_y=self.__offset_y,
            )

        display.put_image(
            target=image,
            source=self.__maze_image,
            x=0,
            y=0,
        )

    def __render_maze(
        self: "GameScreen",
        display: GraphicsBackend,
        image: Image,
        maze: MazeGrid,
        cell_size: int,
        offset_x: int,
        offset_y: int,
    ) -> None:
        """Render every wall in the current maze."""

        segments = self.__collect_wall_segments(
            maze=maze,
            cell_size=cell_size,
            offset_x=offset_x,
            offset_y=offset_y,
        )

        outer_thickness, inner_thickness = (
            self.__calculate_wall_thickness(
                cell_size
            )
        )

        for x0, y0, x1, y1 in segments:
            display.draw_line(
                image=image,
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                color=self._WALL_COLOR,
                thickness=outer_thickness,
                rounded=True,
            )

        for x0, y0, x1, y1 in segments:
            display.draw_line(
                image=image,
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                color=self._BACKGROUND_COLOR,
                thickness=inner_thickness,
                rounded=True,
            )

    def __collect_wall_segments(
        self: "GameScreen",
        maze: MazeGrid,
        cell_size: int,
        offset_x: int,
        offset_y: int,
    ) -> set[WallSegment]:
        """Collect unique wall segments from the maze."""

        segments: set[WallSegment] = set()

        for row_index, row in enumerate(maze):
            for column_index, cell in enumerate(row):
                left = (
                    offset_x
                    + column_index * cell_size
                )

                top = (
                    offset_y
                    + row_index * cell_size
                )

                right = left + cell_size
                bottom = top + cell_size

                if cell & Wall.NORTH:
                    segments.add(
                        self.__normalize_segment(
                            left,
                            top,
                            right,
                            top,
                        )
                    )

                if cell & Wall.EAST:
                    segments.add(
                        self.__normalize_segment(
                            right,
                            top,
                            right,
                            bottom,
                        )
                    )

                if cell & Wall.SOUTH:
                    segments.add(
                        self.__normalize_segment(
                            left,
                            bottom,
                            right,
                            bottom,
                        )
                    )

                if cell & Wall.WEST:
                    segments.add(
                        self.__normalize_segment(
                            left,
                            top,
                            left,
                            bottom,
                        )
                    )

        return segments

    def __normalize_segment(
        self: "GameScreen",
        x0: int,
        y0: int,
        x1: int,
        y1: int,
    ) -> WallSegment:
        """Return a segment with a stable point order."""

        start = (x0, y0)
        end = (x1, y1)

        if start <= end:
            return x0, y0, x1, y1

        return x1, y1, x0, y0

    def __calculate_wall_thickness(
        self: "GameScreen",
        cell_size: int,
    ) -> tuple[int, int]:
        """Calculate responsive odd wall thickness values."""

        outer_thickness = max(
            3,
            min(
                9,
                round(cell_size * 0.25),
            ),
        )

        if outer_thickness % 2 == 0:
            outer_thickness += 1

        inner_thickness = max(
            1,
            round(cell_size * 0.08),
        )

        if inner_thickness % 2 == 0:
            inner_thickness += 1

        if inner_thickness >= outer_thickness:
            inner_thickness = max(
                1,
                outer_thickness - 2,
            )

        return (
            outer_thickness,
            inner_thickness,
        )

    def __get_maze_size(
        self: "GameScreen",
        column_count: int,
        row_count: int,
        cell_size: int,
    ) -> tuple[int, int]:
        """Return maze dimensions in pixels."""

        return (
            column_count * cell_size,
            row_count * cell_size,
        )

    def __get_offsets(
        self: "GameScreen",
        image: Image,
        maze_width: int,
        maze_height: int,
    ) -> tuple[int, int]:
        """Return maze screen offsets."""

        return (
            (image.width - maze_width) // 2,
            (
                image.height
                - maze_height
                - self.__hud_height
            ) // 2,
        )

    def __render_error(
        self: "GameScreen",
        display: GraphicsBackend,
        image: Image,
        text: str,
    ) -> None:
        """Render a non-fatal game screen error."""

        display.write_text(
            text=text,
            image=image,
            font_size=self.__error_font_size,
            color=self._ERROR_COLOR,
            position=(
                self.__padding,
                self.__padding,
            ),
        )

    def __ensure_pellet_image(
        self: "GameScreen",
        display: GraphicsBackend,
    ) -> None:
        if self.__pellet_image is not None:
            return

        if self.__pellet_size is None:
            return

        self.__pellet_image = display.new_image(
            self.__pellet_size,
            self.__pellet_size,

        )

        display.clear(image=self.__pellet_image, color=PELLET_COLOR)

    def __ensure_pacman_scale(
        self: "GameScreen",
        display: "GraphicsBackend",
    ) -> None:
        if self.__player_size is None:
            return

        if self.__prepared_player_size == self.__player_size:
            return

        self.__pacman_sprite.prepare_scale(
            display=display,
            size=(
                self.__player_size,
                self.__player_size,
            ),
        )
