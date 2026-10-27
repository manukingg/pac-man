from ...graphics import GraphicsBackend, Image
from ...models import GameState, ScorePopup, GamePhase
from .game_layout import GameLayout


SCORE_POPUP_COLOR = (255, 255, 255)
SCORE_POPUP_RISE_FACTOR = 0.35


class GameOverlayRenderer:
    def __init__(self: "GameOverlayRenderer") -> None:
        pass

    def render(
        self: "GameOverlayRenderer",
        display: GraphicsBackend,
        image: Image,
        game_state: GameState,
        layout: GameLayout,
    ) -> None:
        if (
            game_state.phase != GamePhase.GHOST_EATEN
            or game_state.score_popup is None
            or layout.score_popup_size is None
            or layout.cell_size is None
        ):
            return

        self.__render_score_popup(
            display=display,
            image=image,
            popup=game_state.score_popup,
            size=layout.score_popup_size,
            progress=game_state.phase_progress,
            rise_distance=(
                layout.cell_size * SCORE_POPUP_RISE_FACTOR
            ),
        )

    def __render_score_popup(
        self: "GameOverlayRenderer",
        display: GraphicsBackend,
        image: Image,
        popup: ScorePopup,
        size: int,
        progress: float,
        rise_distance: float,
    ) -> None:
        text = str(popup.score)

        text_width = (
            len(text) * 5 * size
            + len(text) - 1 * size
        )

        text_height = 8 * size

        eased_progress = 1.0 - (1.0 - progress) ** 2

        rise_offset = rise_distance * eased_progress

        x = round(popup.position.x - text_width / 2)

        y = round(popup.position.y - text_height / 2 - rise_offset)

        display.write_text(
            text=str(popup.score),
            image=image,
            font_size=size,
            color=SCORE_POPUP_COLOR,
            position=(x, y),
        )
