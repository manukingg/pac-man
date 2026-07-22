from .screen import Screen
from ..models.menu_screen import MenuScreenType

from ..graphics import PygameWrapper
from ..graphics.image import Image
from ..models import AppState


class MainMenuScreen(Screen):
    """Main application menu."""
    def __init__(self):
        self.menu_screen = MenuScreenType.MAIN_MENU

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
        image: Image,
        display: PygameWrapper,
        state: AppState,
    ) -> None:
        display.clear(image, (0, 0, 0))
        display.write_text(
            text="good,",
            image=image,
            font_size=14,
            align=("center", 0.1),
            color=(255, 255, 0),
        )
