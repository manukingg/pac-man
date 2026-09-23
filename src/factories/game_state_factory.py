from ..models import (
    Config,
    GameState,
    GhostKind,
    GhostModel,
    GridPosition,
    Level,
    PlayerModel,
    MazeGrid
)
from ..services import MazeGeneratorService


class GameStateFactory:
    """Create initialized game states."""

    def __init__(
        self: "GameStateFactory",
        config: Config,
    ) -> None:
        self.__config = config
        self.__generator_service = MazeGeneratorService(config)

    def create(
        self: "GameStateFactory",
        level: Level,
    ) -> GameState:
        """Create a fully initialized game state."""

        maze = self.__generator_service.generate()
        player = self.__create_player(level)
        ghosts = self.__create_ghosts(level)
        pallets = self.__create_pallets(maze)

        return GameState(
            maze=maze,
            ghosts=ghosts,
            player=player,
            score=0,
            lives=self.__config.lives,
            level=level.level_number,
            remaining_time=float(self.__config.level_max_time),
            pallets=pallets
        )

    def __create_pallets(
        self: "GameStateFactory",
        maze: MazeGrid
    ) -> set[GridPosition]:
        pallets: set[GridPosition] = set()
        for row_index, row in enumerate(maze):
            for col_index, cell in enumerate(row):
                if cell != 15:
                    pallets.add(GridPosition(row=row_index, column=col_index))
        return pallets

    def __create_player(
        self: "GameStateFactory",
        level: Level,
    ) -> PlayerModel:
        """Create the player in the center of the level."""

        position = GridPosition(
            row=level.height // 2 - 1,
            column=level.width // 2 - 1,
        )

        return PlayerModel(
            grid_position=position,
            spawn_grid_position=position,
        )

    def __create_ghosts(
        self: "GameStateFactory",
        level: Level,
    ) -> list[GhostModel]:
        """Create one ghost in each corner of the level."""

        spawn_positions = {
            GhostKind.BLINKY: GridPosition(
                row=0,
                column=0,
            ),
            GhostKind.PINKY: GridPosition(
                row=0,
                column=level.width - 1,
            ),
            GhostKind.INKY: GridPosition(
                row=level.height - 1,
                column=0,
            ),
            GhostKind.CLYDE: GridPosition(
                row=level.height - 1,
                column=level.width - 1,
            ),
        }

        ghosts: list[GhostModel] = []

        for kind in GhostKind:
            spawn_position = spawn_positions[kind]

            ghosts.append(
                GhostModel(
                    kind=kind,
                    position=spawn_position,
                    spawn_position=spawn_position,
                )
            )

        return ghosts
