from ..graphics import Display
from ..models import AppState

from .screen import Screen


class MainMenuScreen(Screen):
    """Main application menu."""

    def handle_event(
        self: "MainMenuScreen",
        event: object,
        state: AppState,
    ) -> None:
        pass

    def update(
        self: "MainMenuScreen",
        delta_time: float,
        state: AppState,
    ) -> None:
        pass

    def render(
        self: "MainMenuScreen",
        display: Display,
        state: AppState,
    ) -> None:
        display.clear(0x000000)
        display.draw_text(
            x=300,
            y=150,
            text="PAC-MAN",
            color=0xFFFF00,
        )
        display.draw_text(
            x=300,
            y=250,
            text="Start Game",
            color=0xFFFFFF,
        )