from ..animation import AnimatedSprite
from ..graphics import (
    Image,
    PygameWrapper,
    GraphicsEvent,
    EventType,
    Key,
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
from ..graphics import Image, GraphicsBackend
from ..graphics.events import GraphicsEvent
from ..models import AppState, Wall

from .screen import Screen


Color = tuple[int, int, int]
WallSegment = tuple[int, int, int, int]

HUD_HEIGHT = 140
PLAYER_SIZE = 48
PLAYER_SPEED = 205.0
POSITION_EPSILON = 0.001


class GameScreen(Screen):
    """Render and control the current game session."""

    _BACKGROUND_COLOR: Color = (0, 0, 0)
    _WALL_COLOR: Color = (32, 88, 255)
    _ERROR_COLOR: Color = (255, 64, 64)

    _PADDING = 24
    _ERROR_FONT_SIZE = 2

    def __init__(
        self: "GameScreen",
        pacman_sprite: AnimatedSprite,
    ) -> None:
        self.__pacman_sprite = pacman_sprite
        self.__maze_image: Image | None = None

        self.__cell_size: int | None = None
        self.__offset_x: int | None = None
        self.__offset_y: int | None = None

    def handle_event(
        self: "GameScreen",
        event: GraphicsEvent,
        state: AppState,
    ) -> None:
        """Handle gameplay input."""

        if event.type != EventType.KEY_DOWN:
            return

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

        row_count = len(maze)
        column_count = len(maze[0])

        cell_size = self.__calculate_cell_size(
            image_width=image.width,
            image_height=image.height,
            row_count=row_count,
            column_count=column_count,
        )

        if cell_size <= 0:
            self.__render_error(
                display=display,
                image=image,
                text="MAZE DOES NOT FIT THE WINDOW",
            )
            return

        maze_width, maze_height = self.__get_maze_size(
            column_count=column_count,
            row_count=row_count,
            cell_size=cell_size,
        )

        offset_x, offset_y = self.__get_offsets(
            image=image,
            maze_width=maze_width,
            maze_height=maze_height,
        )

        self.__cell_size = cell_size
        self.__offset_x = offset_x
        self.__offset_y = offset_y

        if self.__maze_image is None:
            self.__maze_image = display.new_image(
                image.width,
                image.height,
            )

            display.clear(
                image=self.__maze_image,
                color=self._BACKGROUND_COLOR,
            )

            self.__render_maze(
                display=display,
                image=self.__maze_image,
                maze=maze,
                cell_size=cell_size,
                offset_x=offset_x,
                offset_y=offset_y,
            )

        display.put_image(
            target=image,
            source=self.__maze_image,
            x=0,
            y=0,
        )

        self.__initialize_player_position(
            player=game_state.player,
        )
        print(game_state.player.grid_position)

        self.__render_pacman(
            display=display,
            image=image,
            player=game_state.player,
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
    ) -> None:
        """Move Pac-Man continuously through the maze."""

        if player.position is None:
            return

        distance = (
            PLAYER_SPEED
            * player.speed_multiplier
            * delta_time
        )

        while distance > POSITION_EPSILON:
            current_cell_center = self.__get_grid_position_center(
                player.grid_position
            )

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

            if player.direction == Direction.NONE:
                self.__pacman_sprite.stop()
                return

            target_grid_position = player.grid_position.moved(
                player.direction
            )

            target_position = self.__get_grid_position_center(
                target_grid_position
            )

            remaining_distance = self.__distance_to_target(
                position=player.position,
                target=target_position,
            )

            if remaining_distance <= POSITION_EPSILON:
                player.move_to(target_position)
                player.move_to_grid(target_grid_position)
                continue

            step = min(
                distance,
                remaining_distance,
            )

            player.move_to(
                player.position.moved(
                    direction=player.direction,
                    distance=step,
                )
            )

            self.__pacman_sprite.play(
                animation=player.direction.name.lower(),
            )

            distance -= step

            if step + POSITION_EPSILON < remaining_distance:
                break

            player.move_to(target_position)
            player.move_to_grid(target_grid_position)

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

    def __render_pacman(
        self: "GameScreen",
        display: PygameWrapper,
        image: Image,
        player: PlayerModel,
    ) -> None:
        """Render Pac-Man using his continuous position."""

        if player.position is None:
            return

        player_x = int(
            player.position.x - PLAYER_SIZE / 2
        )

        player_y = int(
            player.position.y - PLAYER_SIZE / 2
        )

        display.put_image(
            target=image,
            source=self.__pacman_sprite.current_image,
            x=player_x,
            y=player_y,
            scale=(PLAYER_SIZE, PLAYER_SIZE),
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

    def __render_maze(
        self: "GameScreen",
        display: PygameWrapper,
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

    def __calculate_cell_size(
        self: "GameScreen",
        image_width: int,
        image_height: int,
        row_count: int,
        column_count: int,
    ) -> int:
        """Calculate the largest cell size fitting the image."""

        available_width = (
            image_width
            - self._PADDING * 2
        )

        available_height = (
            image_height
            - self._PADDING * 2
            - HUD_HEIGHT
        )

        cell_width = (
            available_width
            // column_count
        )

        cell_height = (
            available_height
            // row_count
        )

        return min(
            cell_width,
            cell_height,
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
                - HUD_HEIGHT
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
            font_size=self._ERROR_FONT_SIZE,
            color=self._ERROR_COLOR,
            position=(
                self._PADDING,
                self._PADDING,
            ),
        )