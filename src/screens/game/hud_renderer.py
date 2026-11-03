from ...models import GameState
from ...graphics import GraphicsBackend, Image
from .game_layout import GameLayout
from ...constants import (
    HUD_COLOR,
)


class HudRenderer:
    def __init__(self: "HudRenderer") -> None:
        self.__prepared_size: int | None = None

    def invalidate(self: "HudRenderer") -> None:
        self.__prepared_size = None

    def render(
        self: "HudRenderer",
        display: GraphicsBackend,
        image: Image,
        game_state: GameState,
        layout: GameLayout,
    ) -> None:
        font_size = layout.hud_font_size
        margin = layout.hud_margin
        # life_icon_size = layout.life_icon_size

        self.__show_time(
            display=display,
            image=image,
            game_state=game_state,
            font_size=font_size,
            hud_margin=margin,
        )

        self.__show_score(
            display=display,
            image=image,
            game_state=game_state,
            font_size=font_size,
            hud_margin=margin,
        )

    def prepare(
        self: "HudRenderer",
        display: GraphicsBackend,
        layout: GameLayout,
    ) -> None:
        font_size = layout.hud_font_size

        if self.__prepared_size == font_size:
            return

        display.prepare_scaled_font(font_size, color=HUD_COLOR)

        self.__prepared_size = font_size

    def __show_time(
        self: "HudRenderer",
        display: GraphicsBackend,
        image: Image,
        game_state: GameState,
        font_size: int,
        hud_margin: int,
    ) -> None:
        time = f"{game_state.remaining_time:.2f}".replace(".", ":")
        display.write_text(
            text=f"REMAINING: {time}",
            image=image,
            font_size=font_size,
            color=HUD_COLOR,
            align=("left", hud_margin),
        )

    def __show_score(
        self: "HudRenderer",
        display: GraphicsBackend,
        image: Image,
        game_state: GameState,
        font_size: int,
        hud_margin: int,
    ) -> None:
        display.write_text(
            text=f"SCORE: {game_state.score}",
            image=image,
            font_size=font_size,
            color=HUD_COLOR,
            align=("center", hud_margin)
        )
