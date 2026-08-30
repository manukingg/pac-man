from dataclasses import dataclass, field
from enum import Enum

from src.graphics.rect import Rect


class DropdownButtonState(Enum):
    CLOSED = "closed"
    OPENED = "opened"


@dataclass
class DropdownButton:
    label: str
    action: str
    options: tuple[str]
    current_index: int
    rect: Rect

    state: DropdownButtonState = DropdownButtonState.CLOSED
    option_rects: list[Rect] = field(default_factory=list)
    hovered_option_index: int | None = None

    @property
    def selected_option(self: "DropdownButton") -> str:
        return self.options[self.current_index]

    def open(self: "DropdownButton") -> None:
        self.state = DropdownButtonState.OPENED

    def close(self: "DropdownButton") -> None:
        self.state = DropdownButtonState.CLOSED
        self.hovered_option_index = None

    def toggle(self: "DropdownButton") -> None:
        if self.state == DropdownButtonState.CLOSED:
            self.open()
        else:
            self.close()
