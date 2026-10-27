from ...models import (
    GameState,
    Position,
    GridPosition,
    GameRules,
    GhostModel,
    GamePhase,
    PlayerModel,
    GhostMode
)

COLLISION_TRESHOLD = 0.0001
EATEN_GHOST_SPEED_MULTIPLIER = 1.0

GHOST_BEHAVIOR_SCHEDULE = (
    (GhostMode.CHASE, 20.0),
    (GhostMode.SCATTER, 7.0),
    (GhostMode.CHASE, 20.0),
    (GhostMode.SCATTER, 7.0),
    (GhostMode.CHASE, 20.0),
    (GhostMode.SCATTER, 5.0),
)


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
        collision_distance: float,
    ) -> None:
        self.__handle_timers(
            game_state=game_state,
            delta_time=delta_time,
        )
        self.__handle_pickups(
            game_state=game_state,
            reached_cells=reached_cells,
        )

        self.__handle_collisions(
            game_state=game_state,
            collision_distance=collision_distance
        )

    def update_phase(
        self: "GameRulesController",
        game_state: GameState,
        delta_time: float,
    ) -> bool:
        """Return false if you can continue playing
        true if gameplay blocked"""
        if game_state.phase == GamePhase.PLAYING:
            return False

        game_state.update_phase(delta_time)

        if game_state.phase_time_remaining > 0:
            return True

        finished_phase = game_state.phase

        if finished_phase == GamePhase.GHOST_EATEN:
            game_state.clear_ghost_score()

        elif finished_phase == GamePhase.PLAYER_DEATH:
            if game_state.lives > 0:
                self.__reset_round(game_state)

        game_state.finish_phase()

        return False

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
                self.__eat_power_pellet(
                    game_state=game_state,
                    position=cell,
                )

    def __handle_collisions(
        self: "GameRulesController",
        game_state: GameState,
        collision_distance: float,
    ) -> None:
        player = game_state.player

        if player.position is None:
            return

        for ghost in game_state.ghosts:

            if ghost.position is None:
                continue

            if self.__is_colliding(
                first=ghost.position,
                second=player.position,
                collision_distance=collision_distance,
            ):
                if ghost.edible:
                    self.__eat_ghost(ghost=ghost, game_state=game_state)
                    return
                elif ghost.dangerous:
                    self.__kill_player(game_state=game_state, player=player)
                    return

    def __handle_timers(
        self: "GameRulesController",
        game_state: GameState,
        delta_time: float,
    ) -> None:
        game_state.update_remaining_time(delta_time=delta_time)

        power_mode_was_active = game_state.power_mode_active

        game_state.update_power_mode(delta_time=delta_time)

        if not power_mode_was_active:
            self.__update_ghost_behavior(
                game_state=game_state,
                delta_time=delta_time,
            )

        if power_mode_was_active and not game_state.power_mode_active:
            self.__finish_power_mode(game_state=game_state)

    def __is_colliding(
        self: "GameRulesController",
        first: Position,
        second: Position,
        collision_distance: float
    ) -> bool:
        # dx = first.x - second.x
        # dy = first.y - second.y

        # return (
        #     dx * dx + dy * dy
        #     <= collision_distance * collision_distance
        # )
        return (
            (
                first.x == second.x and
                abs(first.y - second.y) <= collision_distance
            )
            or (
                first.y == second.y and
                abs(first.x - second.x) <= collision_distance
            )
        )

    def __eat_ghost(
        self: "GameRulesController",
        ghost: GhostModel,
        game_state: GameState,
    ) -> None:
        if ghost.position is None:
            return

        score = game_state.consume_ghost_score(
            base_score=self.__rules.score_per_ghost
        )

        game_state.add_score(score)

        game_state.show_ghost_score(
            ghost_kind=ghost.kind,
            position=ghost.position,
            score=score,
        )
        ghost.eat(speed_multiplier=EATEN_GHOST_SPEED_MULTIPLIER)
        game_state.start_phase(phase=GamePhase.GHOST_EATEN, duration=1.0)

    def __kill_player(
        self: "GameRulesController",
        game_state: GameState,
        player: PlayerModel,
    ) -> None:
        if player.invincible:
            return

        player.die()
        game_state.lose_life()
        game_state.start_phase(GamePhase.PLAYER_DEATH, duration=2.0)

    def __eat_power_pellet(
        self: "GameRulesController",
        game_state: GameState,
        position: GridPosition,
    ) -> None:
        game_state.remove_power_pellet(position)

        game_state.add_score(self.__rules.score_per_super_pacgum)

        game_state.activate_power_mode(game_state.level.frightened_duration)

        game_state.player.set_speed(
            game_state.level.powered_pacman_speed_multiplier
        )
        for ghost in game_state.ghosts:
            ghost.frighten(
                speed_multiplier=(
                    game_state.level.frightened_speed_multiplier
                )
            )

    def __finish_power_mode(
        self: "GameRulesController",
        game_state: GameState,
    ) -> None:
        game_state.player.set_speed(
            game_state.level.pacman_speed_multiplier
        )

        for ghost in game_state.ghosts:
            if not ghost.frightened:
                continue

            ghost.restore_normal_mode(
                mode=game_state.ghost_behavior_mode,
                speed_multiplier=(
                    game_state.level.ghost_speed_multiplier
                ),
            )

        game_state.ghosts_eaten_in_power_mode = 0

    def __reset_round(
        self: "GameRulesController",
        game_state: GameState,
    ) -> None:
        self.__reset_ghost_behavior(game_state=game_state)
        game_state.player.respawn()

        game_state.player.set_speed(
            game_state.level.pacman_speed_multiplier
        )

        for ghost in game_state.ghosts:
            ghost.reset_to_spawn(
                mode=game_state.ghost_behavior_mode,
                speed_multiplier=game_state.level.ghost_speed_multiplier
            )

        game_state.power_mode_remaining = 0.0
        game_state.clear_ghost_score()

    def __update_ghost_behavior(
        self: "GameRulesController",
        game_state: GameState,
        delta_time: float,
    ) -> None:
        if game_state.ghost_behavior_time_remaining is None:
            return

        game_state.ghost_behavior_time_remaining = max(
            0.0,
            game_state.ghost_behavior_time_remaining - delta_time
        )

        if game_state.ghost_behavior_time_remaining > 0:
            return

        next_index = game_state.ghost_behavior_index + 1

        if next_index >= len(GHOST_BEHAVIOR_SCHEDULE):
            game_state.ghost_behavior_index = next_index
            game_state.ghost_behavior_mode = GhostMode.CHASE
            game_state.ghost_behavior_time_remaining = None

            self.__switch_ghost_behavior(
                game_state=game_state,
                mode=GhostMode.CHASE,
            )

            return

        mode, duration = GHOST_BEHAVIOR_SCHEDULE[next_index]

        game_state.ghost_behavior_index = next_index
        game_state.ghost_behavior_mode = mode
        game_state.ghost_behavior_time_remaining = duration

        self.__switch_ghost_behavior(
            game_state=game_state,
            mode=mode,
        )

    def __switch_ghost_behavior(
        self: "GameRulesController",
        game_state: GameState,
        mode: GhostMode,
    ) -> None:
        for ghost in game_state.ghosts:
            ghost.switch_behavior(mode)

    def __reset_ghost_behavior(
        self: "GameRulesController",
        game_state: GameState,
    ) -> None:
        mode, duration = GHOST_BEHAVIOR_SCHEDULE[0]

        game_state.ghost_behavior_index = 0
        game_state.ghost_behavior_mode = mode
        game_state.ghost_behavior_time_remaining = duration
