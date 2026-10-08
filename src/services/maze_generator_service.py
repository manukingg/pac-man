import random
from mazegenerator import MazeGenerator

from ..models import Config, MazeGrid, Wall, Level


class MazeGeneratorService:

    def __init__(
        self: 'MazeGeneratorService',
        config: Config,
        level: Level
    ) -> None:
        random.seed(int(config.seed))
        entry: tuple[int, int] = (random.randint(0, level.width - 1),
                                  random.randint(0, level.height - 1))
        exit: tuple[int, int] = (random.randint(0, level.width - 1),
                                 random.randint(0, level.height - 1))
        while entry == exit:
            exit: tuple[int, int] = (
                random.randint(0, level.width - 1),
                random.randint(0, level.height - 1)
            )
        self.__generator = MazeGenerator(
            size=(level.width, level.height),
            perfect=False,
            entry_cell=entry,
            exit_cell=exit,
            seed=int(config.seed)
        )
        self.__seed: int = int(config.seed)

    def generate(self: 'MazeGeneratorService') -> MazeGrid:
        self.__generator.generate(self.__seed)
        raw_maze = self.__generator.maze
        grid: MazeGrid = [
            [Wall(value) for value in row]
            for row in raw_maze
        ]
        print(self.__generator._width, self.__generator._height)
        return grid
