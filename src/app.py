import pygame

from .models import Config
from .graphics import PygameWrapper
from .screens import Screen
from .screens.main_menu_screen import MainMenuScreen
from .models import AppState, ScreenType
from .screens import Screen, MainMenuScreen, GameScreen
from .models import AppState, ScreenType, Level
from .factories import GameStateFactory

from .graphics.events import EventType


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
            ScreenType.GAME: GameScreen()
        }
        self.width = config.window_width
        self.height = config.window_height

        self._game_state_factory = GameStateFactory(config)

        self._clock = pygame.time.Clock()

        self._frame_needs_rebuild = False

    def _handle_action(self: "Application", action: str | None) -> None:
        if action is None:
            return

        if action == "quit":
            self._state.running = False
            return

        if action == "open_settings":
            self._state.current_screen = ScreenType.MENU_SETTINGS
            return

        if action.startswith("set_fullscreen:"):
            _, value = action.split(":", 1)

            enabled = value == "on"

            self.width, self.height = self._display.set_fullscreen(enabled)
            self._frame_needs_rebuild = True
            return

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
                    self._handle_action(action)

                screen = self._screens[self._state.current_screen]

                action = screen.update(delta_time, self._state)
                self._handle_action(action)

                if self._frame_needs_rebuild:
                    frame = self._display.new_image(self.width, self.height)
                    self._frame_needs_rebuild = False

                self._display.clear(frame, (0, 0, 0))

                screen.render(
                    display=self._display,
                    image=frame,
                    state=self._state
                )
                self._display.put_image_to_window(frame, 0, 0)
                self._display.present()

        except Exception as e:
            print(e)

        finally:
            self._display.quit()
