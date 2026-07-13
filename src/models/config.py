from pydantic import BaseModel, Field
    
level = [
    {
        "level_number": 1,
        "width": "15",
        "height": "15"
    },
    {
        "level_number": 2,
        "width": "20",
        "height": "18"
    },
    {
        "level_number": 3,
        "width": "20",
        "height": "20"
    },

    {
        "level_number": 4,
        "width": "25",
        "height": "20"
    },

    {
        "level_number": 5,
        "width": "25",
        "height": "25"
    },

    {
        "level_number": 6,
        "width": "30",
        "height": "25"
    },
    {
        "level_number": 7,
        "width": "30",
        "height": "28"
    },
    {
        "level_number": 8,
        "width": "32",
        "height": "30"
    },
    {
        "level_number": 9,
        "width": "35",
        "height": "30"
    },
    {
        "level_number": 10,
        "width": "35",
        "height": "35"
    }
]


class Level(BaseModel):
    level_number: int
    width: int
    height: int


class Config(BaseModel):
    highscore_filename: str = Field(default="highscores.json")
    levels: list[Level] = level
    lives: int = 3
    pacgum: int = 42
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    window_width: int = 800
    window_height: int = 600
    seed: str = "42"
    level_max_time: int = 90