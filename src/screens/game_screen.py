from ..graphics import Display
from ..models import AppState, Wall

from .screen import Screen


class GameScreen(Screen):
    """Render and control the current game session."""

    _BACKGROUND_COLOR = 0x000000
    _WALL_COLOR = 0x0000FF
    _ERROR_COLOR = 0xFF4040
    _PADDING = 24

    def handle_event(
        self: "GameScreen",
        event: object,
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
        display: Display,
        state: AppState,
    ) -> None:
        """Render the current maze."""

        game_state = state.game_state

        if game_state is None:
            self.__render_error(
                display=display,
                text="GAME STATE IS NOT INITIALIZED",
            )
            return

        maze = game_state.maze

        if not maze or not maze[0]:
            self.__render_error(
                display=display,
                text="MAZE IS EMPTY",
            )
            return

        self.__render_maze(
            display=display,
            state=state,
        )

    def __render_maze(
        self: "GameScreen",
        display: Display,
        state: AppState,
    ) -> None:
        """Render every wall in the current maze."""

        game_state = state.game_state

        if game_state is None:
            return

        maze = game_state.maze
        row_count = len(maze)
        column_count = len(maze[0])

        cell_size = self.__calculate_cell_size(
            window_width=state.config.window_width,
            window_height=state.config.window_height,
            row_count=row_count,
            column_count=column_count,
        )

        if cell_size <= 0:
            self.__render_error(
                display=display,
                text="MAZE DOES NOT FIT THE WINDOW",
            )
            return

        maze_width = column_count * cell_size
        maze_height = row_count * cell_size

        offset_x = (
            state.config.window_width - maze_width
        ) // 2

        offset_y = (
            state.config.window_height - maze_height
        ) // 2

        for row_index, row in enumerate(maze):
            for column_index, cell in enumerate(row):
                self.__render_cell(
                    display=display,
                    cell=cell,
                    row=row_index,
                    column=column_index,
                    cell_size=cell_size,
                    offset_x=offset_x,
                    offset_y=offset_y,
                )

    def __render_cell(
        self: "GameScreen",
        display: Display,
        cell: int,
        row: int,
        column: int,
        cell_size: int,
        offset_x: int,
        offset_y: int,
    ) -> None:
        """Render the walls of one maze cell."""

        left = offset_x + column * cell_size
        top = offset_y + row * cell_size
        right = left + cell_size
        bottom = top + cell_size

        if cell & Wall.NORTH:
            display.draw_line(
                x1=left,
                y1=top,
                x2=right,
                y2=top,
                color=self._WALL_COLOR,
            )

        if cell & Wall.EAST:
            display.draw_line(
                x1=right,
                y1=top,
                x2=right,
                y2=bottom,
                color=self._WALL_COLOR,
            )

        if cell & Wall.SOUTH:
            display.draw_line(
                x1=left,
                y1=bottom,
                x2=right,
                y2=bottom,
                color=self._WALL_COLOR,
            )

        if cell & Wall.WEST:
            display.draw_line(
                x1=left,
                y1=top,
                x2=left,
                y2=bottom,
                color=self._WALL_COLOR,
            )

    def __calculate_cell_size(
        self: "GameScreen",
        window_width: int,
        window_height: int,
        row_count: int,
        column_count: int,
    ) -> int:
        """Calculate the largest cell size fitting the window."""

        available_width = window_width - self._PADDING * 2
        available_height = window_height - self._PADDING * 2

        cell_width = available_width // column_count
        cell_height = available_height // row_count

        return min(cell_width, cell_height)

    def __render_error(
        self: "GameScreen",
        display: Display,
        text: str,
    ) -> None:
        """Render a non-fatal game screen error."""

        display.draw_text(
            x=self._PADDING,
            y=self._PADDING,
            text=text,
            color=self._ERROR_COLOR,
        )
