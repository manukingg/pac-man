from .screen import Screen
from ..models import AppState
from .resolutions import settings_resolutions, resolutions
from ..ui import MenuButton
from ..graphics import Rect
from ..graphics import (
    PygameWrapper,
    Image,
    GraphicsEvent,
    EventType,
    Key,
)


class InstructionsScreen(Screen):
    """Instructions for the game."""

    def __init__(self: "InstructionsScreen") -> None:
        self._back_button = MenuButton(
            label="Back to Menu",
            action="main_menu",
            rect=Rect(0, 0, 0, 0),
        )

    def handle_event(
        self: "InstructionsScreen",
        event: GraphicsEvent,
        state: AppState,
    ) -> str | None:
        if event.type == EventType.MOUSE_MOTION:
            if event.pos is not None:
                if self._back_button.rect.contains(event.pos):
                    self._back_button.label = ">Back to Menu<"
                else:
                    self._back_button.label = "Back to Menu"
                    return None
        if event.type == EventType.MOUSE_DOWN:
            if event.button == 1 and event.pos is not None:
                if self._back_button.rect.contains(event.pos):
                    return "open_menue"
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
        # resolution_key = settings_resolutions.get((image.width, image.height))
        # layout = resolutions.get(resolution_key)

        # name_font = layout["name_font"]
        # buttons_font = layout["buttons_font"]
        # name_top_gap = layout["name_top_gap"]
        # next_button_start = layout["next_button_start"]
        # gap_between_buttons = layout["gap_between_buttons"]
        # dropdown_font_size = layout["dropdown_font_size"]
        # dropdown_options_font_size = layout["dropdown_options_font_size"]
        background_color = (0, 0, 0)
        title_color = (255, 255, 0)
        text_color = (255, 255, 255)

        title_font = 15
        text_font = 6

        title_position = (50, 50)
        text_position = (50, 200)
        line_gap = 55

        display.clear(
            image=image,
            color=background_color,
        )

        display.write_text(
            text="PAC-MAN INSTRUCTIONS",
            image=image,
            font_size=title_font,
            color=title_color,
            position=title_position,
        )

        instructions = [
            "USE ARROW KEYS / WASD TO MOVE",
            "EAT DOTS TO SCORE POINTS",
            "EAT ALL DOTS TO COMPLETE THE LEVEL",
            "AVOID THE GHOSTS",
            "TOUCHING A GHOST COSTS ONE LIFE",
            "YOU START WITH A LIMITED NUMBER OF LIVES",
            "POWER PELLETS MAKE GHOSTS VULNERABLE",
            "EAT VULNERABLE GHOSTS FOR BONUS POINTS",
            "BONUS ITEMS CAN APPEAR IN THE MAZE",
            "COLLECT BONUS ITEMS FOR EXTRA POINTS",
            "CLEAR THE MAZE TO ADVANCE",
            "LOSE ALL LIVES AND THE GAME IS OVER",
            "CLEAR ALL 10 LEVELS TO WIN",
        ]

        x, y = text_position

        for line in instructions:
            display.write_text(
                text=line,
                image=image,
                font_size=text_font,
                color=text_color,
                position=(x, y),
            )

            y += line_gap

        button_font = 6
        button_x = int((image.width - len(self._back_button.label)
                       * 6 * button_font) / 2)
        button_y = y + line_gap

        self._back_button.rect = Rect(
            x=button_x,
            y=button_y,
            width=len(self._back_button.label) * 6 * button_font,
            height=8 * button_font,
        )

        display.write_text(
            text=self._back_button.label,
            image=image,
            font_size=button_font,
            color=text_color,
            position=(
                self._back_button.rect.x,
                self._back_button.rect.y,
            ),
        )
