from dataclasses import dataclass

from ..graphics import Image
from ..models import Direction
from .ghost import GhostKind
from ..animation import AnimationClip


@dataclass(frozen=True, slots=True)
class GhostImages:
    chase: dict[Direction, Image]


@dataclass(frozen=True, slots=True)
class GhostAssets:
    ghosts: dict[GhostKind, GhostImages]

    frightened: Image
    frightened_warning: AnimationClip

    eaten: dict[Direction, Image]
