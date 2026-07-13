from dataclasses import dataclass

from .config import Config
from .ghost import GhostModel
from .player import PlayerModel
from .screen import ScreenType


@dataclass
class GameState:
    """Mutable state of the current game session."""
    # maze: Any | TODO: Add when maze generator will be integrated
    ghosts: list[GhostModel]
    player: PlayerModel
    score: int = 0
    lives: int = 3
    level: int = 1
    remaining_time: float = 90.0
    paused: bool = False
    ghosts_edible: bool = False
    ghosts_edible_time: float = 0.0


@dataclass
class AppState:
    """Global application state."""
    current_screen: ScreenType
    config: Config
    game_state: GameState | None = None 
    running: bool = True
