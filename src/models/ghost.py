"""Ghost state model."""

from dataclasses import dataclass
from enum import Enum, auto

from .common import Direction, GridPosition, Position


class GhostMode(Enum):
    """Current behavioral state of a ghost."""

    CHASE = auto()
    SCATTER = auto()
    FRIGHTENED = auto()
    EATEN = auto()
    FROZEN = auto()
    RESPAWNING = auto()


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

    respawn_time_remaining: float = 0.0

    direction: Direction = Direction.NONE
    position: Position | None = None
    mode: GhostMode = GhostMode.CHASE

    force_reverse_pending: bool = False

    @property
    def edible(self: "GhostModel") -> bool:
        """Return whether the ghost can currently be eaten."""

        return self.frightened

    @property
    def dangerous(self: "GhostModel") -> bool:
        """Return whether touching the ghost harms the player."""

        return self.mode in (GhostMode.CHASE, GhostMode.SCATTER)

    @property
    def active(self: "GhostModel") -> bool:
        """Return whether the ghost may currently move."""

        return self.mode != GhostMode.FROZEN

    @property
    def frightened(self: "GhostModel") -> bool:
        return self.mode == GhostMode.FRIGHTENED

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

    def frighten(self: "GhostModel", speed_multiplier: float) -> None:
        """Make the ghost edible for a limited duration."""

        if self.mode not in (GhostMode.CHASE, GhostMode.SCATTER):
            return

        self.mode = GhostMode.FRIGHTENED

        if self.direction != Direction.NONE:
            self.direction = self.direction.reversed()
            self.force_reverse_pending = True

        self.set_speed(speed_multiplier)

    def restore_normal_mode(
        self: "GhostModel",
        mode: GhostMode,
        speed_multiplier: float
    ) -> None:
        """Return the ghost to its normal chase behavior."""
        if mode not in (GhostMode.CHASE, GhostMode.SCATTER):
            raise ValueError("Normal ghost mode must be CHSE or SCATTER")

        self.mode = mode
        self.force_reverse_pending = False

        self.set_speed(speed_multiplier)

    def switch_behavior(self: "GhostModel", mode: GhostMode) -> None:
        if mode not in (GhostMode.CHASE, GhostMode.SCATTER):
            raise ValueError("Ghost behavior must be CHASE or SCATTER")

        if self.mode not in (GhostMode.CHASE, GhostMode.SCATTER):
            return

        if self.mode == mode:
            return

        self.mode = mode

        if self.direction != Direction.NONE:
            self.direction = self.direction.reversed()
            self.force_reverse_pending = True

    def eat(self: "GhostModel", speed_multiplier: float) -> None:
        """Mark the ghost as eaten."""
        if not self.edible:
            return

        self.mode = GhostMode.EATEN
        self.force_reverse_pending = False
        self.set_speed(speed_multiplier)

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

    def reset_to_spawn(
        self: "GhostModel",
        mode: GhostMode,
        speed_multiplier: float,
    ) -> None:
        self.grid_position = self.spawn_position
        self.position = None

        self.direction = Direction.NONE
        self.force_reverse_pending = False
        self.respawn_time_remaining = 0.0
        self.restore_normal_mode(
            mode=mode,
            speed_multiplier=speed_multiplier,
        )

    def start_respawning(
        self: "GhostModel",
        duration: float,
    ) -> None:
        if self.mode != GhostMode.EATEN:
            return

        self.mode = GhostMode.RESPAWNING

        self.respawn_time_remaining = max(0.0, duration)

        self.force_reverse_pending = False

    def update_respawn(
        self: "GhostModel",
        delta_time: float,
    ) -> None:
        if self.mode != GhostMode.RESPAWNING:
            return

        self.respawn_time_remaining = max(
            0.0,
            self.respawn_time_remaining - delta_time
        )

    def finish_respawn(
        self: "GhostModel",
        mode: GhostMode,
        speed_multiplier: float,
    ) -> None:
        if self.mode != GhostMode.RESPAWNING:
            return

        self.respawn_time_remaining = 0.0

        self.restore_normal_mode(
            mode=mode,
            speed_multiplier=speed_multiplier,
        )


@dataclass(slots=True)
class ScorePopup:
    ghost_kind: GhostKind
    position: Position
    score: int
