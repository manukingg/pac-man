"""Player state model."""

from dataclasses import dataclass

from .common import Direction, GridPosition, Position


@dataclass(slots=True)
class PlayerModel:
    """Mutable state of the Pac-Man player."""

    grid_position: GridPosition
    spawn_grid_position: GridPosition
    position: Position | None = None

    direction: Direction = Direction.NONE
    requested_direction: Direction = Direction.NONE

    alive: bool = True
    invincible: bool = False
    speed_multiplier: float = 2

    def request_move(self: "PlayerModel", direction: Direction) -> None:
        """Remember the direction requested by the player."""

        self.requested_direction = direction

    def move_to(self: "PlayerModel", position: Position) -> None:
        """Move the player to a validated maze position."""

        self.position = position

    def move_to_grid(
        self: "PlayerModel",
        position: GridPosition,
    ) -> None:
        self.grid_position = position

    def change_direction(self: "PlayerModel", direction: Direction) -> None:
        """Change the current movement direction."""

        self.direction = direction

    def die(self: "PlayerModel") -> None:
        """Mark the player as dead unless invincibility is active."""

        if not self.invincible:
            self.alive = False

    def respawn(self: "PlayerModel", position: Position) -> None:
        """Respawn the player at the initial maze position."""

        self.grid_position = self.spawn_grid_position
        self.position = position
        self.direction = Direction.NONE
        self.requested_direction = Direction.NONE
        self.alive = True
