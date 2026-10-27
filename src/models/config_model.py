from pydantic import BaseModel, Field, ConfigDict
from .rules import GameRules


DEFAULT_LEVELS = [
        {
            "level_number": 1,
            "width": 14,
            "height": 10,
            "frightened_duration": 6.0,
            "frightened_speed_multiplier": 0.50,
            "ghost_speed_multiplier": 0.75,
            "pacman_speed_multiplier": 0.80,
            "powered_pacman_speed_multiplier": 0.90
        },
        {
            "level_number": 2,
            "width": 7,
            "height": 5,
            "frightened_duration": 5.0,
            "frightened_speed_multiplier": 0.55,
            "ghost_speed_multiplier": 0.85,
            "pacman_speed_multiplier": 0.90,
            "powered_pacman_speed_multiplier": 0.95
        },
        {
            "level_number": 3,
            "width": 8,
            "height": 8,
            "frightened_duration": 4.0,
            "frightened_speed_multiplier": 0.55,
            "ghost_speed_multiplier": 0.85,
            "pacman_speed_multiplier": 0.90,
            "powered_pacman_speed_multiplier": 0.95
        },

        {
            "level_number": 4,
            "width": 10,
            "height": 8,
            "frightened_duration": 3.0,
            "frightened_speed_multiplier": 0.55,
            "ghost_speed_multiplier": 0.85,
            "pacman_speed_multiplier": 0.90,
            "powered_pacman_speed_multiplier": 0.95
        },
        {
            "level_number": 5,
            "width": 13,
            "height": 9,
            "frightened_duration": 2.0,
            "frightened_speed_multiplier": 0.60,
            "ghost_speed_multiplier": 0.95,
            "pacman_speed_multiplier": 1.00,
            "powered_pacman_speed_multiplier": 1.00
        },
        {
            "level_number": 6,
            "width": 14,
            "height": 10,
            "frightened_duration": 5.0,
            "frightened_speed_multiplier": 0.60,
            "ghost_speed_multiplier": 0.95,
            "pacman_speed_multiplier": 1.00,
            "powered_pacman_speed_multiplier": 1.00
        },
        {
            "level_number": 7,
            "width": 14,
            "height": 14,
            "frightened_duration": 2.0,
            "frightened_speed_multiplier": 0.60,
            "ghost_speed_multiplier": 0.95,
            "pacman_speed_multiplier": 1.00,
            "powered_pacman_speed_multiplier": 1.00
        },
        {
            "level_number": 8,
            "width": 18,
            "height": 14,
            "frightened_duration": 1.0,
            "frightened_speed_multiplier": 0.60,
            "ghost_speed_multiplier": 0.95,
            "pacman_speed_multiplier": 1.00,
            "powered_pacman_speed_multiplier": 1.00
        },
        {
            "level_number": 9,
            "width": 18,
            "height": 18,
            "frightened_duration": 5.0,
            "frightened_speed_multiplier": 0.60,
            "ghost_speed_multiplier": 0.95,
            "pacman_speed_multiplier": 1.00,
            "powered_pacman_speed_multiplier": 1.00
        },
        {
            "level_number": 10,
            "width": 22,
            "height": 18,
            "frightened_duration": 5.0,
            "frightened_speed_multiplier": 0.60,
            "ghost_speed_multiplier": 0.95,
            "pacman_speed_multiplier": 1.00,
            "powered_pacman_speed_multiplier": 1.00
        }
    ]


class Level(BaseModel):
    model_config = ConfigDict(extra="ignore")

    level_number: int

    width: int
    height: int

    pacman_speed_multiplier: float = Field(
        ge=0.0,
        le=2.0,
    )
    powered_pacman_speed_multiplier: float = Field(
        ge=0.0,
        le=2.0,
    )

    frightened_duration: float = Field(
        ge=0.0,
        le=10.0,
    )
    frightened_speed_multiplier: float = Field(
        ge=0.0,
        le=2.0,
    )
    ghost_speed_multiplier: float = Field(
        ge=0.0,
        le=2.0
    )


class Config(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_default=True)

    highscore_filename: str = "highscores.json"

    levels: list[Level] = Field(
        default_factory=lambda: [
            Level.model_validate(level) for level in DEFAULT_LEVELS
        ]
    )
    lives: int = Field(default=3, ge=1, le=10)
    pacgum: int = Field(default=42, ge=0)
    window_width: int = 1800
    window_height: int = 1200
    seed: str = "42"
    level_max_time: int = Field(default=90, ge=90, le=500)
    game_rules: GameRules = Field(
        default_factory=GameRules
    )

    def get_level(
        self: "Config",
        level_number: int,
    ) -> Level:
        for level in self.levels:
            if level.level_number == level_number:
                return level

        raise ValueError(
            f"Level {level_number} is not configured"
        )
