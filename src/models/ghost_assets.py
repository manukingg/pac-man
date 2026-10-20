from dataclasses import dataclass

from ..graphics import Image, GraphicsBackend
from ..models import Direction
from .ghost import GhostKind
from ..animation import AnimatedSprite


@dataclass(frozen=True, slots=True)
class GhostImages:
    chase: dict[Direction, Image]


@dataclass(frozen=True, slots=True)
class GhostAssets:
    ghosts: dict[GhostKind, GhostImages]

    frightened: Image
    frightened_warning: AnimatedSprite

    eaten: dict[Direction, Image]

    def prepare_scale(
        self: "GhostAssets",
        display: GraphicsBackend,
        size: tuple[int, int],
    ) -> None:
        width, height = size

        for _, image in self.ghosts.items():
            display.prepare_scaled_image(
                image.chase.get(Direction.DOWN),
                width,
                height
            )
            display.prepare_scaled_image(
                image.chase.get(Direction.UP),
                width,
                height
            )
            display.prepare_scaled_image(
                image.chase.get(Direction.RIGHT),
                width,
                height
            )
            display.prepare_scaled_image(
                image.chase.get(Direction.LEFT),
                width,
                height
            )

        for _, image in self.eaten.items():
            display.prepare_scaled_image(
                image,
                width,
                height,
            )
        display.prepare_scaled_image(
            self.frightened,
            width,
            height,
        )
        for image in self.frightened_warning.get_current_animation_images:
            display.prepare_scaled_image(
                image,
                width,
                height,
            )
