from pydantic import BaseModel, Field


class GameRules(BaseModel):
    score_per_pacgum: int = Field(
        default=10,
        ge=1,
        le=1000,
    )
    score_per_super_pacgum: int = Field(
        default=50,
        ge=10,
        le=3000,
    )
    score_per_ghost: int = Field(
        default=200,
        ge=15,
        le=5000,
    )
