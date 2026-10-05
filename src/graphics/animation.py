from .image import Image

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnimationClip:
    frames: tuple[Image, ...]
    frame_duration: float
    loop: bool = True

    def __post_init__(self: 'AnimationClip') -> None:
        if not self.frames:
            raise ValueError("Error: Animation must "
                             "contain at least one frame")
        if self.frame_duration <= 0:
            raise ValueError("Error: Frame duration must be > 0")
