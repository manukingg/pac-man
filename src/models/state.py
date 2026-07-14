from dataclasses import dataclass

from .config_model import Config
from .ghost import GhostModel
from .player import PlayerModel
from .screen import ScreenType
from .maze import MazeModel


@dataclass
class GameState:
    """Mutable state of the current game session."""
    maze: MazeModel
    ghosts: list[GhostModel]
    player: PlayerModel
    score: int
    lives: int
    level: int
    remaining_time: float
    paused: bool = False
    power_mode_remaining: float = 0.0

    @property
    def ghosts_are_edible(self) -> bool:
        """Return whether ghosts are currently edible."""
        return self.power_mode_remaining > 0.0

@dataclass
class AppState:
    """Global application state."""
    current_screen: ScreenType
    config: Config
    game_state: GameState | None = None 
    running: bool = True
