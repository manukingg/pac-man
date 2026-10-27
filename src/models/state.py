from dataclasses import dataclass
from enum import Enum, auto

from .config_model import Config, Level
from .ghost import GhostModel, ScorePopup, GhostKind, GhostMode
from .player import PlayerModel
from .screen import ScreenType
from .maze import MazeGrid
from .common import GridPosition, Position


class GamePhase(Enum):
    PLAYING = auto()
    GHOST_EATEN = auto()
    PLAYER_DEATH = auto()
    LEVEL_COMPLETE = auto()


@dataclass
class GameState:
    """Mutable state of the current game session."""
    maze: MazeGrid

    ghosts: list[GhostModel]
    player: PlayerModel

    score: int
    lives: int
    level: Level
    remaining_time: float

    pellets: set[GridPosition] | None
    power_pellets: set[GridPosition] | None

    power_mode_remaining: float = 0.0

    ghost_behavior_mode: GhostMode = GhostMode.CHASE
    ghost_behavior_index: int = 0
    ghost_behavior_time_remaining: float | None = 20.0

    phase: GamePhase = GamePhase.PLAYING
    phase_time_remaining: float = 0.0
    phase_duration: float = 0.0

    score_popup: ScorePopup | None = None

    ghosts_eaten_in_power_mode: int = 0

    @property
    def power_mode_active(self: "GameState") -> bool:
        """Return whether ghosts are currently edible."""
        return self.power_mode_remaining > 0.0

    @property
    def phase_progress(self: "GameState") -> float:
        if self.phase_duration <= 0:
            return 1.0
        return 1.0 - (
            self.phase_time_remaining
            / self.phase_duration
        )

    def add_score(self: "GameState", score: int) -> None:
        self.score += score

    def remove_pellet(self: "GameState", position: GridPosition) -> None:
        self.pellets.discard(position)

    def remove_power_pellet(self: "GameState", position: GridPosition) -> None:
        self.power_pellets.discard(position)

    def lose_life(self: "GameState") -> None:
        self.lives = max(0, self.lives - 1)

    def activate_power_mode(
        self: "GameState",
        duration: float,
    ) -> None:
        self.power_mode_remaining = duration
        self.ghosts_eaten_in_power_mode = 0

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

    def show_ghost_score(
        self: "GameState",
        ghost_kind: GhostKind,
        position: Position,
        score: int,
    ) -> None:
        self.score_popup = ScorePopup(
            ghost_kind=ghost_kind,
            position=position,
            score=score,
        )

    def clear_ghost_score(
        self: "GameState",
    ) -> None:
        self.score_popup = None

    def start_phase(
        self: "GameState",
        phase: GamePhase,
        duration: float,
    ) -> None:
        self.phase = phase
        self.phase_duration = max(0.0, duration)
        self.phase_time_remaining = self.phase_duration

    def update_phase(
        self: "GameState",
        delta_time: float,
    ) -> None:
        if self.phase == GamePhase.PLAYING:
            return

        self.phase_time_remaining = max(
            0.0,
            self.phase_time_remaining - delta_time,
        )

    def finish_phase(
        self: "GameState",
    ) -> None:
        self.phase = GamePhase.PLAYING
        self.phase_time_remaining = 0.0
        self.phase_duration = 0.0

    def consume_ghost_score(
        self: "GameState",
        base_score: int,
    ) -> int:
        score = base_score * (
            2 ** self.ghosts_eaten_in_power_mode
        )

        self.ghosts_eaten_in_power_mode += 1

        return score


@dataclass
class AppState:
    """Global application state."""
    current_screen: ScreenType
    config: Config
    game_state: GameState | None = None
    running: bool = True
