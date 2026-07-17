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

    def draw_line(
        self: "Display",
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: int,
    ) -> None:
        """Draw a horizontal or vertical line."""

        if y1 == y2:
            start_x = min(x1, x2)
            end_x = max(x1, x2)

            for x in range(start_x, end_x + 1):
                self.draw_pixel(
                    x=x,
                    y=y1,
                    color=color,
                )

            return

        if x1 == x2:
            start_y = min(y1, y2)
            end_y = max(y1, y2)

            for y in range(start_y, end_y + 1):
                self.draw_pixel(
                    x=x1,
                    y=y,
                    color=color,
                )

            return

        raise ValueError(
            "Only horizontal and vertical lines are supported."
        )

    @staticmethod
    def _to_rgb(color: int) -> tuple[int, int, int]:
        return (
            (color >> 16) & 0xFF,
            (color >> 8) & 0xFF,
            color & 0xFF,
        )