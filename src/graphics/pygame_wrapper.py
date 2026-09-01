from pathlib import Path

import pygame

from .events import EventType, GraphicsEvent, Key
from .image import Image
from .pygame_image import PygameImage
from .font_map import FONT_MAP
from .helpers import get_aligned_position
from .animation import AnimationClip
from typing import Optional, Iterable


Color = tuple[int, int, int]


class PygameWrapper:
    def __init__(
        self: "PygameWrapper",
        width: int,
        height: int,
        title: str
    ) -> None:
        pygame.init()

        self._title = title
        self._screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

        self._event_queue: list[GraphicsEvent] = []

    def new_image(self: "PygameWrapper", width: int, height: int) -> Image:
        return PygameImage(pygame.Surface((width, height)))

    def load_image(self: "PygameWrapper", path: str | Path) -> Image:
        surface = pygame.image.load(str(path)).convert_alpha()
        return PygameImage(surface)

    def clear(self: "PygameWrapper", image: Image, color: Color) -> None:
        pygame_image = self._as_pygame_image(image)
        pygame_image.fill(color)

    def clear_window(self: "PygameWrapper", color: Color) -> None:
        self._screen.fill(color)

    def load_animation(
        self: "PygameWrapper",
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

    def resize_window(
        self: "PygameWrapper",
        width: int,
        height: int,
    ) -> None:
        self._screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(self._title)

    def put_pixel(
        self: "PygameWrapper",
        image: Image,
        x: int,
        y: int,
        color: Color,
    ) -> None:
        if 0 <= x < image.width and 0 <= y < image.height:
            pygame_image = self._as_pygame_image(image)
            pygame_image.set_at((x, y), color)

    def get_pixel(
        self: "PygameWrapper",
        image: Image,
        x: int,
        y: int
    ) -> Color:
        pygame_image = self._as_pygame_image(image)
        return pygame_image.get_at(x, y)

    def put_image(
        self: "PygameWrapper",
        target: Image,
        source: Image,
        x: int,
        y: int,
        scale: tuple[int, int] | None = None,
    ) -> None:
        target_image = self._as_pygame_image(target)
        source_image = self._as_pygame_image(source)

        if scale is None:
            target_image.blit(source, (x, y))
            return

        width, height = scale

        if width <= 0 or height <= 0:
            raise ValueError("Scale size must be positive")

        if width == source.width and height == source.height:
            target_image.blit(source, (x, y))
            return

        self.__put_scaled_image(
            target=target_image,
            source=source_image,
            x=x,
            y=y,
            size=scale
        )

    def put_image_to_window(
        self: "PygameWrapper",
        image: Image,
        x: int,
        y: int,
    ) -> None:
        pygame_image = self._as_pygame_image(image)
        self._screen.blit(pygame_image._surface, (x, y))

    def present(self: "PygameWrapper") -> None:
        pygame.display.flip()

    def poll_events(self: "PygameWrapper") -> list[GraphicsEvent]:
        for pygame_event in pygame.event.get():
            converted_event = self._convert_event(pygame_event)

            if converted_event is not None:
                self._push_event(converted_event)

        return self._drain_event_queue()

    @staticmethod
    def get_desktop_size() -> tuple[int, int]:
        pygame.init()

        desktop_sizes = pygame.display.get_desktop_sizes()

        if not desktop_sizes:
            return 800, 600

        return desktop_sizes[0]

    def get_window_size(self: "PygameWrapper") -> tuple[int, int]:
        return self._screen.get_size()

    def draw_line(
        self: "PygameWrapper",
        image: Image,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        color: Color,
        thickness: int = 1,
        rounded: bool = False,
    ) -> None:
        """Draw a line with optional thickness and rounded ends."""

        if thickness <= 0:
            raise ValueError("Line thickness must be positive")

        if thickness % 2 == 0:
            raise ValueError("Line thickness must be an odd number")

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
            for offset in range(-radius, radius + 1):
                self._draw_single_line(
                    image=image,
                    x0=x0,
                    y0=y0 + offset,
                    x1=x1,
                    y1=y1 + offset,
                    color=color,
                )

        elif x0 == x1:
            for offset in range(-radius, radius + 1):
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
                self._draw_filled_circle(
                    image=image,
                    center_x=x,
                    center_y=y,
                    radius=radius,
                    color=color,
                )

        if rounded:
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
        self: "PygameWrapper",
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
        self: "PygameWrapper",
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

    def _draw_filled_circle(
        self: "PygameWrapper",
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

    def __put_scaled_image(
        self: "PygameWrapper",
        target: PygameImage,
        source: PygameImage,
        x: int,
        y: int,
        size: tuple[int, int]
    ) -> None:
        """Draw an image using nearest-neighbour scaling."""

        for target_y in range(size[1]):
            source_y = target_y * source.height // size[1]

            for target_x in range(size[0]):
                source_x = target_x * source.width // size[0]

                color = source.get_at(source_x, source_y)

                self.put_pixel(
                    image=target,
                    x=x + target_x,
                    y=y + target_y,
                    color=color,
                )

    def draw_rect(
        self: "PygameWrapper",
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

    def write_text(
        self: "PygameWrapper",
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

    def quit(self: "PygameWrapper") -> None:
        pygame.quit()

    def _get_font_letter_bitmap(
        self: "PygameWrapper",
        letter: str,
        font: int,
    ) -> tuple[str]:
        letter_bitmap = FONT_MAP.get(letter)
        result = []
        for row in range(len(letter_bitmap)):
            extended_column = ""
            for column in range(len(letter_bitmap[row])):
                for _ in range(font):
                    extended_column += letter_bitmap[row][column]
            for _ in range(font):
                result.append(extended_column)
        return tuple(result)

    def _convert_event(
        self: "PygameWrapper",
        event: pygame.event.Event
    ) -> GraphicsEvent | None:
        if event.type == pygame.QUIT:
            return GraphicsEvent(EventType.QUIT)

        if event.type == pygame.KEYUP:
            return GraphicsEvent(
                type=EventType.KEY_UP,
                key=self._convert_key(event.key)
            )

        if event.type == pygame.KEYDOWN:
            return GraphicsEvent(
                type=EventType.KEY_DOWN,
                key=self._convert_key(event.key),
            )

        return None

    def _convert_key(self: "PygameWrapper", key: int) -> Key:
        key_map = {
            pygame.K_UP: Key.UP,
            pygame.K_DOWN: Key.DOWN,
            pygame.K_LEFT: Key.LEFT,
            pygame.K_RIGHT: Key.RIGHT,
            pygame.K_w: Key.W,
            pygame.K_a: Key.A,
            pygame.K_s: Key.S,
            pygame.K_d: Key.D,
            pygame.K_RETURN: Key.ENTER,
            pygame.K_SPACE: Key.SPACE,
            pygame.K_ESCAPE: Key.ESCAPE,
        }

        return key_map.get(key, Key.UNKNOWN)

    def _as_pygame_image(
        self: "PygameWrapper",
        image: Image,
    ) -> PygameImage:
        if not isinstance(image, PygameImage):
            raise TypeError("Expected PygameImage")

        return image

    def _push_event(
        self: "PygameWrapper",
        event: GraphicsEvent,
    ) -> None:
        self._event_queue.append(event)

    def _drain_event_queue(self: "PygameWrapper") -> list[GraphicsEvent]:
        events = self._event_queue
        self._event_queue = []

        return events