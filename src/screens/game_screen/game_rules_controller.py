from ...models import GameState, GridPosition, GameRules, GhostMode

FRIGHTENED_WARNING_TIME = 2


class GameRulesController:
    def __init__(
        self: "GameRulesController",
        rules: GameRules,
    ) -> None:
        self.__rules = rules

    def update(
        self: "GameRulesController",
        game_state: GameState,
        reached_cells: list[GridPosition],
        delta_time: float,
    ) -> None:
        self.__handle_timers(
            game_state=game_state,
            delta_time=delta_time,
        )
        self.__handle_pickups(
            game_state=game_state,
            reached_cells=reached_cells,
        )

        # self.__handle_collisions()

    def __handle_pickups(
        self: "GameRulesController",
        game_state: GameState,
        reached_cells: list[GridPosition],
    ) -> None:
        for cell in reached_cells:
            if cell in game_state.pellets:
                game_state.remove_pellet(cell)
                game_state.add_score(self.__rules.score_per_pacgum)
            elif cell in game_state.power_pellets:
                game_state.remove_power_pellet(cell)
                game_state.add_score(self.__rules.score_per_super_pacgum)
                game_state.activate_power_mode(6)
                self.__make_ghosts_edible(game_state=game_state)

    def __make_ghosts_edible(
        self: "GameRulesController",
        game_state: GameState,
    ) -> None:
        for ghost in game_state.ghosts:
            ghost.frighten()

    # def __handle_collision(
    #     self: "GameRulesController",
    #     game_state: GameState,
    # ) -> None:
    #     for ghost in game_state.ghosts:
    #         if ghost.position

    def __handle_timers(
        self: "GameRulesController",
        game_state: GameState,
        delta_time: float,
    ) -> None:
        game_state.update_remaining_time(delta_time=delta_time)
        game_state.update_power_mode(delta_time=delta_time)

        for ghost in game_state.ghosts:
            if (
                ghost.mode == GhostMode.FRIGHTENED
                and (0 < game_state.power_mode_remaining
                     < FRIGHTENED_WARNING_TIME)
            ):
                print(ghost.mode)
                ghost.frighten_warning()
                print(ghost.mode)
            elif (
                ghost.mode == GhostMode.FRIGHTENED_WARNING
                and FRIGHTENED_WARNING_TIME < game_state.power_mode_remaining
            ):
                ghost.frighten()
            elif (
                ghost.mode == GhostMode.FRIGHTENED_WARNING
                and game_state.power_mode_remaining <= 0
            ):
                ghost.restore_chase_mode()
