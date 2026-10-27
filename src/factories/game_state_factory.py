from ..models import (
    Config,
    GameState,
    GhostKind,
    GhostModel,
    GridPosition,
    Level,
    PlayerModel,
    MazeGrid,
    Direction
)
from ..services import MazeGeneratorService


class GameStateFactory:
    """Create initialized game states."""

    def __init__(
        self: "GameStateFactory",
        config: Config,
    ) -> None:
        self.__config: Config = config
        self.__generator_service: MazeGeneratorService | None = None

    def create(
        self: "GameStateFactory",
        level: Level,
    ) -> GameState:
        """Create a fully initialized game state."""

        self.__generator_service = MazeGeneratorService(
            seed=self.__config.seed,
            level=level,
        )
        maze = self.__generator_service.generate()
        player = self.__create_player(level)
        ghosts = self.__create_ghosts(level)
        power_pellets = self.__create_power_pellets(maze)
        pellets = self.__create_pellets(maze, power_pellets, player)

        return GameState(
            maze=maze,
            ghosts=ghosts,
            player=player,
            score=0,
            lives=self.__config.lives,
            level=level,
            remaining_time=float(self.__config.level_max_time),
            pellets=pellets,
            power_pellets=power_pellets,
        )

    def __create_player(
        self: "GameStateFactory",
        level: Level,
    ) -> PlayerModel:
        """Create the player in the center of the level."""

        position = GridPosition(
            row=level.height // 2 - 1,
            column=level.width // 2 - 1,
        )

        player = PlayerModel(
            grid_position=position,
            spawn_grid_position=position,
        )

        player.set_speed(level.pacman_speed_multiplier)

        return player

    def __create_ghosts(
        self: "GameStateFactory",
        level: Level,
    ) -> list[GhostModel]:
        """Create one ghost in each corner of the level."""

        spawn_positions = {
            GhostKind.BLINKY: GridPosition(
                row=0,
                column=level.width - 1,
            ),
            GhostKind.PINKY: GridPosition(
                row=0,
                column=0,
            ),
            GhostKind.INKY: GridPosition(
                row=level.height - 1,
                column=level.width - 1,
            ),
            GhostKind.CLYDE: GridPosition(
                row=level.height - 1,
                column=0,
            ),
        }

        ghosts: list[GhostModel] = []

        for kind in GhostKind:
            spawn_position = spawn_positions[kind]
            ghost = GhostModel(
                        kind=kind,
                        grid_position=spawn_position,
                        spawn_position=spawn_position,
                        direction=Direction.LEFT
                    )
            ghost.set_speed(level.ghost_speed_multiplier)
            ghosts.append(ghost)

        return ghosts

    def __create_pellets(
        self: "GameStateFactory",
        maze: MazeGrid,
        power_pellets: set[GridPosition],
        player: PlayerModel,
    ) -> set[GridPosition]:
        pellets: set[GridPosition] = set()

        for row_index, row in enumerate(maze):
            for col_index, cell in enumerate(row):
                position = GridPosition(row=row_index, column=col_index)
                if cell != 15 and position not in power_pellets:
                    pellets.add(position)
        pellets.discard(player.grid_position)
        return pellets

    def __create_power_pellets(
        self: "GameStateFactory",
        maze: MazeGrid
    ) -> set[GridPosition]:
        return {
            GridPosition(row=0, column=0),
            GridPosition(row=0, column=len(maze[0]) - 1),
            GridPosition(row=len(maze) - 1, column=0),
            GridPosition(row=len(maze) - 1, column=len(maze[0]) - 1)
        }
