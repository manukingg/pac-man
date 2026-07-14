from ..models import GameState, Config, PlayerModel, GhostModel


class GameStateFactory:
    """Create initialized game states."""

    def __init__(
        self: 'GameStateFactory',
        config: Config
    ) -> None:
        self.__config = config

    def __create_player(self: 'GameStateFactory') -> PlayerModel:
        pass

    def __create_ghosts(self: 'GameStateFactory') -> list[GhostModel]:
        pass
