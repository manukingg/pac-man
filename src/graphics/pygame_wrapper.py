from pathlib import Path

import pygame

from src.graphics.events import EventType, GraphicsEvent, Key
from src.graphics.image import Image


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
            image._surface.set_at((x, y), color)

    def get_pixel(self: "PygameWrapper", image: Image, x: int, y: int) -> Color:
        return image.get_at(x, y)

    def put_image(
        self: "PygameWrapper",
        target: Image,
        source: Image,
        x: int,
        y: int,
    ) -> None:
        target.blit(source, (x, y))

    def put_image_to_window(self: "PygameWrapper", image: Image, x: int, y: int) -> None:
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
    ) -> None:
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        error = dx - dy
        x = x0
        y = y0

        while True:
            self.put_pixel(image, x, y, color)

            if x == x1 and y == y1:
                break

            double_error = 2 * error
            if double_error > -dy:
                error -= dy
                x += sx

            if double_error < dx:
                error += dx
                y += sy

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

    def quit(self: "PygameWrapper") -> None:
        pygame.quit()

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