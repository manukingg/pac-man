from pathlib import Path

import pygame

from src.graphics.events import EventType, GraphicsEvent, Key
from src.graphics.image import Image
from src.graphics.font_map import FONT_MAP
from .helpers import get_aligned_position
from typing import Optional


Color = tuple[int, int, int]


class PygameWrapper:
    def __init__(
        self: "PygameWrapper",
        width: int,
        height: int,
        title: str
    ) -> None:
        pygame.init()
        self._screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

    def new_image(self: "PygameWrapper", width: int, height: int) -> Image:
        return Image(pygame.Surface((width, height)))

    def load_image(self: "PygameWrapper", path: str | Path) -> Image:
        return Image(pygame.image.load(str(path)))

    def clear(self: "PygameWrapper", image: Image, color: Color) -> None:
        image.fill(color)

    def clear_window(self: "PygameWrapper", color: Color) -> None:
        self._screen.fill(color)

    def put_pixel(
        self: "PygameWrapper",
        image: Image,
        x: int,
        y: int,
        color: Color,
    ) -> None:
        if 0 <= x < image.width and 0 <= y < image.height:
            image.set_at((x, y), color)

    def get_pixel(
        self: "PygameWrapper",
        image: Image,
        x: int,
        y: int
    ) -> Color:
        return image.get_at(x, y)

    def put_image(
        self: "PygameWrapper",
        target: Image,
        source: Image,
        x: int,
        y: int,
    ) -> None:
        target._surface.blit(source._surface, (x, y))

    def put_image_to_window(
        self: "PygameWrapper",
        image: Image,
        x: int,
        y: int,
    ) -> None:
        self._screen.blit(image._surface, (x, y))

    def present(self: "PygameWrapper") -> None:
        pygame.display.flip()

    def poll_events(self: "PygameWrapper") -> list[GraphicsEvent]:
        events: list[GraphicsEvent] = []

        for event in pygame.event.get():
            converted = self._convert_event(event)
            if converted is not None:
                events.append(converted)

        return events

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

        if event.type == pygame.MOUSEBUTTONDOWN:
            return GraphicsEvent(
                type=EventType.MOUSE_DOWN,
                button=event.button,
                pos=event.pos
            )

        if event.type == pygame.MOUSEBUTTONUP:
            return GraphicsEvent(
                type=EventType.MOUSE_UP,
                button=event.button,
                pos=event.pos
            )

        if event.type == pygame.MOUSEMOTION:
            return GraphicsEvent(
                type=EventType.MOUSE_MOTION,
                pos=event.pos
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
