from pathlib import Path

import pygame

from src.graphics.events import EventType, GraphicsEvent, Key
from src.graphics.image import Image


Color = tuple[int, int, int]


class GraphicsBackend:
    def __init__(
        self: "GraphicsBackend",
        width: int,
        height: int,
        title: str
    ) -> None:
        pygame.init()
        self._screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
    
    def new_image(self: "GraphicsBackend", width: int, height: int) -> Image:
        return Image(pygame.Surface((width, height)))
    
    def load_image(self: "GraphicsBackend", path: str | Path) -> Image:
        return Image(pygame.image.load(str(path)))

    def clear(self: "GraphicsBackend", image: Image, color: Color) -> None:
        image._surface.fill(color)

    def clear_window(self: "GraphicsBackend", color: Color) -> None:
        self._screen.fill(color)
    
    def put_pixel(
        self: "GraphicsBackend",
        image: Image,
        x: int,
        y: int,
        color: Color,
    ) -> None:
        if 0 <= x < image.width and 0 <= y < image.height:
            image._surface.set_at((x, y), color)

    def get_pixel(self: "GraphicsBackend", image: Image, x: int, y: int) -> Color:
        pixel = image._surface.get_at((x, y))
        return pixel.r, pixel.g, pixel.b
    
    def put_image(
        self: "GraphicsBackend",
        target: Image,
        source: Image,
        x: int,
        y: int,
    ) -> None:
        target._surface.blit(source._surface, (x, y))

    def put_image_to_window(self: "GraphicsBackend", image: Image, x: int, y: int) -> None:
        self._screen.blit(image._surface, (x, y))

    def present(self: "GraphicsBackend") -> None:
        pygame.display.flip()

    def poll_events(self: "GraphicsBackend") -> list[GraphicsEvent]:
        events: list[GraphicsEvent] = []

        for event in pygame.event.get():
            converted = self._convert_event(event)
            if converted is not None:
                events.append(converted)

        return events
    
    def quit(self: "GraphicsBackend") -> None:
        pygame.quit()

    def _convert_event(
        self: "GraphicsBackend",
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
        
    def _convert_key(self: "GraphicsBackend", key: int) -> Key:
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