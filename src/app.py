import json

from pathlib import Path

from .animation import AnimatedSprite
from .graphics import GraphicsBackend
from .models import AppState, ScreenType
from .screens import (
    Screen,
    MainMenuScreen,
    GameScreen,
    get_available_resolution_options,
    get_available_resolutions,
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
        self._preferences_path = Path("user_preferences.json")

        desktop_width, desktop_height = GraphicsBackend.get_desktop_size()

        available_resolutions = get_available_resolutions(
            desktop_width=desktop_width,
            desktop_height=desktop_height,
        )

        preferred_resolution = self._load_preferred_resolution()

        if preferred_resolution is None:
            preferred_resolution = (
                config.window_width,
                config.window_height,
            )

        self.width, self.height = get_nearest_available_resolution(
            requested_width=preferred_resolution[0],
            requested_height=preferred_resolution[1],
            available_resolutions=available_resolutions,
        )

        config.window_width = self.width
        config.window_height = self.height

        self._state = AppState(
            current_screen=ScreenType.MAIN_MENU,
            config=config,
        )

        assets_path = Path("assets")

        self._display = GraphicsBackend(
            width=self.width,
            height=self.height,
            title="Pac-Man",
        )

        current_resolution = resolution_to_text(
            width=self.width,
            height=self.height,
        )

        resolution_options = get_available_resolution_options(
            desktop_width=desktop_width,
            desktop_height=desktop_height,
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
            initial_animation="left",
            playing=False
        )

        self._screens: dict[ScreenType, Screen] = {
            ScreenType.MAIN_MENU: MainMenuScreen(
                resolution_options=resolution_options,
                current_resolution=current_resolution,
            ),
            ScreenType.GAME: GameScreen(pacman_sprite=pacman_sprite)
        }

        self._game_state_factory = GameStateFactory(config)
        level = Level(level_number=1, width=20, height=20)
        self._state.game_state = self._game_state_factory.create(level=level)

        self._frame = self._display.new_image(self.width, self.height)

        self._frame_needs_rebuild = False

    def _load_preferred_resolution(
        self: "Application",
    ) -> tuple[int, int] | None:
        try:
            raw_text = self._preferences_path.read_text(encoding="utf-8")
            raw_data = json.loads(raw_text)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            return None
        except OSError:
            return None

        if not isinstance(raw_data, dict):
            return None

        width = raw_data.get("window_width")
        height = raw_data.get("window_height")

        if not isinstance(width, int) or not isinstance(height, int):
            return None

        if width <= 0 or height <= 0:
            return None

        return width, height

    def _save_user_preferences(self: "Application") -> None:
        data = {
            "window_width": self.width,
            "window_height": self.height,
        }

        try:
            self._preferences_path.write_text(
                json.dumps(data, indent=4) + "\n",
                encoding="utf-8",
            )
        except OSError as error:
            print(f"Could not save user preferences: {error}")

    def _rebuild_frame_if_needed(self: "Application") -> None:
        if not self._frame_needs_rebuild:
            return

        self._frame = self._display.new_image(self.width, self.height)
        self._frame_needs_rebuild = False

    def _handle_events(self: "Application") -> None:
        screen = self._screens[self._state.current_screen]

        for event in self._display.poll_events():
            if event.type == EventType.QUIT:
                self._state.running = False
                return
            action = screen.handle_event(event, self._state)
            self._handle_action(action)

            screen = self._screens[self._state.current_screen]

    def _update_current_screen(self: "Application", delta_time: float) -> None:
        screen = self._screens[self._state.current_screen]

        action = screen.update(delta_time, self._state)
        self._handle_action(action)

    def _render_current_screen(self: "Application") -> None:
        screen = self._screens[self._state.current_screen]

        self._display.clear(self._frame, (0, 0, 0))

        screen.render(
            display=self._display,
            image=self._frame,
            state=self._state,
        )

        self._display.put_image_to_window(self._frame, 0, 0)
        self._display.present()

    def _run_frame(self: "Application", delta_time: float) -> bool:
        self._handle_events()
        self._update_current_screen(delta_time)
        self._rebuild_frame_if_needed()
        self._render_current_screen()

        return self._state.running

    def _handle_action(self: "Application", action: str | None) -> None:
        if action is None:
            return

        if action == "start_game":
            self._state.current_screen = ScreenType.GAME

        if action == "quit":
            self._state.running = False
            return

        if action == "open_settings":
            self._state.current_screen = ScreenType.MENU_SETTINGS
            return

        if action.startswith("set_resolution:"):
            _, value = action.split(":", 1)

            size = parse_resolution_text(value)
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
            self._save_user_preferences()
            return

    def run(self: "Application") -> None:
        """Run the application loop."""
        try:
            self._display.start_loop(self._run_frame)

        except Exception as e:
            print(e)

        finally:
            self._display.quit()
