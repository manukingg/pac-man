from pydantic import BaseModel, Field, ConfigDict
    
DEFAULT_LEVELS = [
    {"level_number": 1, "width": "15", "height": "15"},
    {"level_number": 2, "width": "20", "height": "18"},
    {"level_number": 3, "width": "20", "height": "20"},
    {"level_number": 4, "width": "25", "height": "20"},
    {"level_number": 5, "width": "25", "height": "25"},
    {"level_number": 6, "width": "30", "height": "25"},
    {"level_number": 7, "width": "30", "height": "28"},
    {"level_number": 8, "width": "32", "height": "30"},
    {"level_number": 9, "width": "35", "height": "30"},
    {"level_number": 10, "width": "35", "height": "35"}
]


class Level(BaseModel):
    model_config = ConfigDict(extra="ignore")

    level_number: int
    width: int
    height: int


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
    points_per_pacgum: int = Field(default=10, ge=1, le=1000)
    points_per_super_pacgum: int = Field(default=50, ge=10, le=3000)
    points_per_ghost: int = Field(default=200, ge=15, le=5000)
    window_width: int = 800
    window_height: int = 600
    seed: str = "42"
    level_max_time: int = Field(default=90, ge=90, le=500)