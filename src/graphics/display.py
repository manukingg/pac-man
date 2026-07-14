import pygame


class Display:
    """Pygame backend restricted to MLX-like operations."""

    def __init__(
        self: "Display",
        width: int,
        height: int,
        title: str,
    ) -> None:
        pygame.init()

        self._screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

        self._font = pygame.font.Font(None, 36)

    def clear(self: "Display", color: int) -> None:
        self._screen.fill(self._to_rgb(color))

    def draw_text(
        self: "Display",
        x: int,
        y: int,
        text: str,
        color: int,
    ) -> None:
        rendered = self._font.render(
            text,
            True,
            self._to_rgb(color),
        )
        self._screen.blit(rendered, (x, y))

    def present(self: "Display") -> None:
        pygame.display.flip()

    def close(self: "Display") -> None:
        pygame.quit()

    @staticmethod
    def _to_rgb(color: int) -> tuple[int, int, int]:
        return (
            (color >> 16) & 0xFF,
            (color >> 8) & 0xFF,
            color & 0xFF,
        )