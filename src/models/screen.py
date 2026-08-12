from enum import Enum, auto


class ScreenType(Enum):
    """Available application screens."""

    MAIN_MENU = auto()
    MENU_SETTINGS = auto()
    GAME = auto()
    PAUSE = auto()
    LEADERBOARD = auto()
    INSTRUCTIONS = auto()
    GAME_OVER = auto()
    VICTORY = auto()
