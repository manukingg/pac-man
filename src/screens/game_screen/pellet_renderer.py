from ...graphics import GraphicsBackend, Image
from ...models import GridPosition

from .game_layout import GameLayout


Color = tuple[int, int, int]

PELLET_COLOR: Color = (255, 220, 180)


class PelletRenderer:
    def __init__(self: "PelletRenderer") -> None:
        self.__pellet_image: Image | None = None
        self.__pellet_size: int | None = None

    def render(
        self: "PelletRenderer",
        display: GraphicsBackend,
        image: Image,
        pellets: set[GridPosition],
        layout: GameLayout,
    ) -> None:
        """Render all remaining pellets."""
        self.__ensure_pellet_image(
            display=display,
            pellet_size=layout.pellet_size,
        )
        if self.__pellet_image is None:
            return

        for grid_position in pellets:
            center = layout.get_grid_position_center(
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

    def invalidate(self: "PelletRenderer") -> None:
        self.__pellet_image = None
        self.__pellet_size = None

    def __ensure_pellet_image(
        self: "PelletRenderer",
        display: GraphicsBackend,
        pellet_size: int,
    ) -> None:
        if (
            self.__pellet_image is not None
            and self.__pellet_size == pellet_size
        ):
            return

        self.__pellet_image = display.new_image(
            pellet_size,
            pellet_size,
        )

        display.clear(image=self.__pellet_image, color=PELLET_COLOR)

        self.__pellet_size = pellet_size
