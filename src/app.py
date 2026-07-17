import pygame

from .models import Config
from .graphics import Display
from .screens import Screen, MainMenuScreen
from .models import AppState, ScreenType
from .factories import GameStateFactory


class Application:
    """Main Pac-Man application."""

    def __init__(self: "Application", config: Config) -> None:
        self._state = AppState(
            current_screen=ScreenType.MAIN_MENU,
            config=config,
        )

        self._display = Display(
            width=config.window_width,
            height=config.window_height,
            title="Pac-Man",
        )

        self._screens: dict[ScreenType, Screen] = {
            ScreenType.MAIN_MENU: MainMenuScreen(),
        }

        self._game_state_factory = GameStateFactory(config)

        self._clock = pygame.time.Clock()

    def run(self: "Application") -> None:
        """Run the application loop."""

        try:
            while self._state.running:
                delta_time = self._clock.tick(60) / 1000.0

                screen = self._screens[self._state.current_screen]

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._state.running = False
                        continue

                    screen.handle_event(event, self._state)

                screen.update(delta_time, self._state)

                self._display.clear(0x000000)
                screen.render(self._display, self._state)
                self._display.present()
        finally:
            self._display.close()
