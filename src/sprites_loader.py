from pathlib import Path

from .graphics import GraphicsBackend
from .animation import AnimationClip, AnimatedSprite
from .models import GhostImages, GhostAssets, GhostKind, Direction


class SpritesLoader:
    def __init__(self: "SpritesLoader", display: GraphicsBackend) -> None:
        self._display = display

    def load_ghosts_sprites(self: "SpritesLoader") -> GhostAssets:
        assets_path = Path("assets/ghosts")
        ghosts: dict[GhostKind, GhostImages] = {
            GhostKind.BLINKY: self.__load_chase_mode(assets_path, "blinky"),
            GhostKind.INKY: self.__load_chase_mode(assets_path, "inky"),
            GhostKind.PINKY: self.__load_chase_mode(assets_path, "pinky"),
            GhostKind.CLYDE: self.__load_chase_mode(assets_path, "clyde"),
        }
        frightened = self._display.load_image(assets_path / "feared_1.xpm")
        return GhostAssets(
            ghosts=ghosts,
            frightened=frightened,
            frightened_warning=AnimatedSprite(
                animations={"all": self._display.load_animation(
                    paths=[
                        assets_path / "feared_1.xpm",
                        assets_path / "feared_2.xpm"
                        ],
                    frame_duration=1,
                    loop=True,
                )},
                initial_animation="all",
                playing=True,
            ),
            eaten={
                Direction.UP: self._display.load_image(
                    assets_path / "eaten_up.xpm"),
                Direction.DOWN: self._display.load_image(
                    assets_path / "eaten_down.xpm"),
                Direction.RIGHT: self._display.load_image(
                    assets_path / "eaten_right.xpm"),
                Direction.LEFT: self._display.load_image(
                    assets_path / "eaten_left.xpm")
            },
        )

    def load_pacman_animations(
        self: "SpritesLoader",
    ) -> dict[str, AnimationClip]:

        assets_path = Path("assets")

        animations = {
            "right": self._display.load_animation(
                paths=[
                    assets_path / "pacman-right/1.xpm",
                    assets_path / "pacman-right/2.xpm",
                    assets_path / "pacman-right/3.xpm",
                    assets_path / "pacman-right/2.xpm",
                    assets_path / "pacman-right/1.xpm",

                ],
                frame_duration=0.08
            ),
            "left": self._display.load_animation(
                paths=[
                    assets_path / "pacman-left/3.xpm",
                    assets_path / "pacman-left/2.xpm",
                    assets_path / "pacman-left/1.xpm",
                    assets_path / "pacman-left/2.xpm",
                    assets_path / "pacman-left/3.xpm"
                ],
                frame_duration=0.08
            ),
            "up": self._display.load_animation(
                paths=[
                    assets_path / "pacman-up/1.xpm",
                    assets_path / "pacman-up/2.xpm",
                    assets_path / "pacman-up/3.xpm",
                    assets_path / "pacman-up/2.xpm",
                    assets_path / "pacman-up/1.xpm",
                ],
                frame_duration=0.08
            ),
            "down": self._display.load_animation(
                paths=[
                    assets_path / "pacman-down/1.xpm",
                    assets_path / "pacman-down/2.xpm",
                    assets_path / "pacman-down/3.xpm",
                    assets_path / "pacman-down/2.xpm",
                    assets_path / "pacman-down/1.xpm"
                ],
                frame_duration=0.08
            )
        }

        return animations

    def __load_chase_mode(
        self: "SpritesLoader",
        assets_path: Path,
        name: str,
    ) -> GhostImages:
        ghost_path = assets_path / name
        return GhostImages(
            chase={
                    Direction.UP: self._display.load_image(
                        ghost_path / f"{name}_up.xpm"),
                    Direction.DOWN: self._display.load_image(
                        ghost_path / f"{name}_down.xpm"),
                    Direction.RIGHT: self._display.load_image(
                        ghost_path / f"{name}_right.xpm"),
                    Direction.LEFT: self._display.load_image(
                        ghost_path / f"{name}_left.xpm")
                }
            )
