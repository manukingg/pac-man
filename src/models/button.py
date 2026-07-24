from dataclasses import dataclass

from src.graphics.rect import Rect


@dataclass
class MenuButton:
    label: str
    action: str
    rect: Rect
