from abc import ABC, abstractmethod

from ..graphics import Display
from ..models import AppState


class Screen(ABC):
    """Base class for application screens."""

    @abstractmethod
    def handle_event(
        self,
        event: object,
        state: AppState,
    ) -> None:
        """Handle an input event."""

    @abstractmethod
    def update(
        self,
        delta_time: float,
        state: AppState,
    ) -> None:
        """Update screen logic."""

    @abstractmethod
    def render(
        self,
        display: Display,
        state: AppState,
    ) -> None:
        """Render the screen."""