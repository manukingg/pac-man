"""Player state model."""

from dataclasses import dataclass

from .common import Direction, GridPosition


@dataclass(slots=True)
class PlayerModel:
    """Mutable state of the Pac-Man player."""

    position: GridPosition
    spawn_position: GridPosition

    direction: Direction = Direction.NONE
    requested_direction: Direction = Direction.NONE

    alive: bool = True
    invincible: bool = False
    speed_multiplier: float = 1.0

    def request_move(self, direction: Direction) -> None:
        """Remember the direction requested by the player."""

        self.requested_direction = direction

    def move_to(self, position: GridPosition) -> None:
        """Move the player to a validated maze position."""

        self.position = position

    def change_direction(self, direction: Direction) -> None:
        """Change the current movement direction."""

        self.direction = direction

    def die(self) -> None:
        """Mark the player as dead unless invincibility is active."""

        if not self.invincible:
            self.alive = False

    def respawn(self) -> None:
        """Respawn the player at the initial maze position."""

        self.position = self.spawn_position
        self.direction = Direction.NONE
        self.requested_direction = Direction.NONE
        self.alive = True
