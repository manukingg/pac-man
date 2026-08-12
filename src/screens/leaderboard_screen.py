from .screen import Screen
from ..models import AppState
from .resolutions import settings_resolutions, resolutions
from ..graphics import (
    PygameWrapper,
    Image,
    GraphicsEvent,
    EventType,
    Key,
)


class LeaderboardScreen(Screen):
    """Leaderboard for the game."""

    def handle_event(
        self: "LeaderboardScreen",
        event: GraphicsEvent,
        state: AppState,
    ) -> str | None:
        if event.type == EventType.KEY_DOWN:
            if event.key == Key.ESCAPE:
                return "main_menu"

        return None

    def update(
        self: "LeaderboardScreen",
        delta_time: float,
        state: AppState,
    ) -> str | None:
        return None

    def render(
        self: "LeaderboardScreen",
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
