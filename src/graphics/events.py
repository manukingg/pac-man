from dataclasses import dataclass
from enum import Enum


class EventType(Enum):
    QUIT = "quit"
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    MOUSE_DOWN = "mouse_down"
    MOUSE_UP = "mouse_up"
    MOUSE_MOTION = "mouse_motion"


class Key(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    W = "w"
    A = "a"
    S = "s"
    D = "d"
    ENTER = "enter"
    SPACE = "space"
    ESCAPE = "escape"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class GraphicsEvent:
    type: EventType
    key: Key | None = None
    button: int | None = None
    pos: tuple[int, int] | None = None
