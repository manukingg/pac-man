from ...graphics import Image, GraphicsBackend
from ...models import MazeGrid, Wall

from .game_layout import GameLayout


Color = tuple[int, int, int]
WallSegment = tuple[int, int, int, int]


class MazeRenderer:
    def __init__(
        self: "MazeRenderer",
        background_color: Color,
        wall_color: Color,
        ft_color: Color,
    ) -> None:
        self.__background_color = background_color
        self.__wall_color = wall_color
        self.__ft_color = ft_color

        self.__maze_image: Image | None = None
        self.__maze: MazeGrid | None = None

    def render(
        self: "MazeRenderer",
        display: GraphicsBackend,
        image: Image,
        maze: MazeGrid,
        layout: GameLayout,
    ) -> None:
        if self.__maze_image is None or self.__maze is not maze:
            self.__maze_image = display.new_image(
                image.width,
                image.height
            )

            display.clear(
                image=self.__maze_image,
                color=self.__background_color
            )

            self.__render_maze(
                display=display,
                image=self.__maze_image,
                maze=maze,
                layout=layout
            )

            self.__maze = maze

        display.put_image(
            target=image,
            source=self.__maze_image,
            x=0,
            y=0,
        )

    def invalidate(self: "MazeRenderer") -> None:
        self.__maze_image = None

    def __render_maze(
        self: "MazeRenderer",
        display: GraphicsBackend,
        image: Image,
        maze: MazeGrid,
        layout: GameLayout,
    ) -> None:
        """Render every wall in the current maze."""

        self.__render_42_cells(
            display=display,
            image=image,
            maze=maze,
            layout=layout,
        )

        segments = self.__collect_wall_segments(
            maze=maze,
            layout=layout
        )

        outer_thickness, inner_thickness = (
            self.__calculate_wall_thickness(
                layout.cell_size,
            )
        )

        for x0, y0, x1, y1 in segments:
            display.draw_line(
                image=image,
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                color=self.__wall_color,
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
                color=self.__background_color,
                thickness=inner_thickness,
                rounded=True,
            )

    def __collect_wall_segments(
        self: "MazeRenderer",
        maze: MazeGrid,
        layout: GameLayout,
    ) -> set[WallSegment]:
        """Collect unique wall segments from the maze."""

        segments: set[WallSegment] = set()

        cell_size = layout.cell_size
        offset_x = layout.offset_x
        offset_y = layout.offset_y

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

                current_is_42 = self.__is_42_cell(
                    maze=maze,
                    row=row_index,
                    column=column_index,
                )

                if (cell & Wall.NORTH and
                    not (current_is_42 and self.__is_42_cell(
                                               maze,
                                               row_index-1,
                                               column_index))):
                    segments.add(
                        self.__normalize_segment(
                            left,
                            top,
                            right,
                            top,
                        )
                    )

                if (cell & Wall.EAST and
                    not (current_is_42 and self.__is_42_cell(
                                                maze,
                                                row_index,
                                                column_index + 1))):
                    segments.add(
                        self.__normalize_segment(
                            right,
                            top,
                            right,
                            bottom,
                        )
                    )

                if (cell & Wall.SOUTH and
                    not (current_is_42 and self.__is_42_cell(
                                            maze,
                                            row_index + 1,
                                            column_index))):
                    segments.add(
                        self.__normalize_segment(
                            left,
                            bottom,
                            right,
                            bottom,
                        )
                    )

                if (cell & Wall.WEST and
                    not (current_is_42 and self.__is_42_cell(
                        maze,
                        row_index,
                        column_index - 1))):
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
        self: "MazeRenderer",
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
        self: "MazeRenderer",
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

    def __render_42_cells(
        self: "MazeRenderer",
        display: GraphicsBackend,
        image: Image,
        maze: MazeGrid,
        layout: GameLayout,
    ) -> None:
        cell_size = layout.cell_size
        offset_x = layout.offset_x
        offset_y = layout.offset_y

        for row_index, row in enumerate(maze):
            for column_index, cell in enumerate(row):
                if cell != 15:
                    continue

                x = offset_x + column_index * cell_size
                y = offset_y + row_index * cell_size

                display.draw_rect(
                    image=image,
                    x=x,
                    y=y,
                    width=cell_size,
                    height=cell_size,
                    color=self.__ft_color,
                )

    def __is_42_cell(
        self: "MazeRenderer",
        maze: MazeGrid,
        row: int,
        column: int,
    ) -> bool:
        if not (0 <= row < len(maze)):
            return False

        if not (0 <= column < len(maze[0])):
            return False

        return maze[row][column] == 15
