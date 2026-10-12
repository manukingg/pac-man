from ...graphics import GraphicsBackend, Image
from ...models import PlayerModel
from ...animation import AnimatedSprite


class PlayerRenderer:
    def __init__(
        self: "PlayerRenderer",
        pacman_sprite: AnimatedSprite,
    ) -> None:
        self.__pacman_sprite = pacman_sprite
        self.__prepared_player_size: int | None = None

    def render(
        self: "PlayerRenderer",
        display: GraphicsBackend,
        image: Image,
        player: PlayerModel,
        player_size: int,
    ) -> None:
        """Render Pac-Man using his continuous position."""

        if player.position is None:
            return

        self.__ensure_scale(
            display=display,
            player_size=player_size,
        )

        player_x = int(
            player.position.x - player_size / 2
        )

        player_y = int(
            player.position.y - player_size / 2
        )
        display.put_image(
            target=image,
            source=self.__pacman_sprite.current_image,
            x=player_x,
            y=player_y,
            scale=(
                player_size,
                player_size,
            ),
        )

    def invalidate(self: "PlayerRenderer") -> None:
        self.__prepared_player_size = None

    def __ensure_scale(
        self: "PlayerRenderer",
        display: GraphicsBackend,
        player_size: int,
    ) -> None:
        if self.__prepared_player_size == player_size:
            return

        self.__pacman_sprite.prepare_scale(
            display=display,
            size=(
                player_size,
                player_size,
            ),
        )
        self.__prepared_player_size = player_size
