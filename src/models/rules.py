from dataclasses import dataclass


@dataclass(frozen=True)
class GameRules:
    score_per_pacgum: int
    score_per_super_pacgum: int
    score_per_ghost: int
