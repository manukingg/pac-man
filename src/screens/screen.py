from abc import ABC, abstractmethod

from ..graphics import PygameWrapper
from ..graphics.image import Image
from ..models import AppState
from ..graphics.events import EventType


class Screen(ABC):
    """Base class for application screens."""

    @abstractmethod
    def handle_event(
        self: "Screen",
        event: EventType,
        state: AppState,
    ) -> None:
        """Handle an input event."""

    @abstractmethod
    def update(
        self: "Screen",
        delta_time: float,
        state: AppState,
    ) -> None:
        """Update screen logic."""

    @abstractmethod
    def render(
        self: "Screen",
        display: PygameWrapper,
        image: Image,
        state: AppState
    ) -> None:
        """Render the screen."""
