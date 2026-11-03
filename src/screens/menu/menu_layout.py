from dataclasses import dataclass

from ...constants import (
    MENU_BASE_WIDTH,
    MENU_BASE_HEIGHT,
    MENU_TITLE_BASE_FONT_SIZE,
    MENU_BUTTON_BASE_FONT_SIZE,
    MENU_DROPDOWN_BASE_FONT_SIZE,
    MENU_DROPDOWN_OPTION_BASE_FONT_SIZE,
    MENU_TITLE_BASE_TOP,
    MENU_BUTTONS_BASE_START_Y,
    MENU_BUTTON_BASE_GAP,
)


@dataclass(frozen=True)
class MenuLayout:
    title_font_size: int
    button_font_size: int

    title_top: int
    buttons_start_y: int
    button_gap: int

    dropdown_font_size: int
    dropdown_option_font_size: int

    @classmethod
    def calculate(
        cls: "MenuLayout",
        width: int,
        height: int
    ) -> "MenuLayout":
        scale = min(
            width / MENU_BASE_WIDTH,
            height / MENU_BASE_HEIGHT,
        )

        return cls(
            title_font_size=max(
                1,
                round(MENU_TITLE_BASE_FONT_SIZE * scale),
            ),
            button_font_size=max(
                1,
                round(MENU_BUTTON_BASE_FONT_SIZE * scale),
            ),
            title_top=round(
                MENU_TITLE_BASE_TOP * scale
            ),
            buttons_start_y=round(
                MENU_BUTTONS_BASE_START_Y * scale
            ),
            button_gap=round(
                MENU_BUTTON_BASE_GAP * scale
            ),
            dropdown_font_size=max(
                1,
                round(MENU_DROPDOWN_BASE_FONT_SIZE * scale),
            ),
            dropdown_option_font_size=max(
                1,
                round(MENU_DROPDOWN_OPTION_BASE_FONT_SIZE * scale),
            ),
        )
