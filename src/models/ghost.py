"""Ghost state model."""

from dataclasses import dataclass
from enum import Enum, auto

from .common import Direction, GridPosition, Position


class GhostMode(Enum):
    """Current behavioral state of a ghost."""

    CHASE = auto()
    FRIGHTENED = auto()
    EATEN = auto()
    RESPAWNING = auto()
    FROZEN = auto()


class GhostKind(Enum):
    """Identity of one of the four ghosts."""

    BLINKY = auto()
    PINKY = auto()
    INKY = auto()
    CLYDE = auto()


@dataclass(slots=True)
class GhostModel:
    """Mutable state of a single ghost."""

    kind: GhostKind

    grid_position: GridPosition
    spawn_position: GridPosition

    speed_multiplier: float = 1.0

    direction: Direction = Direction.NONE
    position: Position | None = None
    mode: GhostMode = GhostMode.CHASE
    respawn_time_remaining: float = 0.0
    frightened_time_remaining: float = 0.0

    @property
    def edible(self: "GhostModel") -> bool:
        """Return whether the ghost can currently be eaten."""

        return self.mode is GhostMode.FRIGHTENED

    @property
    def dangerous(self: "GhostModel") -> bool:
        """Return whether touching the ghost harms the player."""

        return self.mode is GhostMode.CHASE

    @property
    def active(self: "GhostModel") -> bool:
        """Return whether the ghost may currently move."""

        return self.mode not in {
            GhostMode.RESPAWNING,
            GhostMode.FROZEN,
        }

    def move_to(self: "GhostModel", position: GridPosition) -> None:
        """Move the ghost to a validated maze position."""

        self.position = position

    def change_direction(self: "GhostModel", direction: Direction) -> None:
        """Change the ghost movement direction."""

        self.direction = direction

    def frighten(self: "GhostModel", duration: float) -> None:
        """Make the ghost edible for a limited duration."""

        if self.mode in {
            GhostMode.EATEN,
            GhostMode.RESPAWNING,
        }:
            return

        self.mode = GhostMode.FRIGHTENED
        self.frightened_time_remaining = max(0.0, duration)

    def restore_chase_mode(self) -> None:
        """Return the ghost to its normal chase behavior."""

        self.mode = GhostMode.CHASE
        self.frightened_time_remaining = 0.0

    def eat(self: "GhostModel", respawn_delay: float) -> None:
        """Mark the ghost as eaten and start its respawn delay."""

        if not self.edible:
            return

        self.mode = GhostMode.EATEN
        self.frightened_time_remaining = 0.0
        self.respawn_time_remaining = max(0.0, respawn_delay)

    def begin_respawn(self: "GhostModel", position: Position) -> None:
        """Move the ghost back to its corner and start respawning."""

        self.grid_position = self.spawn_position
        self.position = position
        self.direction = Direction.NONE
        self.mode = GhostMode.RESPAWNING

    def finish_respawn(self: "GhostModel") -> None:
        """Return the ghost to the active chase state."""

        self.mode = GhostMode.CHASE
        self.respawn_time_remaining = 0.0

    def increase_speed(self: "GhostModel") -> None:
        """Increase ghost's speed after respawn"""

        self.speed_multiplier += 0.5

    def freeze(self: "GhostModel") -> None:
        """Freeze the ghost for cheat mode."""

        self.mode = GhostMode.FROZEN

    def unfreeze(self: "GhostModel") -> None:
        """Return a frozen ghost to chase mode."""

        if self.mode is GhostMode.FROZEN:
            self.mode = GhostMode.CHASE
