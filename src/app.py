import pygame

from pathlib import Path

from .animation import AnimatedSprite
from .models import Config
from .graphics import PygameWrapper
from .screens import Screen
from .screens.main_menu_screen import MainMenuScreen
from .screens.settings_screen import SettingsMenuScreen
from .models import AppState, ScreenType
from .screens import Screen, MainMenuScreen, GameScreen
from .models import AppState, ScreenType, Level
from .factories import GameStateFactory

from .graphics.events import EventType


class Application:
    """Main Pac-Man application."""

    def __init__(self: "Application", config: Config) -> None:
        self._state = AppState(
            current_screen=ScreenType.GAME,
            config=config,
        )

        assets_path = Path("assets")

        self._display = PygameWrapper(
            width=config.window_width,
            height=config.window_height,
            title="Pac-Man",
        )

        pacman_animations = {
            "right": self._display.load_animation(
                paths=[
                    assets_path / "pacman-right/1.png",
                    assets_path / "pacman-right/2.png",
                    assets_path / "pacman-right/3.png",
                    assets_path / "pacman-right/2.png",
                    assets_path / "pacman-right/1.png",

                ],
                frame_duration=0.08
            ),
            "left": self._display.load_animation(
                paths=[
                    assets_path / "pacman-left/3.png",
                    assets_path / "pacman-left/2.png",
                    assets_path / "pacman-left/1.png",
                    assets_path / "pacman-left/2.png",
                    assets_path / "pacman-left/3.png"
                ],
                frame_duration=0.08
            ),
            "up": self._display.load_animation(
                paths=[
                    assets_path / "pacman-up/1.png",
                    assets_path / "pacman-up/2.png",
                    assets_path / "pacman-up/3.png",
                    assets_path / "pacman-up/2.png",
                    assets_path / "pacman-up/1.png",
                ],
                frame_duration=0.08
            ),
            "down": self._display.load_animation(
                paths=[
                    assets_path / "pacman-down/1.png",
                    assets_path / "pacman-down/2.png",
                    assets_path / "pacman-down/3.png",
                    assets_path / "pacman-down/2.png",
                    assets_path / "pacman-down/1.png"
                ],
                frame_duration=0.08
            )
        }

        pacman_sprite = AnimatedSprite(
            animations=pacman_animations,
            initial_animation="left"
        )

        self._screens: dict[ScreenType, Screen] = {
            ScreenType.MAIN_MENU: MainMenuScreen(),
            ScreenType.MENU_SETTINGS: SettingsMenuScreen(),
            ScreenType.GAME: GameScreen(pacman_sprite=pacman_sprite)
        }
        self.width = config.window_width
        self.height = config.window_height

        self._game_state_factory = GameStateFactory(config)
        level = Level(level_number=1, width=20, height=20)
        self._state.game_state = self._game_state_factory.create(level=level)

        self._clock = pygame.time.Clock()

    def _handle_action(self: "Application", action: str | None) -> None:
        if action is None:
            return

        if action == "quit":
            self._state.running = False

        if action == "open_settings":
            self._state.current_screen = ScreenType.MENU_SETTINGS

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
