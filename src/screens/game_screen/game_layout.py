from dataclasses import dataclass

from ...graphics import Image
from ...models import GridPosition, Position, MazeGrid


@dataclass
class GameLayout:
    cell_size: int | None = None
    offset_x: int | None = None
    offset_y: int | None = None

    padding: int | None = None
    hud_height: int | None = None
    error_font_size: int | None = None

    player_size: int | None = None
    player_speed: float | None = None

    pellet_size: int | None = None
    big_pellet_size: int | None = None

    def update(
        self: "GameLayout",
        image: Image,
        maze: MazeGrid,
    ) -> bool:
        row_count = len(maze)
        column_count = len(maze[0])

        self.update_screen_metrics(image)

        cell_size = self.__calculate_cell_size(
            image_width=image.width,
            image_height=image.height,
            row_count=row_count,
            column_count=column_count,
        )

        if cell_size <= 0:
            self.cell_size = None
            self.offset_x = None
            self.offset_y = None

            self.player_size = None
            self.player_speed = None
            self.pellet_size = None
            self.big_pellet_size = None

            return False

        self.cell_size = cell_size

        self.__calculate_game_metrics()

        maze_width, maze_height = self.__get_maze_size(
            column_count=column_count,
            row_count=row_count,
        )

        self.offset_x, self.offset_y = self.__get_offsets(
            image=image,
            maze_width=maze_width,
            maze_height=maze_height,
        )

        return True

    def get_grid_position_center(
        self: "GameLayout",
        position: GridPosition,
    ) -> Position:
        if (
            self.cell_size is None
            or self.offset_x is None
            or self.offset_y is None
        ):
            raise RuntimeError("Game layout is not initialized")
        return Position(
            x=(
                self.offset_x
                + position.column * self.cell_size
                + self.cell_size / 2
            ),
            y=(
                self.offset_y
                + position.row * self.cell_size
                + self.cell_size / 2
            ),
        )

    def reset(self: "GameLayout") -> None:
        self.cell_size = None
        self.offset_x = None
        self.offset_y = None

        self.padding = None
        self.hud_height = None
        self.error_font_size = None

        self.player_size = None
        self.player_speed = None

        self.pellet_size = None
        self.big_pellet_size = None

    def update_screen_metrics(
        self: "GameLayout",
        image: Image,
    ) -> None:
        shortest_side = min(
            image.width,
            image.height,
        )

        self.padding = max(12, round(shortest_side * 0.025))

        self.hud_height = max(60, round(image.height * 0.12))

        self.error_font_size = max(2, round(shortest_side / 400))

    def __calculate_cell_size(
        self: "GameLayout",
        image_width: int,
        image_height: int,
        row_count: int,
        column_count: int,
    ) -> int:
        if self.padding is None:
            raise RuntimeError("Layout padding is not initialized")
        if self.hud_height is None:
            raise RuntimeError("Layout HUD height is not initialized")

        available_width = image_width - self.padding * 2

        available_height = (
            image_height - self.padding * 2 - self.hud_height)

        cell_width = available_width // column_count

        cell_height = available_height // row_count

        return min(cell_width, cell_height)

    def __calculate_game_metrics(self: "GameLayout") -> None:
        if self.cell_size is None:
            return

        self.player_size = max(8, round(self.cell_size * 0.72))

        self.pellet_size = max(2, round(self.cell_size * 0.10))

        self.big_pellet_size = max(4, round(self.cell_size * 0.25))

        self.player_speed = self.cell_size * 2.5

    def __get_maze_size(
        self: "GameLayout",
        column_count: int,
        row_count: int,
    ) -> tuple[int, int]:
        """Return maze dimensions in pixels."""
        if self.cell_size is None:
            raise RuntimeError("Cell size is not initialized")

        return (
            column_count * self.cell_size,
            row_count * self.cell_size,
        )

    def __get_offsets(
        self: "GameLayout",
        image: Image,
        maze_width: int,
        maze_height: int,
    ) -> tuple[int, int]:
        """Return maze screen offsets."""
        if self.hud_height is None:
            raise RuntimeError("HUD height is not initialized")

        return (
            (image.width - maze_width) // 2,
            (
                image.height
                - maze_height
                - self.hud_height
            ) // 2,
        )
