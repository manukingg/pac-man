from ...models import GhostAssets, GhostModel, GhostMode, Direction
from ...graphics import GraphicsBackend, Image


class GhostsRenderer:
    def __init__(
        self: "GhostsRenderer",
        ghosts_sprites: GhostAssets,
    ) -> None:
        self.__ghost_sprites: GhostAssets = ghosts_sprites
        self.__prepared_scale: int | None = None

    def render(
        self: "GhostsRenderer",
        display: GraphicsBackend,
        image: Image,
        ghosts: list[GhostModel],
        ghosts_size: int,
    ) -> None:
        self.__ensure_scale(
            display=display,
            ghosts_size=ghosts_size
        )

        for ghost in ghosts:
            if ghost.position is None:
                continue
            image_to_put = self.__choose_ghost_sprite(ghost)
            if image_to_put is None:
                continue
            x = round(ghost.position.x - ghosts_size / 2)
            y = round(ghost.position.y - ghosts_size / 2)
            display.put_image(
                target=image,
                source=image_to_put,
                x=x,
                y=y,
                scale=(ghosts_size, ghosts_size),
            )

    def __choose_ghost_sprite(
        self: "GhostsRenderer",
        ghost: GhostModel,
    ) -> Image | None:
        if ghost.mode == GhostMode.FRIGHTENED:
            if 0 < ghost.frightened_time_remaining < 1:
                return self.__ghost_sprites.frightened_warning.current_image

            return self.__ghost_sprites.frightened

        if ghost.direction == Direction.NONE:
            return None

        if ghost.mode == GhostMode.EATEN:
            return self.__ghost_sprites.eaten[ghost.direction]

        ghost_image = self.__ghost_sprites.ghosts[ghost.kind]
        return ghost_image.chase[ghost.direction]

    def invalidate(self: "GhostsRenderer") -> None:
        self.__prepared_scale = None

    def __ensure_scale(
        self: "GhostsRenderer",
        display: GraphicsBackend,
        ghosts_size: int,
    ) -> None:
        if self.__prepared_scale == ghosts_size:
            return
        self.__ghost_sprites.prepare_scale(
            display=display,
            size=(
                ghosts_size,
                ghosts_size,
            )
        )
        self.__prepared_scale = ghosts_size
