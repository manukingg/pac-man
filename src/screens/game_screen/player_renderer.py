from ...graphics import GraphicsBackend, Image
from ...models import PlayerModel, GameState, GamePhase
from ...animation import AnimatedSprite
from ...constants import (
    PLAYER_DEATH_FREEZE_DURATION,
    PLAYER_DEATH_FRAME_DURATION,
    PLAYER_RESPAWN_BLINK_INTERVAL_1,
    PLAYER_RESPAWN_BLINK_INTERVAL_2,
    PLAYER_RESPAWN_BLINK_TRESHOLD,
)


class PlayerRenderer:
    def __init__(
        self: "PlayerRenderer",
        pacman_sprite: AnimatedSprite,
        pacman_death_images: tuple[Image]
    ) -> None:
        self.__pacman_sprite = pacman_sprite
        self.__prepared_player_size: int | None = None
        self.__death_images = pacman_death_images

    def render(
        self: "PlayerRenderer",
        display: GraphicsBackend,
        image: Image,
        player: PlayerModel,
        player_size: int,
        game_state: GameState,
    ) -> None:
        """Render Pac-Man using his continuous position."""

        if player.position is None:
            return

        if (
            game_state.phase == GamePhase.PLAYER_DEATH
            and game_state.phase_elapsed >= PLAYER_DEATH_FREEZE_DURATION
        ):
            self.__pacman_sprite.reset()

        if not self.__is_player_visible(game_state):
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

        player_image = self.__get_player_image(game_state=game_state)

        display.put_image(
            target=image,
            source=player_image,
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

    def __get_player_image(
        self: "PlayerRenderer",
        game_state: GameState,
    ) -> Image:
        if game_state.phase != GamePhase.PLAYER_DEATH:
            return self.__pacman_sprite.current_image

        elapsed = game_state.phase_elapsed

        if elapsed < PLAYER_DEATH_FREEZE_DURATION:
            return self.__pacman_sprite.current_image

        animation_elapsed = elapsed - PLAYER_DEATH_FREEZE_DURATION

        frame_index = int(
            animation_elapsed / PLAYER_DEATH_FRAME_DURATION
        )

        frame_index = min(frame_index, len(self.__death_images) - 1)

        return self.__death_images[frame_index]

    def __is_player_visible(
        self: "PlayerRenderer",
        game_state: GameState,
    ) -> bool:
        if game_state.phase != GamePhase.PLAYER_RESPAWN:
            return True

        interval = PLAYER_RESPAWN_BLINK_INTERVAL_1

        if (
            game_state.phase_elapsed
            >= PLAYER_RESPAWN_BLINK_TRESHOLD
        ):
            interval -= PLAYER_RESPAWN_BLINK_INTERVAL_2

        blink_index = int(
            game_state.phase_elapsed
            / interval
        )

        return blink_index % 2 == 0
