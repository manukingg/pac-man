from pathlib import Path
from collections.abc import Callable
from typing import Iterable

from mlx import Mlx

from .events import GraphicsEvent
from .image import Image
from .animation import AnimationClip
from .mlx_image import MlxImage


Color = tuple[int, int, int]
FrameCallback = Callable[[float], bool]


class MlxWrapper:
    def __init__(
        self: "MlxWrapper",
        width: int,
        height: int,
        title: str,
    ) -> None:
        self._mlx = Mlx()
        self._mlx_ptr = self._mlx.mlx_init()

        if self._mlx_ptr is None:
            raise RuntimeError("mlx_init failed")

        self._width = width
        self._height = height
        self._title = title

        self._window = self._mlx.mlx_new_window(
            self._mlx_ptr,
            width,
            height,
            title,
        )

        self._event_queue: list[GraphicsEvent] = []

    def load_image(self: "MlxWrapper", path: str | Path) -> Image:
        raise NotImplementedError

    def load_animation(
        self: "MlxWrapper",
        paths: Iterable[str | Path],
        frame_duration: float,
        loop: bool = True,
    ) -> AnimationClip:
        frames = tuple(
            self.load_image(path)
            for path in paths
        )

        return AnimationClip(
            frames=frames,
            frame_duration=frame_duration,
            loop=loop,
        )

    def clear_window(self: "MlxWrapper", color: Color) -> None:
        self._mlx.mlx_clear_window(self._mlx_ptr, self._window)

    def poll_events(self: "MlxWrapper") -> list[GraphicsEvent]:
        events = self._event_queue
        self._event_queue = []
        return events

    def resize_window(
        self: "MlxWrapper",
        width: int,
        height: int,
    ) -> None:
        raise NotImplementedError

    @staticmethod
    def get_desktop_size() -> tuple[int, int]:
        mlx = Mlx()
        mlx_ptr = mlx.mlx_init()

        if mlx_ptr is None:
            return 800, 600

        result = mlx.mlx_get_screen_size(mlx_ptr)
        if (
            isinstance(result, tuple)
            and len(result) >= 3
            and isinstance(result[1], int)
            and isinstance(result[2], int)
        ):
            return result[1], result[2]

        return 800, 600

    def start_loop(
        self: "MlxWrapper",
        frame_callback: FrameCallback,
        fps: int = 60,
    ) -> None:
        raise NotImplementedError

    def quit(self: "MlxWrapper") -> None:
        return

    def _as_mlx_image(
        self: "MlxWrapper",
        image: Image,
    ) -> MlxImage:
        if not isinstance(image, MlxImage):
            raise TypeError("Expected MlxImage")

        return image

    def new_image(self: "MlxWrapper", width: int, height: int) -> Image:
        img_ptr = self._mlx.mlx_new_image(
            self._mlx_ptr,
            width,
            height,
        )
        if img_ptr is None:
            raise RuntimeError("mlx_new_image failed")

        data, bits_per_pixel, size_line, image_format = (
            self._mlx.mlx_get_data_addr(img_ptr)
        )

        return MlxImage(
            img_ptr=img_ptr,
            data=data,
            bits_per_pixel=bits_per_pixel,
            size_line=size_line,
            image_format=image_format,
            width=width,
            height=height,
        )

    def clear(self: "MlxWrapper", image: Image, color: Color) -> None:
        mlx_image = self._as_mlx_image(image)
        mlx_image.fill(color)

    def put_pixel(
        self: "MlxWrapper",
        image: Image,
        x: int,
        y: int,
        color: Color,
    ) -> None:
        mlx_image = self._as_mlx_image(image)
        mlx_image.set_at((x, y), color)

    def get_pixel(
        self: "MlxWrapper",
        image: Image,
        x: int,
        y: int,
    ) -> Color:
        mlx_image = self._as_mlx_image(image)
        return mlx_image.get_at(x, y)

    def put_image(
        self: "MlxWrapper",
        target: Image,
        source: Image,
        x: int,
        y: int,
        scale: tuple[int, int] | None = None,
    ) -> None:
        target_image = self._as_mlx_image(target)
        source_image = self._as_mlx_image(source)

        if scale is None:
            target_image.blit(source_image, (x, y))
            return

        width, height = scale

        if width <= 0 or height <= 0:
            raise ValueError("Scale size must be positive")

        if width == source.width and height == source.height:
            target_image.blit(source_image, (x, y))
            return

        self.__put_scaled_image(
            target=target_image,
            source=source_image,
            x=x,
            y=y,
            size=scale,
        )

    def put_image_to_window(
        self: "MlxWrapper",
        image: Image,
        x: int,
        y: int,
    ) -> None:
        mlx_image = self._as_mlx_image(image)

        self._mlx.mlx_put_image_to_window(
            self._mlx_ptr,
            self._window,
            mlx_image.img_ptr,
            x,
            y,
        )

    def present(self: "MlxWrapper") -> None:
        return

    def __put_scaled_image(
        self: "MlxWrapper",
        target: MlxImage,
        source: MlxImage,
        x: int,
        y: int,
        size: tuple[int, int],
    ) -> None:
        target_width, target_height = size

        for target_y in range(target_height):
            source_y = target_y * source.height // target_height

            for target_x in range(target_width):
                source_x = target_x * source.width // target_width

                color = source.get_at(source_x, source_y)

                target.set_at(
                    position=(x + target_x, y + target_y),
                    color=color,
                )
