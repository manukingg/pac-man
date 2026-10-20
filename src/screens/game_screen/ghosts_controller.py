from ...models import GhostAssets, GhostModel,  Direction, MazeGrid
from .maze_navigator import MazeNavigator
from .game_layout import GameLayout

import random


class GhostsController:
    def __init__(
        self: "GhostsController",
        ghosts_sprites: GhostAssets,
        maze_navigator: MazeNavigator,
    ) -> None:
        self.__ghosts_sprites = ghosts_sprites
        self.__maze_navigator = maze_navigator

    def initialize_ghosts_position(
        self: "GhostsController",
        ghosts: list[GhostModel],
        maze: MazeGrid,
        layout: GameLayout,
    ) -> None:

        for ghost in ghosts:
            if ghost.position is not None:
                continue
            position = layout.get_grid_position_center(
                position=ghost.grid_position
            )
            possible_directions = [
                direction
                for direction in (
                    Direction.UP,
                    Direction.DOWN,
                    Direction.LEFT,
                    Direction.RIGHT,
                )
                if self.__maze_navigator.can_move(
                    maze=maze,
                    position=ghost.grid_position,
                    direction=direction,
                )
            ]
            ghost.direction = random.choice(possible_directions)

            ghost.move_to(position)
