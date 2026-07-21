import pygame

from .models import Config
from .graphics import PygameWrapper
from .screens import Screen, MainMenuScreen
from .models import AppState, ScreenType
from .factories import GameStateFactory

from .graphics.events import EventType, GraphicsEvent


class Application:
    """Main Pac-Man application."""

    def __init__(self: "Application", config: Config) -> None:
        self._state = AppState(
            current_screen=ScreenType.MAIN_MENU,
            config=config,
        )

        self._display = PygameWrapper(
            width=config.window_width,
            height=config.window_height,
            title="Pac-Man",
        )

        self._screens: dict[ScreenType, Screen] = {
            ScreenType.MAIN_MENU: MainMenuScreen(),
        }
        self.width = config.window_width
        self.height = config.window_height

        self._game_state_factory = GameStateFactory(config)

        self._clock = pygame.time.Clock()

    def _handle_action(self: "Application") -> None:
        pass

    def run(self: "Application") -> None:
        """Run the application loop."""
        try:
            frame = self._display.new_image(self.width, self.height)

            while self._state.running:
                delta_time = self._clock.tick(60) / 1000.0

                screen = self._screens[self._state.current_screen]

                for event in self._display.poll_events():
                    if event.type == EventType.QUIT:
                        self._state.running = False
                        continue
                    action = screen.handle_event(event, self._state)
                    self._handle_action()
                action = screen.update(delta_time, self._state)
                self._handle_action()
                self._display.clear(frame, (0, 0, 0))
                screen = self._screens[self._state.current_screen]
                screen.render(display=self._display, image=frame, state=self._state)
                self._display.put_image_to_window(frame, 0, 0)
                self._display.present()

        finally:
            self._display.quit()
