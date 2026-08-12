from .screen import Screen
from ..models import AppState
from ..graphics import (
    PygameWrapper,
    Image,
    GraphicsEvent,
    EventType,
    Key,
)


class InstructionsScreen(Screen):
    """Instructions for the game."""

    _BACKGROUND_COLOR = (0, 0, 0)
    _TITLE_COLOR = (255, 255, 0)
    _TEXT_COLOR = (255, 255, 255)

    _TITLE_FONT_SIZE = 16
    _TEXT_FONT_SIZE = 6

    _TITLE_POSITION = (50, 50)
    _TEXT_POSITION = (50, 100)
    _LINE_GAP = 20

    def handle_event(
        self: "InstructionsScreen",
        event: GraphicsEvent,
        state: AppState,
    ) -> str | None:
        if event.type == EventType.KEY_DOWN:
            if event.key == Key.ESCAPE:
                return "main_menu"

        return None

    def update(
        self: "InstructionsScreen",
        delta_time: float,
        state: AppState,
    ) -> str | None:
        return None

    def render(
        self: "InstructionsScreen",
        display: PygameWrapper,
        image: Image,
        state: AppState,
    ) -> None:
        display.clear(
            image=image,
            color=self._BACKGROUND_COLOR,
        )

        display.write_text(
            text="PAC-MAN INSTRUCTIONS",
            image=image,
            font_size=self._TITLE_FONT_SIZE,
            color=self._TITLE_COLOR,
            position=self._TITLE_POSITION,
        )

        instructions = [
            "ARROW KEYS / WASD - MOVE",
            "EAT ALL THE DOTS",
            "AVOID THE GHOSTS",
            "GET AS MANY POINTS AS POSSIBLE",
            "",
            "PRESS ESC TO RETURN TO MENU",
        ]

        x, y = self._TEXT_POSITION

        for line in instructions:
            display.write_text(
                text=line,
                image=image,
                font_size=self._TEXT_FONT_SIZE,
                color=self._TEXT_COLOR,
                position=(x, y),
            )

            y += self._LINE_GAP
