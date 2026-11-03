from .screen import Screen
from ..models import AppState
from ..ui import MenuButton, DropdownButton

from ..graphics import (
    GraphicsBackend,
    Image,
    GraphicsEvent,
    Rect,
)

from .menu import MenuController, MenuRenderer


class MainMenuScreen(Screen):
    """Main application menu."""
    def __init__(
        self: "MainMenuScreen",
        resolution_options: list[str],
        current_resolution: str,
    ) -> None:
        current_index = self.__get_resolution_index(
            options=resolution_options,
            current_resolution=current_resolution
        )
        self.__buttons: list[MenuButton] = [
            MenuButton(
                label="Play",
                action="start_game",
                rect=Rect(0, 0, 0, 0),
            ),
            MenuButton(
                label="Leaderboard",
                action="open_leaderboard",
                rect=Rect(0, 0, 0, 0),
            ),
            MenuButton(
                label="Instructions",
                action="open_instructions",
                rect=Rect(0, 0, 0, 0),
            ),
            MenuButton(
                label="Quit",
                action="quit",
                rect=Rect(0, 0, 0, 0),
            ),
        ]
        self.__dropdowns: list[DropdownButton] = [
            DropdownButton(
                label="Resolution",
                action="set_resolution",
                options=resolution_options,
                current_index=current_index,
                rect=Rect(0, 0, 0, 0),
            ),
        ]

        self.__controller = MenuController(
            buttons=self.__buttons,
            dropdowns=self.__dropdowns,
        )
        self.__renderer = MenuRenderer()

    def handle_event(
        self: "MainMenuScreen",
        event: GraphicsEvent,
        state: AppState,
    ) -> str | None:
        return self.__controller.handle_event(event=event)

    def update(
        self: "MainMenuScreen",
        delta_time: float,
        state: AppState,
    ) -> str | None:
        return self.__controller.update(delta_time=delta_time)

    def render(
        self: "MainMenuScreen",
        display: GraphicsBackend,
        image: Image,
        state: AppState,
    ) -> None:
        self.__renderer.render(
            display=display,
            image=image,
            buttons=self.__buttons,
            dropdowns=self.__dropdowns,
            focused_menu_index=(
                self.__controller.focused_menu_index
            ),
            focused_dropdown_index=(
                self.__controller.focused_dropdown_index
            ),
            focused_option_index=(
                self.__controller.focused_option_index
            ),
        )

    @staticmethod
    def __get_resolution_index(
        options: list[str],
        current_resolution: str,
    ) -> int:
        try:
            return options.index(current_resolution)
        except ValueError:
            return 0
