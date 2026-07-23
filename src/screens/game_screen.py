from ..graphics import Image, PygameWrapper
from ..graphics.events import GraphicsEvent
from ..models import AppState, Wall

from .screen import Screen


Color = tuple[int, int, int]
WallSegment = tuple[int, int, int, int]


class GameScreen(Screen):
    """Render and control the current game session."""

    _BACKGROUND_COLOR: Color = (0, 0, 0)
    _WALL_COLOR: Color = (32, 88, 255)
    _ERROR_COLOR: Color = (255, 64, 64)
    _PADDING = 24
    _ERROR_FONT_SIZE = 2

    def handle_event(
        self: "GameScreen",
        event: GraphicsEvent,
        state: AppState,
    ) -> None:
        """Handle gameplay input."""

    def update(
        self: "GameScreen",
        delta_time: float,
        state: AppState,
    ) -> None:
        """Update the current game session."""

    def render(
        self: "GameScreen",
        display: PygameWrapper,
        image: Image,
        state: AppState,
    ) -> None:
        """Render the current maze."""

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

        self.__render_maze(
            display=display,
            image=image,
            maze=maze,
        )

    def __render_maze(
        self: "GameScreen",
        display: PygameWrapper,
        image: Image,
        maze: list[list[int]],
    ) -> None:
        """Render every wall in the current maze."""

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

        maze_width = column_count * cell_size
        maze_height = row_count * cell_size

        offset_x = (image.width - maze_width) // 2
        offset_y = (image.height - maze_height) // 2

        segments = self.__collect_wall_segments(
            maze=maze,
            cell_size=cell_size,
            offset_x=offset_x,
            offset_y=offset_y,
        )

        outer_thickness, inner_thickness = (
            self.__calculate_wall_thickness(cell_size)
        )

        # Первый проход: толстая синяя основа.
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

        # Второй проход: вырезаем чёрную середину.
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
        maze: list[list[int]],
        cell_size: int,
        offset_x: int,
        offset_y: int,
    ) -> set[WallSegment]:
        """Collect unique wall segments from the maze."""

        segments: set[WallSegment] = set()

        for row_index, row in enumerate(maze):
            for column_index, cell in enumerate(row):
                left = offset_x + column_index * cell_size
                top = offset_y + row_index * cell_size
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
            min(9, round(cell_size * 0.25)),
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

        return outer_thickness, inner_thickness

    def __calculate_cell_size(
        self: "GameScreen",
        image_width: int,
        image_height: int,
        row_count: int,
        column_count: int,
    ) -> int:
        """Calculate the largest cell size fitting the image."""

        available_width = image_width - self._PADDING * 2
        available_height = image_height - self._PADDING * 2

        cell_width = available_width // column_count
        cell_height = available_height // row_count

        return min(cell_width, cell_height)

    def __render_error(
        self: "GameScreen",
        display: PygameWrapper,
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
