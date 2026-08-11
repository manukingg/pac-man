from .screen import Screen
from ..models import AppState
from ..ui import MenuButton, DropdownButton, DropdownButtonState
from ..graphics import (
    PygameWrapper,
    get_aligned_position,
    get_text_width,
    Image,
    GraphicsEvent, EventType,
    Rect,
    Color,
    Key,
)


class InstructionsScreen(Screen):
    """Instructions for the game."""

    def __init__(self):
        super().__init__()

    def handle_event(
        self: "InstructionsScreen",
        event: EventType,
        state: AppState,
    ) -> str | None:
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
        state: AppState
    ) -> None:
        return None
