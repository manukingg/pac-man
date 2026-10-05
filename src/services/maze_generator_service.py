from mazegenerator import MazeGenerator

from ..models import Config, MazeGrid, Wall


class MazeGeneratorService:

    def __init__(self: 'MazeGeneratorService', config: Config) -> None:
        self.__generator = MazeGenerator(
            size=(20, 20),
            perfect=False,
            entry_cell=(0, 0),
            exit_cell=(2, 2),
            seed=int(config.seed)
        )

    def generate(self: 'MazeGeneratorService') -> MazeGrid:
        self.__generator.generate()
        raw_maze = self.__generator.maze
        grid: MazeGrid = [
            [Wall(value) for value in row]
            for row in raw_maze
        ]
        return grid
