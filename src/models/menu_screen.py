from enum import Enum, auto


class MenuScreenType(Enum):
    """Available Menu screens."""

    MAIN_MENU = auto()
    SETTINGS = auto()
    LEADERBOARD = auto()