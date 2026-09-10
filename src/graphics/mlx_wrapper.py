import time

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Optional

from mlx import Mlx

from .animation import AnimationClip
from .events import EventType, GraphicsEvent, Key
from .font_map import FONT_MAP
from .helpers import get_aligned_position
from .image import Image
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
            raise RuntimeError("Could not initialize MLX")

        self._title = title
        self._width = width
        self._height = height

        self._window = self._mlx.mlx_new_window(
            self._mlx_ptr,
            width,
            height,
            title,
        )

        if self._window is None:
            raise RuntimeError("Could not create MLX window")

        self._event_queue: list[GraphicsEvent] = []

        self._frame_callback: FrameCallback | None = None
        self._target_frame_time = 1.0 / 60.0
        self._previous_time = time.perf_counter()

        self._register_hooks()

    def _register_hooks(self: "MlxWrapper") -> None:
        # KeyPress
        self._mlx.mlx_hook(
            self._window,
            2,
            1,
            self._on_key_down,
            None,
        )

        # KeyRelease
        self._mlx.mlx_hook(
            self._window,
            3,
            2,
            self._on_key_up,
            None,
        )

        # Window close
        self._mlx.mlx_hook(
            self._window,
            33,
            0,
            self._on_close,
            None,
        )

    def new_image(
        self: "MlxWrapper",
        width: int,
        height: int,
    ) -> Image:
        ptr = self._mlx.mlx_new_image(
            self._mlx_ptr,
            width,
            height,
        )

        if ptr is None:
            raise RuntimeError("Could not create MLX image")

        return self._wrap_image(
            ptr=ptr,
            width=width,
            height=height,
        )

    def _wrap_image(
        self: "MlxWrapper",
        ptr,
        width: int,
        height: int,
    ) -> MlxImage:
        data, bits_per_pixel, size_line, image_format = (
            self._mlx.mlx_get_data_addr(ptr)
        )

        return MlxImage(
            ptr=ptr,
            data=data,
            width=width,
            height=height,
            bits_per_pixel=bits_per_pixel,
            size_line=size_line,
            image_format=image_format,
        )

    def load_image(
        self: "MlxWrapper",
        path: str | Path,
    ) -> Image:
        path = Path(path)

        if path.suffix.lower() == ".xpm":
            ptr, width, height = self._mlx.mlx_xpm_file_to_image(
                self._mlx_ptr,
                str(path),
            )
        elif path.suffix.lower() == ".png":
            ptr, width, height = self._mlx.mlx_png_file_to_image(
                self._mlx_ptr,
                str(path),
            )
        else:
            raise ValueError(
                f"Unsupported image format: {path.suffix}"
            )

        if ptr is None:
            raise RuntimeError(f"Could not load image: {path}")

        return self._wrap_image(
            ptr=ptr,
            width=width,
            height=height,
        )

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

    def clear(
        self: "MlxWrapper",
        image: Image,
        color: Color,
    ) -> None:
        mlx_image = self._as_mlx_image(image)

        red, green, blue = color

        mlx_image.fill(
            (
                red,
                green,
                blue,
                255,
            )
        )

    def clear_window(
        self: "MlxWrapper",
        color: Color,
    ) -> None:
        if color == (0, 0, 0):
            self._mlx.mlx_clear_window(
                self._mlx_ptr,
                self._window,
            )
            return

        image = self.new_image(
            self._width,
            self._height,
        )

        self.clear(image, color)
        self.put_image_to_window(image, 0, 0)

    def put_pixel(
        self: "MlxWrapper",
        image: Image,
        x: int,
        y: int,
        color: Color,
    ) -> None:
        if not (
            0 <= x < image.width
            and 0 <= y < image.height
        ):
            return

        mlx_image = self._as_mlx_image(image)

        red, green, blue = color

        mlx_image.set_rgba(
            x,
            y,
            (red, green, blue, 255),
        )

    def get_pixel(
        self: "MlxWrapper",
        image: Image,
        x: int,
        y: int,
    ) -> Color:
        mlx_image = self._as_mlx_image(image)

        red, green, blue, _ = mlx_image.get_rgba(x, y)

        return red, green, blue

    def put_image(
        self: "MlxWrapper",
        target: Image,
        source: Image,
        x: int,
        y: int,
        scale: tuple[int, int] | None = None,
    ) -> None:
        target_image = self._as_mlx_image(
            target
        )

        source_image = self._as_mlx_image(
            source
        )

        if scale is None:
            source_image.blit_to(
                target=target_image,
                x=x,
                y=y,
            )

            return

        width, height = scale

        if width <= 0 or height <= 0:
            raise ValueError(
                "Scale size must be positive"
            )

        if (
            width == source_image.width
            and height == source_image.height
        ):
            source_image.blit_to(
                target=target_image,
                x=x,
                y=y,
            )

            return

        self._put_scaled_image(
            target=target_image,
            source=source_image,
            x=x,
            y=y,
            width=width,
            height=height,
        )

    def _put_scaled_image(
        self: "MlxWrapper",
        target: MlxImage,
        source: MlxImage,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        for target_y in range(height):
            destination_y = y + target_y

            if not (
                0 <= destination_y
                < target.height
            ):
                continue

            source_y = (
                target_y
                * source.height
                // height
            )

            for target_x in range(width):
                destination_x = (
                    x + target_x
                )

                if not (
                    0 <= destination_x
                    < target.width
                ):
                    continue

                source_x = (
                    target_x
                    * source.width
                    // width
                )

                color = source.get_rgba(
                    source_x,
                    source_y,
                )

                self._blend_pixel(
                    target=target,
                    x=destination_x,
                    y=destination_y,
                    source_color=color,
                )

    def _blend_pixel(
        self: "MlxWrapper",
        target: MlxImage,
        x: int,
        y: int,
        source_color: tuple[int, int, int, int],
    ) -> None:
        source_red, source_green, source_blue, source_alpha = (
            source_color
        )

        if source_alpha == 0:
            return

        if source_alpha == 255:
            target.set_rgba(
                x,
                y,
                source_color,
            )
            return

        target_red, target_green, target_blue, target_alpha = (
            target.get_rgba(x, y)
        )

        alpha = source_alpha / 255.0
        inverse_alpha = 1.0 - alpha

        red = int(
            source_red * alpha
            + target_red * inverse_alpha
        )

        green = int(
            source_green * alpha
            + target_green * inverse_alpha
        )

        blue = int(
            source_blue * alpha
            + target_blue * inverse_alpha
        )

        result_alpha = int(
            source_alpha
            + target_alpha * inverse_alpha
        )

        target.set_rgba(
            x,
            y,
            (
                red,
                green,
                blue,
                result_alpha,
            ),
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
            mlx_image.ptr,
            x,
            y,
        )

    def present(self: "MlxWrapper") -> None:
        pass

    def poll_events(
        self: "MlxWrapper",
    ) -> list[GraphicsEvent]:
        return self._drain_event_queue()

    def start_loop(
        self: "MlxWrapper",
        frame_callback: FrameCallback,
        fps: int = 60,
    ) -> None:
        self._frame_callback = frame_callback
        self._target_frame_time = 1.0 / fps
        self._previous_time = time.perf_counter()

        self._mlx.mlx_loop_hook(
            self._mlx_ptr,
            self._loop,
            None,
        )

        self._mlx.mlx_loop(self._mlx_ptr)

    def _loop(
        self: "MlxWrapper",
        _param,
    ) -> int:
        now = time.perf_counter()

        delta_time = (
            now
            - self._previous_time
        )

        if delta_time < self._target_frame_time:
            return 0

        self._previous_time = now

        if self._frame_callback is None:
            return 0

        running = self._frame_callback(
            delta_time
        )

        if not running:
            self._mlx.mlx_loop_exit(
                self._mlx_ptr
            )

        return 0

    @staticmethod
    def get_desktop_size() -> tuple[int, int]:
        mlx = Mlx()
        mlx_ptr = mlx.mlx_init()

        if mlx_ptr is None:
            return 800, 600

        try:
            result, width, height = mlx.mlx_get_screen_size(
                mlx_ptr
            )

            if result != 0:
                return 800, 600

            return width, height

        finally:
            mlx.mlx_release(mlx_ptr)

    def get_window_size(
        self: "MlxWrapper",
    ) -> tuple[int, int]:
        return self._width, self._height

    def resize_window(
        self: "MlxWrapper",
        width: int,
        height: int,
    ) -> None:
        if (
            width == self._width
            and height == self._height
        ):
            return

        self._mlx.mlx_destroy_window(
            self._mlx_ptr,
            self._window,
        )

        self._width = width
        self._height = height

        self._window = self._mlx.mlx_new_window(
            self._mlx_ptr,
            width,
            height,
            self._title,
        )

        if self._window is None:
            raise RuntimeError(
                "Could not recreate MLX window"
            )

        self._register_hooks()

    def draw_rect(
        self: "MlxWrapper",
        image: Image,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Color,
    ) -> None:
        mlx_image = self._as_mlx_image(image)

        red, green, blue = color

        mlx_image.fill_rect(
            x=x,
            y=y,
            width=width,
            height=height,
            color=(
                red,
                green,
                blue,
                255,
            ),
        )

    def draw_line(
        self: "MlxWrapper",
        image: Image,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        color: Color,
        thickness: int = 1,
        rounded: bool = False,
    ) -> None:
        if thickness <= 0:
            raise ValueError(
                "Line thickness must be positive"
            )

        if thickness % 2 == 0:
            raise ValueError(
                "Line thickness must be an odd number"
            )

        radius = thickness // 2

        # Fast horizontal line
        if y0 == y1:
            left = min(x0, x1)
            width = abs(x1 - x0) + 1

            self.draw_rect(
                image=image,
                x=left,
                y=y0 - radius,
                width=width,
                height=thickness,
                color=color,
            )

        # Fast vertical line
        elif x0 == x1:
            top = min(y0, y1)
            height = abs(y1 - y0) + 1

            self.draw_rect(
                image=image,
                x=x0 - radius,
                y=top,
                width=thickness,
                height=height,
                color=color,
            )

        else:
            if thickness == 1:
                self._draw_single_line(
                    image=image,
                    x0=x0,
                    y0=y0,
                    x1=x1,
                    y1=y1,
                    color=color,
                )

            else:
                for x, y in self._get_line_points(
                    x0,
                    y0,
                    x1,
                    y1,
                ):
                    self._draw_filled_circle(
                        image=image,
                        center_x=x,
                        center_y=y,
                        radius=radius,
                        color=color,
                    )

        if rounded and radius > 0:
            self._draw_filled_circle(
                image=image,
                center_x=x0,
                center_y=y0,
                radius=radius,
                color=color,
            )

            self._draw_filled_circle(
                image=image,
                center_x=x1,
                center_y=y1,
                radius=radius,
                color=color,
            )

    def _draw_single_line(
        self: "MlxWrapper",
        image: Image,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        color: Color,
    ) -> None:
        for x, y in self._get_line_points(
            x0,
            y0,
            x1,
            y1,
        ):
            self.put_pixel(
                image=image,
                x=x,
                y=y,
                color=color,
            )

    def _get_line_points(
        self: "MlxWrapper",
        x0: int,
        y0: int,
        x1: int,
        y1: int,
    ):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        step_x = 1 if x0 < x1 else -1
        step_y = 1 if y0 < y1 else -1

        error = dx - dy

        x = x0
        y = y0

        while True:
            yield x, y

            if x == x1 and y == y1:
                break

            double_error = error * 2

            if double_error > -dy:
                error -= dy
                x += step_x

            if double_error < dx:
                error += dx
                y += step_y

    def _draw_filled_circle(
        self: "MlxWrapper",
        image: Image,
        center_x: int,
        center_y: int,
        radius: int,
        color: Color,
    ) -> None:
        radius_squared = radius * radius

        for offset_y in range(
            -radius,
            radius + 1,
        ):
            remaining = (
                radius_squared
                - offset_y * offset_y
            )

            half_width = int(
                remaining ** 0.5
            )

            self.draw_rect(
                image=image,
                x=center_x - half_width,
                y=center_y + offset_y,
                width=half_width * 2 + 1,
                height=1,
                color=color,
            )

    def write_text(
        self: "MlxWrapper",
        text: str,
        image: Image,
        font_size: int,
        color: Color,
        position: Optional[
            tuple[int, int]
        ] = None,
        align: Optional[
            tuple[str | int, ...]
        ] = None,
    ) -> None:
        if align is None and position is None:
            top_left_x, top_left_y = 0, 0

        elif align is not None and position is not None:
            return

        elif align is not None:
            top_left_x, top_left_y = (
                get_aligned_position(
                    align=align,
                    text=text,
                    font_size=font_size,
                    image=image,
                )
            )

        else:
            top_left_x, top_left_y = position

        pixel_space = font_size

        for letter in text:
            if letter not in FONT_MAP:
                letter = "?"

            if (
                top_left_x + 5 * font_size
                > image.width
            ):
                top_left_x = pixel_space
                top_left_y += (
                    8 * font_size
                    + pixel_space
                )

            if (
                top_left_y + 8 * font_size
                > image.height
            ):
                break

            bitmap = self._get_font_letter_bitmap(
                letter,
                font_size,
            )

            for row in range(len(bitmap)):
                for column in range(len(bitmap[row])):
                    if bitmap[row][column] == "1":
                        self.put_pixel(
                            image,
                            top_left_x + column,
                            top_left_y + row,
                            color,
                        )

            top_left_x += (
                5 * font_size
                + pixel_space
            )

    def _get_font_letter_bitmap(
        self: "MlxWrapper",
        letter: str,
        font: int,
    ) -> tuple[str, ...]:
        letter_bitmap = FONT_MAP.get(letter)

        result: list[str] = []

        for row in range(len(letter_bitmap)):
            extended_column = ""

            for column in range(
                len(letter_bitmap[row])
            ):
                extended_column += (
                    letter_bitmap[row][column]
                    * font
                )

            for _ in range(font):
                result.append(
                    extended_column
                )

        return tuple(result)

    def _on_key_down(
        self: "MlxWrapper",
        keycode: int,
        _param,
    ) -> int:
        self._push_event(
            GraphicsEvent(
                type=EventType.KEY_DOWN,
                key=self._convert_key(keycode),
            )
        )

        return 0

    def _on_key_up(
        self: "MlxWrapper",
        keycode: int,
        _param,
    ) -> int:
        self._push_event(
            GraphicsEvent(
                type=EventType.KEY_UP,
                key=self._convert_key(keycode),
            )
        )

        return 0

    def _on_close(
        self: "MlxWrapper",
        _param,
    ) -> int:
        self._push_event(
            GraphicsEvent(
                type=EventType.QUIT,
            )
        )

        return 0

    def _convert_key(
        self: "MlxWrapper",
        keycode: int,
    ) -> Key:
        key_map = {
            65362: Key.UP,
            65364: Key.DOWN,
            65361: Key.LEFT,
            65363: Key.RIGHT,

            ord("w"): Key.W,
            ord("a"): Key.A,
            ord("s"): Key.S,
            ord("d"): Key.D,

            65293: Key.ENTER,
            32: Key.SPACE,
            65307: Key.ESCAPE,
        }

        return key_map.get(
            keycode,
            Key.UNKNOWN,
        )

    def _as_mlx_image(
        self: "MlxWrapper",
        image: Image,
    ) -> MlxImage:
        if not isinstance(image, MlxImage):
            raise TypeError(
                "Expected MlxImage"
            )

        return image

    def _push_event(
        self: "MlxWrapper",
        event: GraphicsEvent,
    ) -> None:
        self._event_queue.append(event)

    def _drain_event_queue(
        self: "MlxWrapper",
    ) -> list[GraphicsEvent]:
        events = self._event_queue
        self._event_queue = []

        return events

    def quit(self: "MlxWrapper") -> None:
        if self._window is not None:
            self._mlx.mlx_destroy_window(
                self._mlx_ptr,
                self._window,
            )

            self._window = None

        if self._mlx_ptr is not None:
            self._mlx.mlx_release(
                self._mlx_ptr
            )

            self._mlx_ptr = None
