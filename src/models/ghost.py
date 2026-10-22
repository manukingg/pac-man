"""Ghost state model."""

from dataclasses import dataclass
from enum import Enum, auto

from .common import Direction, GridPosition, Position


class GhostMode(Enum):
    """Current behavioral state of a ghost."""

    CHASE = auto()
    FRIGHTENED = auto()
    FRIGHTENED_WARNING = auto()
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

    force_reverse_pending: bool = False

    @property
    def edible(self: "GhostModel") -> bool:
        """Return whether the ghost can currently be eaten."""

        return self.frightened

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

    @property
    def frightened(self: "GhostModel") -> bool:
        return self.mode in {
            GhostMode.FRIGHTENED,
            GhostMode.FRIGHTENED_WARNING,
        }

    def move_to(self: "GhostModel", position: Position) -> None:
        """Move the ghost to a validated maze position."""

        self.position = position

    def move_to_grid(
        self: "GhostModel",
        position: GridPosition,
    ) -> None:
        self.grid_position = position

    def change_direction(self: "GhostModel", direction: Direction) -> None:
        """Change the ghost movement direction."""

        self.direction = direction

    def frighten(self: "GhostModel") -> None:
        """Make the ghost edible for a limited duration."""

        if self.mode in {
            GhostMode.EATEN,
            GhostMode.RESPAWNING,
        }:
            return

        self.mode = GhostMode.FRIGHTENED

        if self.direction != Direction.NONE:
            self.direction = self.direction.reversed()
            self.force_reverse_pending = True

        self.set_speed(0.65)

    def frighten_warning(self: "GhostModel") -> None:
        """Make the ghost frighten almost ended"""

        if self.mode in {
            GhostMode.EATEN,
            GhostMode.RESPAWNING,
        }:
            return

        self.mode = GhostMode.FRIGHTENED_WARNING

    def restore_chase_mode(self) -> None:
        """Return the ghost to its normal chase behavior."""

        self.mode = GhostMode.CHASE
        self.set_speed(1)

    def eat(self: "GhostModel", respawn_delay: float) -> None:
        """Mark the ghost as eaten and start its respawn delay."""

        if not self.edible:
            return

        self.mode = GhostMode.EATEN
        self.force_reverse_pending = False
        self.respawn_time_remaining = max(0.0, respawn_delay)

    def begin_respawn(self: "GhostModel", position: Position) -> None:
        """Move the ghost back to its corner and start respawning."""

        self.grid_position = self.spawn_position
        self.position = position
        self.direction = Direction.NONE
        self.mode = GhostMode.RESPAWNING
        self.force_reverse_pending = False

    def finish_respawn(self: "GhostModel") -> None:
        """Return the ghost to the active chase state."""

        self.mode = GhostMode.CHASE
        self.respawn_time_remaining = 0.0
        self.force_reverse_pending = False

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

    def finish_forced_reverse(
        self: "GhostModel"
    ) -> None:
        self.force_reverse_pending = False

    def set_speed(self: "GhostModel", speed: float) -> None:
        self.speed_multiplier = speed
