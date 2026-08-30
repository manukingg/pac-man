import pygame

from pathlib import Path

from .animation import AnimatedSprite
from .graphics import PygameWrapper
from .models import AppState, ScreenType
from .screens import (
    Screen,
    MainMenuScreen,
    GameScreen,
    get_available_resolution_options,
    get_available_resolution,
    get_nearest_available_resolution,
    resolution_to_text,
    parse_resolution_text,
)
from .models import (
    Config,
    Level,
)
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

        desktop_width, desktop_height = self._display.get_desktop_size()

        current_resolution = f"{config.window_width}x{config.window_height}"

        resolution_options = get_available_resolution_options(
            desktop_width=desktop_width,
            desktop_height=desktop_height,
        )

        if current_resolution not in resolution_options:
            resolution_options.insert(0, current_resolution)

        self._screens: dict[ScreenType, Screen] = {
            ScreenType.MAIN_MENU: MainMenuScreen(
                resolution_options=resolution_options,
                current_resolution=current_resolution,
            ),
            ScreenType.GAME: GameScreen(pacman_sprite=pacman_sprite)
        }

        self.width = config.window_width
        self.height = config.window_height

        self._game_state_factory = GameStateFactory(config)
        level = Level(level_number=1, width=20, height=20)
        self._state.game_state = self._game_state_factory.create(level=level)

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

        if action.startswith("set_resolution:"):
            _, value = action.split(":", 1)

            size = self._parse_resolution(value)
            if size is None:
                print(f"Invalid resolution: {value}")
                return

            new_width, new_height = size

            if new_width == self.width and new_height == self.height:
                return

            self.width = new_width
            self.height = new_height

            self._state.config.window_width = new_width
            self._state.config.window_height = new_height

            self._display.resize_window(
                width=self.width,
                height=self.height,
            )
            self._frame_needs_rebuild = True
            return

    def run(self: "Application") -> None:
        """Run the application loop."""
        try:
            frame = self._display.new_image(self.width, self.height)
            while self._state.running:
                delta_time = 0  # self._clock.tick(60) / 1000.0

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
