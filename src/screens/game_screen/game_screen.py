from .pellet_renderer import PelletRenderer
from .maze_renderer import MazeRenderer
from .player_controller import PlayerController
from .game_layout import GameLayout
from .player_renderer import PlayerRenderer
from .maze_navigator import MazeNavigator
from .ghosts_renderer import GhostsRenderer
from .ghosts_controller import GhostsController
from .game_rules_controller import GameRulesController
from .game_overlay_renderer import GameOverlayRenderer

from ...animation import AnimatedSprite
from ...graphics import (
    Image,
    GraphicsEvent,
    EventType,
    Key,
    GraphicsBackend
)
from ...models import (
    AppState,
    Direction,
    MazeGrid,
    GhostAssets,
    GameRules,
)

from ..screen import Screen


Color = tuple[int, int, int]

PELLET_COLOR: Color = (255, 220, 180)


class GameScreen(Screen):
    """Render and control the current game session."""

    _BACKGROUND_COLOR: Color = (0, 0, 0)
    _WALL_COLOR: Color = (32, 88, 255)
    _FT_COLOR: Color = (0, 4, 53)
    _ERROR_COLOR: Color = (255, 64, 64)

    def __init__(
        self: "GameScreen",
        pacman_sprite: AnimatedSprite,
        ghosts_sprites: GhostAssets,
        rules: GameRules,
    ) -> None:
        self.__maze_navigator = MazeNavigator()
        self.__ghosts_controller = GhostsController(
            maze_navigator=self.__maze_navigator,
        )
        self.__player_controller = PlayerController(
            pacman_sprite=pacman_sprite,
            maze_navigator=self.__maze_navigator,
        )
        self.__ghosts_renderer = GhostsRenderer(
            ghosts_sprites=ghosts_sprites,
        )
        self.__player_renderer = PlayerRenderer(
            pacman_sprite=pacman_sprite
        )

        self.__pellet_renderer = PelletRenderer()

        self.__maze_renderer = MazeRenderer(
            self._BACKGROUND_COLOR,
            self._WALL_COLOR,
            self._FT_COLOR,
        )

        self.__game_rules_controller = GameRulesController(rules=rules)

        self.__layout = GameLayout()

        self.__game_overlay_renderer = GameOverlayRenderer()

    def handle_event(
        self: "GameScreen",
        event: GraphicsEvent,
        state: AppState,
        change_resolution: bool | None = None
    ) -> str | None:
        """Handle gameplay input."""

        if change_resolution:
            self.__layout.reset()
            self.__maze_renderer.invalidate()
            self.__pellet_renderer.invalidate()
            self.__player_renderer.invalidate()
            self.__ghosts_renderer.invalidate()
            if state.game_state is not None:
                state.game_state.player.reset_position()
            return

        if event.type != EventType.KEY_DOWN:
            return

        if event.key == Key.ESCAPE:
            return "quit"

        game_state = state.game_state

        if game_state is None:
            return

        direction_by_key = {
            Key.UP: Direction.UP,
            Key.W: Direction.UP,
            Key.DOWN: Direction.DOWN,
            Key.S: Direction.DOWN,
            Key.LEFT: Direction.LEFT,
            Key.A: Direction.LEFT,
            Key.RIGHT: Direction.RIGHT,
            Key.D: Direction.RIGHT,
        }

        direction = direction_by_key.get(event.key)

        if direction is None:
            return

        game_state.player.request_move(direction)

    def update(
        self: "GameScreen",
        delta_time: float,
        state: AppState,
    ) -> None:
        """Update the current game session."""

        game_state = state.game_state

        if game_state is None:
            return

        if self.__layout.player_speed is None:
            return

        if game_state.power_pellets is None or game_state.pellets is None:
            return

        if self.__game_rules_controller.update_phase(
            game_state=game_state,
            delta_time=delta_time,
        ):
            return

        reached_cells = self.__player_controller.update(
            player=game_state.player,
            maze=game_state.maze,
            delta_time=delta_time,
            layout=self.__layout,
            player_speed=self.__layout.player_speed,
        )

        self.__ghosts_controller.update(
            ghosts=game_state.ghosts,
            player=game_state.player,
            maze=game_state.maze,
            delta_time=delta_time,
            ghosts_speed=self.__layout.ghosts_speed,
            normal_speed_multiplier=game_state.level.ghost_speed_multiplier,
            normal_mode=game_state.ghost_behavior_mode,
            layout=self.__layout,
        )

        self.__game_rules_controller.update(
            game_state=game_state,
            reached_cells=reached_cells,
            delta_time=delta_time,
            collision_distance=self.__layout.collision_distance,
        )

        self.__pellet_renderer.update(delta_time=delta_time)

        self.__ghosts_renderer.update(
            ghosts=game_state.ghosts,
            delta_time=delta_time,
            game_state=game_state,
        )

    def render(
        self: "GameScreen",
        display: GraphicsBackend,
        image: Image,
        state: AppState,
    ) -> None:
        """Render the current game session."""

        display.clear(
            image=image,
            color=self._BACKGROUND_COLOR,
        )

        game_state = state.game_state

        if game_state is None:
            self.__render_error(
                display=display,
                image=image,
                text="GAME STATE IS NOT INITIALIZED",
            )
            return

        maze = game_state.maze

        if not maze or not maze[0]:
            self.__render_error(
                display=display,
                image=image,
                text="MAZE IS EMPTY",
            )
            return

        if not self.__initialize_layout(
            image=image,
            maze=maze,
        ):
            self.__render_error(
                display=display,
                image=image,
                text="MAZE DOES NOT FIT THE WINDOW"
            )
            return

        self.__maze_renderer.render(
            display=display,
            image=image,
            maze=maze,
            layout=self.__layout,
        )

        self.__player_controller.initialize_player_position(
            player=game_state.player,
            layout=self.__layout,
        )

        self.__ghosts_controller.initialize_ghosts_position(
            ghosts=game_state.ghosts,
            maze=maze,
            layout=self.__layout,
        )

        if self.__layout.pellet_size is not None:
            self.__pellet_renderer.render(
                display=display,
                image=image,
                pellets=game_state.pellets,
                power_pellets=game_state.power_pellets,
                layout=self.__layout,
            )

        if self.__layout.player_size is not None:
            self.__player_renderer.render(
                display=display,
                image=image,
                player=game_state.player,
                player_size=self.__layout.player_size,
            )

        if self.__layout.ghost_size is not None:
            self.__ghosts_renderer.render(
                display=display,
                image=image,
                ghosts=game_state.ghosts,
                ghosts_size=self.__layout.ghost_size,
                game_state=game_state,
            )

        self.__game_overlay_renderer.render(
            display=display,
            image=image,
            game_state=game_state,
            layout=self.__layout,
        )

    def __initialize_layout(
        self: "GameScreen",
        image: Image,
        maze: MazeGrid,
    ) -> bool:
        old_cell_size = self.__layout.cell_size
        old_offset_x = self.__layout.offset_x
        old_offset_y = self.__layout.offset_y

        old_player_size = self.__layout.player_size
        old_pellet_size = self.__layout.pellet_size
        old_ghost_size = self.__layout.ghost_size

        if not self.__layout.update(
            image=image,
            maze=maze,
        ):
            return False

        if (
            self.__layout.cell_size != old_cell_size
            or self.__layout.offset_x != old_offset_x
            or self.__layout.offset_y != old_offset_y
        ):
            self.__maze_renderer.invalidate()

        if self.__layout.player_size != old_player_size:
            self.__player_renderer.invalidate()

        if self.__layout.pellet_size != old_pellet_size:
            self.__pellet_renderer.invalidate()

        if self.__layout.ghost_size != old_ghost_size:
            self.__ghosts_renderer.invalidate()

        return True

    def __render_error(
        self: "GameScreen",
        display: GraphicsBackend,
        image: Image,
        text: str,
    ) -> None:
        """Render a non-fatal game screen error."""

        self.__layout.update_screen_metrics(image)

        if (
            self.__layout.error_font_size is None
            or self.__layout.padding is None
        ):
            raise RuntimeError("Screen metrics are not initialized")

        display.write_text(
            text=text,
            image=image,
            font_size=self.__layout.error_font_size,
            color=self._ERROR_COLOR,
            position=(
                self.__layout.padding,
                self.__layout.padding,
            ),
        )
