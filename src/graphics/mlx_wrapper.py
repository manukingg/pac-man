import time
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Optional

from mlx import Mlx

from .events import EventType, GraphicsEvent, Key
from .image import Image
from .animation import AnimationClip
from .helpers import get_aligned_position
from .mlx_image import MlxImage
from .font_map import FONT_MAP


Color = tuple[int, int, int]
Scale = int | float | tuple[int, int]
FrameCallback = Callable[[float], bool]
KEY_PRESS_EVENT = 2
KEY_PRESS_MASK = 1
WINDOW_CLOSE_EVENT = 33


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

        self._window = self._mlx.mlx_new_window(
            self._mlx_ptr,
            width,
            height,
            title,
        )

        if self._window is None:
            raise RuntimeError("mlx_new_window failed")

        self._width = width
        self._height = height
        self._title = title
        self._frame_callback: FrameCallback | None = None
        self._loop_error: BaseException | None = None
        self._previous_frame_time = 0.0
        self._target_frame_time = 0.0

        self._event_queue: list[GraphicsEvent] = []
        self._images: list[MlxImage] = []

        self._clear_image: MlxImage | None = None

        self._scaled_images: dict[
            tuple[int, int, int],
            MlxImage,
        ] = {}

        self._register_window_hooks()
        print("MLX INITIALIZED")

    def start_loop(
        self: "MlxWrapper",
        frame_callback: FrameCallback,
        fps: int = 60,
    ) -> None:
        if fps <= 0:
            raise ValueError(
                "FPS must be positive"
            )

        self._frame_callback = frame_callback
        self._target_frame_time = 1.0 / fps
        self._previous_frame_time = time.perf_counter()

        self._mlx.mlx_loop_hook(
            self._mlx_ptr,
            self._on_loop,
            None,
        )

        self._loop_error = None

        self._mlx.mlx_do_key_autorepeatoff(self._mlx_ptr)

        try:
            self._mlx.mlx_loop(self._mlx_ptr)
        finally:
            self._mlx.mlx_do_key_autorepeaton(self._mlx_ptr)
        if self._loop_error is not None:
            error = self._loop_error
            self._loop_error = None
            raise error

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

        if thickness == 1:
            self._draw_single_line(
                image=image,
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                color=color,
            )
            return

        radius = thickness // 2

        if y0 == y1:
            for offset in range(
                -radius,
                radius + 1,
            ):
                self._draw_single_line(
                    image=image,
                    x0=x0,
                    y0=y0 + offset,
                    x1=x1,
                    y1=y1 + offset,
                    color=color,
                )

        elif x0 == x1:
            for offset in range(
                -radius,
                radius + 1,
            ):
                self._draw_single_line(
                    image=image,
                    x0=x0 + offset,
                    y0=y0,
                    x1=x1 + offset,
                    y1=y1,
                    color=color,
                )

        else:
            for x, y in self._get_line_points(
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
            ):
                self.draw_filled_circle(
                    image=image,
                    center_x=x,
                    center_y=y,
                    radius=radius,
                    color=color,
                )

        if rounded:
            self.draw_filled_circle(
                image=image,
                center_x=x0,
                center_y=y0,
                radius=radius,
                color=color,
            )

            self.draw_filled_circle(
                image=image,
                center_x=x1,
                center_y=y1,
                radius=radius,
                color=color,
            )

    def new_image(
        self: "MlxWrapper",
        width: int,
        height: int,
    ) -> Image:
        img_ptr = self._mlx.mlx_new_image(
            self._mlx_ptr,
            width,
            height,
        )

        if img_ptr is None:
            raise RuntimeError("mlx_new_image failed")

        return self._create_mlx_image(
            img_ptr=img_ptr,
            width=width,
            height=height
        )

    def resize_window(
        self: "MlxWrapper",
        width: int,
        height: int,
    ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError(
                "Window size must be positive"
            )

        new_window = self._mlx.mlx_new_window(
            self._mlx_ptr,
            width=width,
            height=height,
            title=self._title,
        )

        if new_window is None:
            raise RuntimeError(
                "mlx_new_window failed"
            )
        old_window = self._window
        self._window = new_window
        self._width = width
        self._height = height

        self._register_window_hooks()

        self._mlx.mlx_destroy_window(
            mlx_ptr=self._mlx_ptr,
            win_ptr=old_window,
        )

        if self._clear_image is not None:
            self.destroy_image(
                self._clear_image
            )
            self._clear_image = None

    def prepare_scaled_image(
        self: "MlxWrapper",
        image: Image,
        width: int,
        height: int,
    ) -> None:
        source = self._as_mlx_image(image)

        self._get_scaled_image(
            source=source,
            width=width,
            height=height,
        )

    def load_image(
        self: "MlxWrapper",
        path: str | Path,
    ) -> Image:
        image_path = Path(path)

        if not image_path.is_file():
            raise FileNotFoundError(
                f"Image file not found: {image_path}"
            )

        suffix = image_path.suffix.lower()

        if suffix == ".xpm":
            img_ptr, width, height = (
                self._mlx.mlx_xpm_file_to_image(
                    self._mlx_ptr,
                    str(image_path),
                )
            )
        else:
            raise ValueError(
                f"Unsupported image format: {suffix}"
            )

        if img_ptr is None:
            raise RuntimeError(
                f"Could not load image: {image_path}"
            )

        return self._create_mlx_image(
            img_ptr=img_ptr,
            width=width,
            height=height,
        )

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

    def clear(
        self: "MlxWrapper",
        image: Image,
        color: Color,
    ) -> None:
        mlx_image = self._as_mlx_image(image)
        mlx_image.fill(color)

    def clear_window(
        self: "MlxWrapper",
        color: Color,
    ) -> None:
        if self._clear_image is None:
            image = self.new_image(
                self._width,
                self._height,
            )

            self._clear_image = (
                self._as_mlx_image(image)
            )

        self._clear_image.fill(color)

        self._mlx.mlx_put_image_to_window(
            self._mlx_ptr,
            self._window,
            self._clear_image.img_ptr,
            0,
            0,
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
            img_ptr=mlx_image.img_ptr,
            x=x,
            y=y,
        )

    def present(self: "MlxWrapper") -> None:
        return

    def put_image(
        self: "MlxWrapper",
        target: Image,
        source: Image,
        x: int,
        y: int,
        scale: Scale | None = None,
    ) -> None:
        target_image = self._as_mlx_image(target)
        source_image = self._as_mlx_image(source)

        target_size = self._resolve_scale(source_image, scale)

        if target_size is None:
            target_image.blit(source_image, (x, y))
            return

        width, height = target_size

        if width == source_image.width and height == source_image.height:
            target_image.blit(source_image, (x, y))
            return

        scaled_image = self._get_scaled_image(
            source=source_image,
            width=width,
            height=height,
        )

        target_image.blit(scaled_image, (x, y))

    def poll_events(self: "MlxWrapper") -> list[GraphicsEvent]:
        return self._drain_event_queue()

    @staticmethod
    def get_desktop_size() -> tuple[int, int]:
        mlx = Mlx()
        mlx_ptr = mlx.mlx_init()

        if mlx_ptr is None:
            return 800, 600

        try:
            result = mlx.mlx_get_screen_size(
                mlx_ptr
            )

            if result is None:
                return 800, 600

            _, width, height = result

            if width <= 0 or height <= 0:
                return 800, 600

            return width, height

        finally:
            mlx.mlx_release(
                mlx_ptr
            )

    def get_window_size(self: "MlxWrapper") -> tuple[int, int]:
        return self._width, self._height

    def load_animation(
        self: "MlxWrapper",
        paths: Iterable[str | Path],
        frame_duration: float,
        loop: bool = True,
    ) -> AnimationClip:
        """Load animation frames from image files."""

        frames = tuple(
            self.load_image(path)
            for path in paths
        )

        return AnimationClip(
            frames=frames,
            frame_duration=frame_duration,
            loop=loop,
        )

    def destroy_image(
        self: "MlxWrapper",
        image: Image,
    ) -> None:
        mlx_image = self._as_mlx_image(image)

        if mlx_image not in self._images:
            return

        dependent_keys = [
            key for key in self._scaled_images if key[0] == id(mlx_image)
        ]

        for key in dependent_keys:
            sclaed_image = self._scaled_images.pop(key)

            if sclaed_image in self._images:
                self.destroy_image(sclaed_image)

        cached_keys = [key for key, cached_image in self._scaled_images.items()
                       if cached_image is mlx_image]

        for key in cached_keys:
            self._scaled_images.pop(key)

        self._mlx.mlx_destroy_image(
            self._mlx_ptr,
            mlx_image.img_ptr,
        )

        self._images.remove(mlx_image)

    def quit(self: "MlxWrapper") -> None:
        for image in self._images.copy():
            self.destroy_image(image)

        self._mlx.mlx_destroy_window(
            self._mlx_ptr,
            self._window,
        )

        self._mlx.mlx_release(self._mlx_ptr)

    def _as_mlx_image(
        self: "MlxWrapper",
        image: Image,
    ) -> MlxImage:
        if not isinstance(image, MlxImage):
            raise TypeError("Expected MlxImage")

        return image

    def _create_mlx_image(
        self: "MlxWrapper",
        img_ptr: object,
        width: int,
        height: int,
    ) -> MlxImage:
        data, bits_per_pixel, size_line, image_format = (
            self._mlx.mlx_get_data_addr(img_ptr)
        )

        image = MlxImage(
            img_ptr=img_ptr,
            data=data,
            bits_per_pixel=bits_per_pixel,
            size_line=size_line,
            image_format=image_format,
            width=width,
            height=height,
        )

        self._images.append(image)

        return image

    def _on_loop(self, _data: object) -> int:
        if self._frame_callback is None:
            return 0

        current_time = time.perf_counter()

        elapsed = current_time - self._previous_frame_time

        if elapsed < self._target_frame_time:
            time.sleep(self._target_frame_time - elapsed)

            current_time = time.perf_counter()

        delta_time = current_time - self._previous_frame_time

        self._previous_frame_time = current_time

        try:
            should_continue = self._frame_callback(delta_time)

            if not should_continue:
                self._mlx.mlx_loop_exit(self._mlx_ptr)

        except BaseException as error:
            self._loop_error = error
            self._mlx.mlx_loop_exit(self._mlx_ptr)

        return 0

    def _resolve_scale(
        self: "MlxWrapper",
        source: MlxImage,
        scale: Scale | None,
    ) -> tuple[int, int] | None:
        if scale is None:
            return None

        if isinstance(scale, tuple):
            width, height = scale
        else:
            width = round(source.width * scale)
            height = round(source.height * scale)

        if width <= 0 or height <= 0:
            raise ValueError("Scale size must be positive")

        return width, height

    def draw_rect(
        self: "MlxWrapper",
        image: Image,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Color,
    ) -> None:
        for current_y in range(y, y + height):
            for current_x in range(x, x + width):
                self.put_pixel(image, current_x, current_y, color)

    def draw_filled_circle(
        self: "MlxWrapper",
        image: Image,
        center_x: int,
        center_y: int,
        radius: int,
        color: Color,
    ) -> None:
        """Draw a filled circle."""

        radius_squared = radius * radius

        for offset_y in range(-radius, radius + 1):
            remaining = radius_squared - offset_y * offset_y
            half_width = int(remaining ** 0.5)

            self._draw_single_line(
                image=image,
                x0=center_x - half_width,
                y0=center_y + offset_y,
                x1=center_x + half_width,
                y1=center_y + offset_y,
                color=color,
            )

    def write_text(
        self: "MlxWrapper",
        text: str,
        image: Image,
        font_size: int,
        color: Color,
        position: Optional[tuple[int, int]] = None,
        align: Optional[tuple[str | int]] = None,
    ) -> None:
        if align is None and position is None:
            top_left_x, top_left_y = (0, 0)
        elif align is not None and position is not None:
            position = None
        elif align is not None:
            try:
                top_left_x, top_left_y = get_aligned_position(
                    align=align,
                    text=text,
                    font_size=font_size,
                    image=image,
                )
            except Exception as e:
                print(e)
                return
        else:
            top_left_x, top_left_y = position

        pixel_space = font_size

        for letter in text:

            if letter not in FONT_MAP:
                letter = "?"

            if top_left_x + 5 * font_size > image.width:
                top_left_x = pixel_space
                top_left_y += 8 * font_size + pixel_space

            if top_left_y + 8 * font_size > image.height:
                break

            letter_sized = self._get_font_letter_bitmap(letter, font_size)
            for row in range(len(letter_sized)):
                for column in range(len(letter_sized[row])):
                    if letter_sized[row][column] == "1":
                        self.put_pixel(
                            image,
                            top_left_x + column,
                            top_left_y + row,
                            color,
                        )
            top_left_x += 5 * font_size + pixel_space

    def _push_event(
        self: "MlxWrapper",
        event: GraphicsEvent,
    ) -> None:
        self._event_queue.append(event)

    def _drain_event_queue(self: "MlxWrapper") -> list[GraphicsEvent]:
        events = self._event_queue
        self._event_queue = []
        return events

    def _convert_key(self: "MlxWrapper", keycode: int) -> Key:
        key_map = {
            65307: Key.ESCAPE,
            65293: Key.ENTER,
            32: Key.SPACE,

            65362: Key.UP,
            65364: Key.DOWN,
            65361: Key.LEFT,
            65363: Key.RIGHT,

            119: Key.W,
            97: Key.A,
            115: Key.S,
            100: Key.D,
        }

        return key_map.get(keycode, Key.UNKNOWN)

    def _push_key_event(
        self: "MlxWrapper",
        keycode: int,
        event_type: EventType,
    ) -> None:
        self._push_event(
            GraphicsEvent(
                type=event_type,
                key=self._convert_key(keycode),
            )
        )

    def _on_key_down(
        self: "MlxWrapper",
        keycode: int,
        _data: object,
    ) -> int:
        self._push_key_event(keycode, EventType.KEY_DOWN)
        return 0

    def _on_key_up(
        self: "MlxWrapper",
        keycode: int,
        _data: object,
    ) -> int:
        self._push_key_event(keycode, EventType.KEY_UP)
        return 0

    def _on_window_close(
        self: "MlxWrapper",
        _data: object,
    ) -> int:
        event = GraphicsEvent(
            type=EventType.QUIT,
        )

        self._push_event(event)

        return 0

    def _draw_single_line(
        self: "MlxWrapper",
        image: Image,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        color: Color,
    ) -> None:
        """Draw a one-pixel Bresenham line."""

        for x, y in self._get_line_points(
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
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
        """Yield every pixel belonging to a line."""

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

    def _get_font_letter_bitmap(
        self: "MlxWrapper",
        letter: str,
        font: int,
    ) -> tuple[str, ...]:
        letter_bitmap = FONT_MAP.get(letter)

        if letter_bitmap is None:
            letter_bitmap = FONT_MAP["?"]

        result: list[str] = []

        for row in range(
            len(letter_bitmap)
        ):
            extended_column = ""

            for column in range(
                len(letter_bitmap[row])
            ):
                for _ in range(font):
                    extended_column += (
                        letter_bitmap[row][column]
                    )

            for _ in range(font):
                result.append(
                    extended_column
                )

        return tuple(result)

    def _register_window_hooks(self: "MlxWrapper") -> None:
        self._mlx.mlx_hook(
            self._window,
            KEY_PRESS_EVENT,
            KEY_PRESS_MASK,
            self._on_key_down,
            None,
        )

        self._mlx.mlx_key_hook(
            self._window,
            self._on_key_up,
            None,
        )

        self._mlx.mlx_hook(
            self._window,
            WINDOW_CLOSE_EVENT,
            0,
            self._on_window_close,
            None,
        )

    def _get_scaled_image(
        self: "MlxWrapper",
        source: MlxImage,
        width: int,
        height: int,
    ) -> MlxImage:
        cache_key = (id(source), width, height,)

        cached = self._scaled_images.get(cache_key)

        if cached is not None:
            return cached

        scaled = self._as_mlx_image(self.new_image(width, height))

        scaled.fill(color=(0, 0, 0), alpha=0,)

        for scaled_y in range(height):
            source_y = scaled_y * source.height // height

            for scaled_x in range(width):
                source_x = scaled_x * source.width // width

                red, green, blue, alpha = source.get_rgba(source_x, source_y)

                if alpha == 0:
                    continue

                scaled.set_at(
                    position=(scaled_x, scaled_y),
                    color=(red, green, blue),
                    alpha=255,
                )
        self._scaled_images[cache_key] = scaled

        return scaled
