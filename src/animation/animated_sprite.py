from ..graphics import Image, AnimationClip, GraphicsBackend

from typing import Mapping


class AnimatedSprite:

    def __init__(
        self: "AnimatedSprite",
        animations: Mapping[str, AnimationClip],
        initial_animation: str,
        playing: bool = True
    ) -> None:
        if not animations:
            raise ValueError("Error: Sprite must have at least one animation")
        if initial_animation not in animations:
            raise KeyError(
                f"Error: animation {initial_animation} does not exist"
            )
        self.__animations = dict(animations)
        self.__current_animation = initial_animation
        self.__frame_index = 0
        self.__elapsed_time = 0.0
        self.__playing = playing

    @property
    def current_image(self: "AnimatedSprite") -> Image:
        """Return the currently displayed animation frame."""

        clip = self.__animations[self.__current_animation]
        return clip.frames[self.__frame_index]

    @property
    def current_animation(self: "AnimatedSprite") -> str:
        return self.__current_animation

    @property
    def is_playing(self: "AnimatedSprite") -> bool:
        return self.__playing

    @property
    def get_current_animation_images(self: "AnimatedSprite") -> tuple[Image]:
        return self.__animations.get(self.current_animation).frames

    def play(
        self: "AnimatedSprite",
        animation: str,
        restart: bool = False,
    ) -> None:
        """Start or continue an animation."""

        if animation not in self.__animations:
            raise KeyError(f"Animation '{animation}' does not exist")

        if animation == self.__current_animation and not restart:
            self.__playing = True
            return

        self.__current_animation = animation
        self.__frame_index = 0
        self.__elapsed_time = 0.0
        self.__playing = True

    def pause(self: "AnimatedSprite") -> None:
        self.__playing = False

    def reset(self: "AnimatedSprite") -> None:
        self.__frame_index = 0
        self.__elapsed_time = 0.0

    def update(
        self: "AnimatedSprite",
        delta_time: float,
    ) -> None:
        """Advance animation according to elapsed time."""

        if delta_time < 0:
            raise ValueError("Delta time cannot be negative")

        if not self.__playing:
            return

        clip = self.__animations[self.__current_animation]

        if len(clip.frames) == 1:
            return

        self.__elapsed_time += delta_time

        while self.__elapsed_time >= clip.frame_duration:
            self.__elapsed_time -= clip.frame_duration
            self.__frame_index += 1

            if self.__frame_index < len(clip.frames):
                continue

            if clip.loop:
                self.__frame_index = 0
            else:
                self.__frame_index = len(clip.frames) - 1
                self.__playing = False
                break

    def stop(
        self: "AnimatedSprite",
        frame_index: int = 0,
    ) -> None:
        clip = self.__animations[self.__current_animation]

        if not 0 <= frame_index < len(clip.frames):
            raise IndexError("Frame index is out of range")

        self.__frame_index = frame_index
        self.__elapsed_time = 0.0
        self.__playing = False

    def prepare_scale(
        self: "AnimatedSprite",
        display: GraphicsBackend,
        size: tuple[int, int],
    ) -> None:
        width, height = size

        for clip in self.__animations.values():
            for frame in clip.frames:
                display.prepare_scaled_image(
                    image=frame,
                    width=width,
                    height=height,
                )
