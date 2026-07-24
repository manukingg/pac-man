from .screen import Screen

from ..graphics import PygameWrapper
from ..graphics.helpers import get_aligned_position
from ..graphics.image import Image
from ..graphics.events import GraphicsEvent, EventType
from ..graphics.rect import Rect
from ..models import AppState, ScreenType
from ..models.button import MenuButton
from ..graphics.image import Color
from .resolutions import settings_resolutions, resolutions


class MainMenuScreen(Screen):
    """Main application menu."""
    def __init__(self: "MainMenuScreen") -> None:
        self._buttons: list[MenuButton] = []
        self._hovered_index: int | None = None
        self._cache: dict[tuple[str, int, Color], Image] = {}
        self._prepared_cache_key: tuple[int, int] | None = None

    def handle_event(
        self: "MainMenuScreen",
        event: GraphicsEvent,
        state: AppState,
    ) -> str | None:
        if event.type == EventType.MOUSE_MOTION:
            self._handle_mouse_motion(event.pos)
            return None

        if event.type == EventType.MOUSE_DOWN:
            if event.button == 1:
                return self._handle_mouse_click(event.pos)

        return None

    def update(
        self: "MainMenuScreen",
        delta_time: float,
        state: AppState,
    ) -> str | None:
        return None

    def render(
        self: "MainMenuScreen",
        image: Image,
        display: PygameWrapper,
        state: AppState,
    ) -> None:
        if state.current_screen == ScreenType.MAIN_MENU:
            self._render_menu_screen(image, display, state)

    def _prepare_text_cache(
        self: "MainMenuScreen",
        name_font: int,
        buttons_font: int,
        display: PygameWrapper,
    ) -> None:
        cache_key = (name_font, buttons_font)

        if self._prepared_cache_key == cache_key:
            return

        title_color = (255, 255, 0)
        default_color = (94, 94, 92)
        hover_color = (255, 255, 255)

        self._get_text_image(
            text="PAC-MAN",
            font_size=name_font,
            color=title_color,
            display=display
        )

        for text in ("Play", "Leaderboard", "Settings", "Quit"):
            self._get_text_image(
                text=text,
                font_size=buttons_font,
                color=default_color,
                display=display,
            )
            self._get_text_image(
                text=text,
                font_size=buttons_font,
                color=hover_color,
                display=display,
            )

        self._get_text_image(
            text=">",
            font_size=buttons_font,
            color=hover_color,
            display=display,
        )
        self._get_text_image(
            text="<",
            font_size=buttons_font,
            color=hover_color,
            display=display
        )

        self._prepared_cache_key = cache_key

    def _render_menu_screen(
        self: "MainMenuScreen",
        image: Image,
        display: PygameWrapper,
        state: AppState,
    ) -> None:
        resolution_key = settings_resolutions.get((image.width, image.height))
        layout = resolutions.get(resolution_key)
        name_font = layout["name_font"]
        buttons_font = layout["buttons_font"]
        name_top_gap = layout["name_top_gap"]
        next_button_start = layout["next_button_start"]
        gap_between_buttons = layout["gap_between_buttons"]

        self._prepare_text_cache(
            name_font=name_font,
            buttons_font=buttons_font,
            display=display
        )

        title_image = self._get_text_image(
            text="PAC-MAN",
            font_size=name_font,
            color=(255, 255, 0),
            display=display,
        )
        title_x, title_y = get_aligned_position(
            align=("center", name_top_gap),
            text="PAC-MAN",
            font_size=name_font,
            image=image,
        )
        display.put_image(
            target=image,
            source=title_image,
            x=title_x,
            y=title_y,
        )

        self._fill_menu_buttons(
            font_size=buttons_font,
            image=image,
            display=display,
            gap_between_buttons=gap_between_buttons,
            next_button_start=next_button_start,
        )

    def _handle_mouse_motion(
        self: "MainMenuScreen",
        mouse_pos: tuple[int, int] | None,
    ) -> None:
        if mouse_pos is None:
            self._hovered_index = None
            return

        self._hovered_index = None

        for index, button in enumerate(self._buttons):
            if button.rect.contains(mouse_pos):
                self._hovered_index = index
                return

    def _handle_mouse_click(
        self: "MainMenuScreen",
        mouse_pos: tuple[int, int],
    ) -> str | None:
        if mouse_pos is None:
            return None

        for button in self._buttons:
            if button.rect.contains(mouse_pos):
                return button.action

        return None

    def _fill_menu_buttons(
        self: "MainMenuScreen",
        font_size: int,
        image: Image,
        display: PygameWrapper,
        gap_between_buttons: int,
        next_button_start: int,
    ) -> None:
        recreate = len(self._buttons) == 0

        button_specs = (
            ("Play", "start_game"),
            ("Leaderboard", "open_leaderboard"),
            ("Settings", "open_settings"),
            ("Quit", "quit"),
        )

        for index, (text, action) in enumerate(button_specs):
            self._create_button(text=text,
                                action=action,
                                align=("center", next_button_start +
                                       index * gap_between_buttons),
                                font_size=font_size,
                                image=image,
                                default_color=(94, 94, 92),
                                hover_color=(255, 255, 255),
                                display=display,
                                recreate=recreate
                                )

    def _create_button(
        self: "MainMenuScreen",
        text: str,
        action: str,
        align: tuple[int | str | float, int | str | float],
        font_size: int,
        image: Image,
        default_color: Color,
        hover_color: Color,
        display: PygameWrapper,
        recreate: bool,
    ) -> None:
        if recreate:
            x, y = get_aligned_position(
                align=align,
                text=text,
                font_size=font_size,
                image=image
            )

            width = (5 * font_size * len(text) +
                     (len(text) - 1) * font_size)
            height = 8 * font_size
            visual_rect = Rect(x, y, width, height)
            hitbox = visual_rect.inflate(
                padding_x=font_size * 4,
                padding_y=font_size * 2
            )
            button = MenuButton(
                label=text,
                action=action,
                rect=hitbox,
            )
            self._buttons.append(button)
        current_button: MenuButton | None = None
        current_index: int | None = None

        for index, button_specified in enumerate(self._buttons):
            if button_specified.label == text:
                current_button = button_specified
                current_index = index
                break

        if current_button is None or current_index is None:
            return

        is_hovered = current_index == self._hovered_index

        color = hover_color if is_hovered else default_color

        text_image = self._get_text_image(
            text=text,
            font_size=font_size,
            color=color,
            display=display,
        )

        x, y = get_aligned_position(
            align=align,
            text=text,
            font_size=font_size,
            image=image,
        )

        display.put_image(
            target=image,
            source=text_image,
            x=x,
            y=y,
        )

        if is_hovered:
            self._draw_hover_arrows(
                button_rect=current_button.rect,
                font_size=font_size,
                color=hover_color,
                image=image,
                display=display,
            )

    def _draw_hover_arrows(
        self: "MainMenuScreen",
        button_rect: Rect,
        font_size: int,
        color: Color,
        image: Image,
        display: PygameWrapper,
    ) -> None:
        arrow_gap = font_size * 2
        arrow_width = 5 * font_size

        arrow_y = button_rect.y + button_rect.height // 2 - 4 * font_size

        left_x = button_rect.x - arrow_gap - arrow_width
        right_x = button_rect.x + button_rect.width + arrow_gap

        left_arrow = self._get_text_image(
            text=">",
            font_size=font_size,
            color=color,
            display=display,
        )

        right_arrow = self._get_text_image(
            text="<",
            font_size=font_size,
            color=color,
            display=display,
        )

        display.put_image(
            target=image,
            source=left_arrow,
            x=left_x,
            y=arrow_y,
        )

        display.put_image(
            target=image,
            source=right_arrow,
            x=right_x,
            y=arrow_y,
        )

    def _get_text_image(
        self: "MainMenuScreen",
        text: str,
        font_size: int,
        color: Color,
        display: PygameWrapper,
    ) -> Image:
        key = (text, font_size, color)

        if key not in self._cache:
            width = len(text) * 5 * font_size + (len(text) - 1) * font_size
            height = 8 * font_size

            image = display.new_image(width, height)
            display.clear(image, (0, 0, 0))

            display.write_text(
                text=text,
                image=image,
                font_size=font_size,
                color=color,
                position=(0, 0),
            )
            self._cache[key] = image

        return self._cache[key]
