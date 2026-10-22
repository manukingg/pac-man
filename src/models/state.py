from dataclasses import dataclass

from .config_model import Config
from .ghost import GhostModel
from .player import PlayerModel
from .screen import ScreenType
from .maze import MazeGrid
from .common import GridPosition


@dataclass
class GameState:
    """Mutable state of the current game session."""
    maze: MazeGrid
    ghosts: list[GhostModel]
    player: PlayerModel
    score: int
    lives: int
    level: int
    remaining_time: float
    pellets: set[GridPosition] | None = None
    power_pellets: set[GridPosition] | None = None
    paused: bool = False
    power_mode_remaining: float = 0.0

    @property
    def ghosts_are_edible(self) -> bool:
        """Return whether ghosts are currently edible."""
        return self.power_mode_remaining > 0.0

    def add_score(self: "GameState", score: int) -> None:
        self.score += score

    def remove_pellet(self: "GameState", position: GridPosition) -> None:
        self.pellets.discard(position)

    def remove_power_pellet(self: "GameState", position: GridPosition) -> None:
        self.power_pellets.discard(position)

    def pause(self: "GameState") -> None:
        self.paused = True

    def unpause(self: "GameState") -> None:
        self.paused = False

    def lose_life(self: "GameState") -> None:
        self.lives = max(0, self.lives - 1)

    def activate_power_mode(
        self: "GameState",
        duration: float,
    ) -> None:
        self.power_mode_remaining = duration

    def update_power_mode(
        self: "GameState",
        delta_time: float,
    ) -> None:
        self.power_mode_remaining = max(
            0.0,
            self.power_mode_remaining - delta_time
        )

    def update_remaining_time(
        self: "GameState",
        delta_time: float,
    ) -> None:
        self.remaining_time = max(
            0.0,
            self.remaining_time - delta_time,
        )


@dataclass
class AppState:
    """Global application state."""
    current_screen: ScreenType
    config: Config
    game_state: GameState | None = None
    running: bool = True
