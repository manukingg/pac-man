from enum import Enum, auto


class ScreenType(Enum):
    """Available application screens."""

    MAIN_MENU = auto()
    GAME = auto()
    PAUSE = auto()
    HIGHSCORES = auto()
    INSTRUCTIONS = auto()
    GAME_OVER = auto()
    VICTORY = auto()
