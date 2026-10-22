from ...graphics import GraphicsBackend, Image
from ...models import GridPosition

from .game_layout import GameLayout


Color = tuple[int, int, int]

POWER_PELLET_BLINK_INTERVAL: float = 0.15
PELLET_COLOR: Color = (255, 220, 180)


class PelletRenderer:
    def __init__(self: "PelletRenderer") -> None:
        self.__pellet_image: Image | None = None
        self.__pellet_size: int | None = None

        self.__power_pellet_image: Image | None = None
        self.__power_pellet_size: int | None = None

        self.__power_pellet_visible: bool = True
        self.__power_pellet_blink_timer = 0.0

    def render(
        self: "PelletRenderer",
        display: GraphicsBackend,
        image: Image,
        pellets: set[GridPosition],
        power_pellets: set[GridPosition],
        layout: GameLayout,
    ) -> None:
        """Render all remaining pellets."""
        self.__ensure_pellet_image(
            display=display,
            pellet_size=layout.pellet_size,
            power_pellet_size=layout.power_pellet_size,
        )
        if self.__pellet_image is None or self.__power_pellet_image is None:
            return

        self.__render_pellets(
            pellets=pellets,
            display=display,
            layout=layout,
            image=image,
        )

        if self.__power_pellet_visible:
            self.__render_power_pellets(
                power_pellets=power_pellets,
                display=display,
                layout=layout,
                image=image,
            )

    def update(
        self: "PelletRenderer",
        delta_time: float,
    ) -> None:
        self.__power_pellet_blink_timer += delta_time

        while self.__power_pellet_blink_timer >= POWER_PELLET_BLINK_INTERVAL:
            self.__power_pellet_blink_timer -= POWER_PELLET_BLINK_INTERVAL

            self.__power_pellet_visible = not self.__power_pellet_visible

    def invalidate(self: "PelletRenderer") -> None:
        self.__pellet_image = None
        self.__pellet_size = None
        self.__power_pellet_image = None
        self.__power_pellet_size = None

    def __render_pellets(
        self: "PelletRenderer",
        pellets: set[GridPosition],
        display: GraphicsBackend,
        layout: GameLayout,
        image: Image,
    ) -> None:
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

    def __render_power_pellets(
        self: "PelletRenderer",
        power_pellets: set[GridPosition],
        display: GraphicsBackend,
        layout: GameLayout,
        image: Image,
    ) -> None:
        for grid_position in power_pellets:
            center = layout.get_grid_position_center(
                grid_position
            )

            x = int(
                center.x - self.__power_pellet_size / 2
            )

            y = int(
                center.y - self.__power_pellet_size / 2
            )

            display.put_image(
                target=image,
                source=self.__power_pellet_image,
                x=x,
                y=y,
            )

    def __ensure_pellet_image(
        self: "PelletRenderer",
        display: GraphicsBackend,
        pellet_size: int,
        power_pellet_size: int,
    ) -> None:
        if (
            self.__pellet_image is not None
            and self.__pellet_size == pellet_size
            and self.__power_pellet_image is not None
            and self.__power_pellet_size == power_pellet_size
        ):
            return

        self.__pellet_image = display.new_image(
            pellet_size,
            pellet_size,
        )

        display.clear(image=self.__pellet_image, color=PELLET_COLOR)

        self.__pellet_size = pellet_size

        self.__power_pellet_image = display.new_image(
            power_pellet_size,
            power_pellet_size,
        )

        display.draw_filled_circle(
            image=self.__power_pellet_image,
            center_x=power_pellet_size // 2,
            center_y=power_pellet_size // 2,
            radius=max(1, power_pellet_size // 2),
            color=PELLET_COLOR,
        )

        self.__power_pellet_size = power_pellet_size
