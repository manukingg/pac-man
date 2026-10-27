from ...models import (
    GhostAssets,
    GhostModel,
    GhostMode,
    Direction,
    GameState,
)
from ...graphics import GraphicsBackend, Image

RESPAWN_BLINK_INTERVAL = 0.2


class GhostsRenderer:
    def __init__(
        self: "GhostsRenderer",
        ghosts_sprites: GhostAssets,
    ) -> None:
        self.__ghost_sprites: GhostAssets = ghosts_sprites
        self.__prepared_scale: int | None = None
        self.__warning_active: bool = False

    def render(
        self: "GhostsRenderer",
        display: GraphicsBackend,
        image: Image,
        ghosts: list[GhostModel],
        ghosts_size: int,
        game_state: GameState,
    ) -> None:
        self.__ensure_scale(
            display=display,
            ghosts_size=ghosts_size
        )

        for ghost in ghosts:
            if ghost.position is None:
                continue

            if (
                game_state.score_popup is not None
                and ghost.kind == game_state.score_popup.ghost_kind
            ):
                continue

            if not self.__is_respawning_visible(ghost):
                continue

            image_to_put = self.__choose_ghost_sprite(ghost, game_state)

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

    def update(
        self: "GhostsRenderer",
        ghosts: list[GhostModel],
        delta_time: float,
        game_state: GameState,
    ) -> None:
        warning_active = (
            0 < game_state.power_mode_remaining < 1
            and any(
                ghost.mode == GhostMode.FRIGHTENED
                for ghost in ghosts
            )
        )

        if warning_active and not self.__warning_active:
            self.__ghost_sprites.frightened_warning.reset()

        if warning_active:
            self.__ghost_sprites.frightened_warning.update(delta_time)

        self.__warning_active = warning_active

    def __choose_ghost_sprite(
        self: "GhostsRenderer",
        ghost: GhostModel,
        game_state: GameState
    ) -> Image | None:
        if ghost.mode == GhostMode.FRIGHTENED:

            if 0 < game_state.power_mode_remaining < 1:
                return self.__ghost_sprites.frightened_warning.current_image

            return self.__ghost_sprites.frightened

        if ghost.mode == GhostMode.RESPAWNING:
            ghost_image = (
                self.__ghost_sprites.ghosts[ghost.kind]
            )

            return ghost_image.chase[Direction.UP]

        if ghost.mode == GhostMode.EATEN:
            return self.__ghost_sprites.eaten[ghost.direction]

        if ghost.direction == Direction.NONE:
            return None

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

    def __is_respawning_visible(
        self: "GhostsRenderer",
        ghost: GhostModel,
    ) -> bool:
        if ghost.mode != GhostMode.RESPAWNING:
            return True

        blink_index = int(
            ghost.respawn_time_remaining / RESPAWN_BLINK_INTERVAL
        )

        return blink_index % 2 == 0
