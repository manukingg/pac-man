from ...models import GhostAssets, GhostModel, GhostKind
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
        for ghost in ghosts:
            if ghost.position is None:
                continue
            image_to_put = self.__choose_ghost_sprite(ghost, ghost_size)

    def __choose_ghost_sprite(
        self: "GhostsRenderer",
        ghost: GhostModel,
        ghost_size: int,
    ) -> Image:
