from .screen import Screen
from ..models import AppState
from ..ui import MenuButton, DropdownButton, DropdownButtonState
from .resolutions import settings_resolutions, resolutions

from ..graphics import (
    PygameWrapper,
    get_aligned_position,
    get_text_width,
    Image,
    GraphicsEvent, EventType,
    Rect,
    Color,
    Key,
)


class MainMenuScreen(Screen):
    """Main application menu."""
    def __init__(
        self: "MainMenuScreen",
        resolution_options: list[str],
        current_resolution: str,
    ) -> None:
        self._buttons: list[MenuButton] = []
        current_index = self._get_resolution_index(
            options=resolution_options,
            current_resolution=current_resolution
        )
        self._dropdown_buttons: list[DropdownButton] = [
            DropdownButton(
                label="Resolution",
                action="set_resolution",
                options=self._get_resolutions(),
                current_index=0,
                rect=Rect(0, 0, 0, 0),
            ),
        ]
        
        self._hovered_index: int | None = None
        self._hovered_dropdown_index: int | None = None
        self._hovered_option_index: int | None = None

        self._pressed_target: tuple[str, int, int | None] | None = None
        self._focused_target: tuple[
            str, int, int | None] = ("menu", 0, None)

        self._cache: dict[tuple[str, int, Color], Image] = {}
        self._prepared_cache_key: tuple[int, int, int, int] | None = None
        self._layout_key: tuple[int, int, int, int, int] | None = None

        self._set_focus("menu", 0, None)

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
                return self._handle_mouse_click_down(event.pos)

        if event.type == EventType.MOUSE_UP:
            if event.button == 1:
                return self._handle_mouse_click_up(event.pos)

        if event.type == EventType.KEY_DOWN:
            return self._handle_key_down(event.key)

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
        self._render_menu_screen(image, display, state)

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
        dropdown_font_size = layout["dropdown_font_size"]
        dropdown_options_font_size = layout["dropdown_options_font_size"]

        self._update_layout(
            image=image,
            font_size=buttons_font,
            start_y=next_button_start,
            gap_between_buttons=gap_between_buttons,
            dropdown_font_size=dropdown_font_size,
            dropdown_options_font_size=dropdown_options_font_size,
        )

        self._prepare_text_cache(
            name_font=name_font,
            buttons_font=buttons_font,
            dropdown_font_size=dropdown_font_size,
            dropdown_options_font_size=dropdown_options_font_size,
            display=display,
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
            image=image
        )
        display.put_image(
            target=image,
            source=title_image,
            x=title_x,
            y=title_y,
        )

        for index, button in enumerate(self._buttons):
            self._render_menu_button(
                button=button,
                button_index=index,
                font_size=buttons_font,
                image=image,
                display=display
            )

        for index, dropdown in enumerate(self._dropdown_buttons):
            self._render_dropdown_button(
                button=dropdown,
                button_index=index,
                font_size=buttons_font,
                dropdown_font_size=dropdown_font_size,
                dropdown_options_font_size=dropdown_options_font_size,
                image=image,
                display=display,
            )

    def _render_menu_button(
        self: "MainMenuScreen",
        button: MenuButton,
        button_index: int,
        font_size: int,
        image: Image,
        display: PygameWrapper,
    ) -> None:
        default_color = (94, 94, 92)
        hover_color = (255, 255, 255)

        color = (hover_color if button_index == self._hovered_index
                 else default_color)

        self._draw_cached_text_at(
            text=button.label,
            font_size=font_size,
            color=color,
            x=button.rect.x,
            y=button.rect.y,
            image=image,
            display=display,
        )

        if button_index == self._hovered_index:
            self._draw_hover_arrows(
                button_rect=button.rect,
                font_size=font_size,
                color=hover_color,
                image=image,
                display=display,
            )

    def _prepare_text_cache(
        self: "MainMenuScreen",
        name_font: int,
        buttons_font: int,
        dropdown_font_size: int,
        dropdown_options_font_size: int,
        display: PygameWrapper,
    ) -> None:
        cache_key = (
            name_font,
            buttons_font,
            dropdown_font_size,
            dropdown_options_font_size,
        )

        if self._prepared_cache_key == cache_key:
            return

        title_color = (255, 255, 0)
        default_color = (94, 94, 92)
        hover_color = (255, 255, 255)
        self._get_text_image(
            text="PAC-MAN",
            font_size=name_font,
            color=title_color,
            display=display,
        )

        for text in ("Play", "Leaderboard", "Instructions", "Quit"):
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

        for dropdown in self._dropdown_buttons:
            for option in dropdown.options:
                self._get_text_image(
                    text=option,
                    font_size=dropdown_options_font_size,
                    color=default_color,
                    display=display
                )
                self._get_text_image(
                    text=option,
                    font_size=dropdown_options_font_size,
                    color=hover_color,
                    display=display
                )
                self._get_text_image(
                    text=f"{option} v",
                    font_size=dropdown_font_size,
                    color=default_color,
                    display=display
                )
                self._get_text_image(
                    text=f"{option} v",
                    font_size=dropdown_font_size,
                    color=hover_color,
                    display=display
                )
                self._get_text_image(
                    text=f"{option} ^",
                    font_size=dropdown_font_size,
                    color=default_color,
                    display=display
                )
                self._get_text_image(
                    text=f"{option} ^",
                    font_size=dropdown_font_size,
                    color=hover_color,
                    display=display
                )
            for symbol in (">", "<"):
                self._get_text_image(
                    text=symbol,
                    font_size=buttons_font,
                    color=hover_color,
                    display=display
                )

        self._prepared_cache_key = cache_key

    def _draw_cached_text_at(
        self: "MainMenuScreen",
        text: str,
        font_size: int,
        color: Color,
        x: int,
        y: int,
        image: Image,
        display: PygameWrapper,
    ) -> None:
        text_image = self._get_text_image(
            text=text,
            font_size=font_size,
            color=color,
            display=display,
        )

        display.put_image(
            target=image,
            source=text_image,
            x=x,
            y=y,
        )

    def _handle_mouse_motion(
        self: "MainMenuScreen",
        mouse_pos: tuple[int, int] | None,
    ) -> None:
        self._hovered_index = None
        self._hovered_dropdown_index = None
        self._hovered_option_index = None

        if mouse_pos is None:
            return

        for dropdown_index, dropdown in enumerate(self._dropdown_buttons):
            if dropdown.rect.contains(mouse_pos):
                self._set_focus("dropdown", dropdown_index, None)
                return

            if dropdown.state == DropdownButtonState.OPENED:
                intersaction_rect = self._get_dropdown_intersation_rect(
                                                                dropdown)

                if intersaction_rect.contains(mouse_pos):
                    for option_index, option_rect in enumerate(
                                            dropdown.option_rects):
                        if option_rect.contains(mouse_pos):
                            self._set_focus(
                                "option",
                                dropdown_index,
                                option_index
                            )
                            return
                    self._set_focus("dropdown", dropdown_index, None)
                    return

        for index, button in enumerate(self._buttons):
            if button.rect.contains(mouse_pos):
                self._set_focus("menu", index, None)
                return

    def _handle_mouse_click_down(
        self: "MainMenuScreen",
        mouse_pos: tuple[int, int],
    ) -> None:
        self._pressed_target = None

        opened_dropdown = self._get_open_dropdown()

        if opened_dropdown is not None:
            dropdown_index, dropdown = opened_dropdown
            interaction_rect = self._get_dropdown_intersation_rect(dropdown)

            if mouse_pos is None or not interaction_rect.contains(mouse_pos):
                dropdown.state = DropdownButtonState.CLOSED
                self._set_focus("dropdown", dropdown_index, None)
                return None

        if mouse_pos is None:
            return None

        for dropdown_index, dropdown in enumerate(self._dropdown_buttons):
            if dropdown.state == DropdownButtonState.OPENED:
                for option_index, option_rect in enumerate(
                                        dropdown.option_rects):
                    if option_rect.contains(mouse_pos):
                        self._pressed_target = (
                            "option",
                            dropdown_index,
                            option_index,
                        )
                        return

        for dropdown_index, dropdown in enumerate(self._dropdown_buttons):
            if dropdown.rect.contains(mouse_pos):
                self._pressed_target = (
                    "dropdown",
                    dropdown_index,
                    None,
                )
                return

        for index, button in enumerate(self._buttons):
            if button.rect.contains(mouse_pos):
                self._pressed_target = (
                    "menu",
                    index,
                    None,
                )
                return

    def _handle_mouse_click_up(
        self: "MainMenuScreen",
        mouse_pos: tuple[int, int],
    ) -> str | None:
        pressed_target = self._pressed_target
        self._pressed_target = None

        if mouse_pos is None or pressed_target is None:
            return None

        target_type, first_index, second_index = pressed_target

        if target_type == "option":
            dropdown = self._dropdown_buttons[first_index]

            if second_index is None:
                return None

            option_rect = dropdown.option_rects[second_index]

            if option_rect.contains(mouse_pos):
                if second_index == dropdown.current_index:
                    dropdown.state = DropdownButtonState.CLOSED
                    self._set_focus("dropdown", first_index, None)
                    return None
                dropdown.current_index = second_index
                dropdown.state = DropdownButtonState.CLOSED
                self._set_focus("dropdown", first_index, None)

                return f"{dropdown.action}:{dropdown.selected_option}"

            return None

        if target_type == "dropdown":
            dropdown = self._dropdown_buttons[first_index]

            if dropdown.rect.contains(mouse_pos):
                if dropdown.state == DropdownButtonState.OPENED:
                    dropdown.state = DropdownButtonState.CLOSED
                else:
                    self._close_all_dropdowns()
                    dropdown.state = DropdownButtonState.OPENED

            return None

        if target_type == "menu":
            button = self._buttons[first_index]

            if button.rect.contains(mouse_pos):
                self._close_all_dropdowns()
                self._set_focus("menu", first_index, None)
                return button.action

            return None

        return None

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

    def _close_all_dropdowns(self: "MainMenuScreen") -> None:
        for dropdown in self._dropdown_buttons:
            dropdown.state = DropdownButtonState.CLOSED

    def _get_dropdown_intersation_rect(
        self: "MainMenuScreen",
        dropdown: DropdownButton,
    ) -> Rect:
        background_rect = self._get_dropdown_background_rect(dropdown)

        min_x = dropdown.rect.x
        min_y = dropdown.rect.y
        max_x = dropdown.rect.x + dropdown.rect.width
        max_y = dropdown.rect.y + dropdown.rect.height

        if background_rect is not None:
            min_x = min(min_x, background_rect.x)
            min_y = min(min_y, background_rect.y)
            max_x = max(max_x, background_rect.x + background_rect.width)
            max_y = max(max_y, background_rect.y + background_rect.height)

        return Rect(
            x=min_x,
            y=min_y,
            width=max_x - min_x,
            height=max_y - min_y,
        )

    def _render_dropdown_button(
        self: "MainMenuScreen",
        button: DropdownButton,
        button_index: int,
        font_size: int,
        dropdown_font_size: int,
        dropdown_options_font_size: int,
        image: Image,
        display: PygameWrapper,
    ) -> None:
        default_color = (94, 94, 92)
        hover_color = (255, 255, 255)

        is_button_hovered = button_index == self._hovered_dropdown_index
        color = hover_color if is_button_hovered else default_color

        label_x = button.rect.x
        label_y = button.rect.y

        value_x = (button.rect.x +
                   get_text_width(button.label, dropdown_font_size)
                   + dropdown_font_size * 4)
        value_y = button.rect.y

        arrow = "v" if button.state == DropdownButtonState.OPENED else "^"
        value_text = f"{button.selected_option} {arrow}"

        self._draw_cached_text_at(
            text=button.label,
            font_size=dropdown_font_size,
            color=color,
            x=label_x,
            y=label_y,
            image=image,
            display=display,
        )

        self._draw_cached_text_at(
            text=value_text,
            font_size=dropdown_font_size,
            color=color,
            x=value_x,
            y=value_y,
            image=image,
            display=display,
        )

        if button.state == DropdownButtonState.OPENED:
            self._render_dropdown_options(
                button=button,
                button_index=button_index,
                dropdown_options_font_size=dropdown_options_font_size,
                image=image,
                display=display,
            )

    def _render_dropdown_options(
        self: "MainMenuScreen",
        button: DropdownButton,
        button_index: int,
        dropdown_options_font_size: int,
        image: Image,
        display: PygameWrapper,
    ) -> None:
        default_color = (94, 94, 92)
        hover_color = (255, 255, 255)

        for option_index, option in enumerate(button.options):
            option_rect = button.option_rects[option_index]

            is_option_hovered = (
                self._hovered_dropdown_index == button_index
                and self._hovered_option_index == option_index
            )

            color = hover_color if is_option_hovered else default_color

            self._draw_cached_text_at(
                text=option,
                font_size=dropdown_options_font_size,
                color=color,
                x=option_rect.x,
                y=option_rect.y,
                image=image,
                display=display,
            )

    def _get_dropdown_background_rect(
        self: "MainMenuScreen",
        button: DropdownButton,
    ) -> Rect | None:
        if not button.option_rects:
            return None

        min_x = button.option_rects[0].x
        max_x = button.option_rects[0].x + button.option_rects[0].width

        min_y = button.option_rects[0].y
        max_y = button.option_rects[0].y + button.option_rects[0].height

        for option_rect in button.option_rects:
            min_x = min(min_x, option_rect.x)
            min_y = min(min_y, option_rect.y)
            max_x = max(max_x, option_rect.x + option_rect.width)
            max_y = max(max_y, option_rect.y + option_rect.height)

        return Rect(
            x=min_x,
            y=min_y,
            width=max_x - min_x,
            height=max_y - min_y,
        )

    def _update_layout(
        self: "MainMenuScreen",
        image: Image,
        font_size: int,
        start_y: int,
        gap_between_buttons: int,
        dropdown_font_size: int,
        dropdown_options_font_size: int,
    ) -> None:
        image_width = image.width
        image_height = image.height
        layout_key = (
            image_width,
            image_height,
            font_size,
            dropdown_font_size,
            dropdown_options_font_size,
        )

        if self._layout_key == layout_key:
            return

        self._layout_key = layout_key
        self._buttons.clear()

        for index, (button_text, button_action) in enumerate(
            [
                ("Play", "start_game"),
                ("Leaderboard", "open_leaderboard"),
                ("Instructions", "open_instructions"),
                ("Quit", "quit")
            ]
        ):
            x, y = get_aligned_position(
                align=("center", start_y + index * gap_between_buttons),
                text=button_text,
                font_size=font_size,
                image=image,
            )
            row_height = 8 * font_size
            row_width = get_text_width(button_text, font_size)

            self._buttons.append(
                MenuButton(
                    label=button_text,
                    action=button_action,
                    rect=Rect(x, y, row_width, row_height)
                )
            )

        for dropdown in self._dropdown_buttons:
            dropdown_text = dropdown.label + dropdown.selected_option + " ^"
            x, y = get_aligned_position(
                align=("left", "bottom"),
                text=dropdown_text,
                font_size=dropdown_font_size,
                image=image,
            )
            row_height = 8 * dropdown_font_size
            row_width = (get_text_width(dropdown_text, dropdown_font_size) +
                         4 * dropdown_font_size)
            dropdown.rect = Rect(x, y, row_width, row_height)

            option_rects: list[Rect] = []

            for option_index in range(len(dropdown.options)):

                option_x = (dropdown.rect.x + get_text_width(
                    dropdown.label, dropdown_font_size)
                    + dropdown_font_size * 4)
                option_height = 8 * dropdown_options_font_size
                option_width = get_text_width(
                    dropdown.options[option_index], dropdown_options_font_size)

                option_rects.append(
                    Rect(
                        x=option_x,
                        y=y - row_height - option_index * (option_height
                                                           + font_size),
                        width=option_width,
                        height=option_height,
                    )
                )

            dropdown.option_rects = option_rects

    def _set_focus(
        self: "MainMenuScreen",
        target_type: str,
        first_index: int,
        second_index: int | None = None,
    ) -> None:
        self._focused_target = (target_type, first_index, second_index)

        self._hovered_index = None
        self._hovered_dropdown_index = None
        self._hovered_option_index = None

        if target_type == "menu":
            self._hovered_index = first_index

        elif target_type == "dropdown":
            self._hovered_dropdown_index = first_index

        elif target_type == "option":
            self._hovered_dropdown_index = first_index
            self._hovered_option_index = second_index

    def _get_open_dropdown_index(self: "MainMenuScreen") -> int | None:
        for index, dropdown in enumerate(self._dropdown_buttons):
            if dropdown.state == DropdownButtonState.OPENED:
                return index

        return None

    def _move_dropdown_option_focus(
        self: "MainMenuScreen",
        dropdown_index: int,
        step: int,
    ) -> None:
        dropdown = self._dropdown_buttons[dropdown_index]

        if not dropdown.options:
            return

        current_index = self._hovered_option_index

        if current_index is None:
            current_index = dropdown.current_index

        next_index = (current_index + step) % len(dropdown.options)

        self._set_focus("option", dropdown_index, next_index)

    def _activate_focused_target(self: "MainMenuScreen") -> str | None:
        target_type, first_index, second_index = self._focused_target

        if target_type == "menu":
            button = self._buttons[first_index]
            self._close_all_dropdowns()
            return button.action

        if target_type == "dropdown":
            dropdown = self._dropdown_buttons[first_index]

            if dropdown.state == DropdownButtonState.OPENED:
                dropdown.state = DropdownButtonState.CLOSED
                self._set_focus("dropdown", first_index, None)
            else:
                self._close_all_dropdowns()
                dropdown.state = DropdownButtonState.OPENED
                self._set_focus("option", first_index, dropdown.current_index)

            return None

        if target_type == "option":
            dropdown = self._dropdown_buttons[first_index]

            if second_index is None:
                return None

            if second_index == dropdown.current_index:
                dropdown.state = DropdownButtonState.CLOSED
                self._set_focus("dropdown", first_index, None)
                return None

            dropdown.current_index = second_index
            dropdown.state = DropdownButtonState.CLOSED
            self._set_focus("dropdown", first_index, None)

            return f"{dropdown.action}:{dropdown.selected_option}"

        return None

    def _get_focus_order(
        self: "MainMenuScreen"
    ) -> list[tuple[str, int, int | None]]:
        result: list[tuple[str, int, int | None]] = []

        for index in range(len(self._buttons)):
            result.append(("menu", index, None))

        for index in range(len(self._dropdown_buttons)):
            result.append(("dropdown", index, None))

        return result

    def _move_focus(self: "MainMenuScreen", step: int) -> None:
        focus_order = self._get_focus_order()

        if not focus_order:
            return

        try:
            current_index = focus_order.index(self._focused_target)
        except ValueError:
            current_index = 0

        next_index = (current_index + step) % len(focus_order)
        target_type, first_index, second_index = focus_order[next_index]

        self._set_focus(target_type, first_index, second_index)

    def _handle_open_dropdown_key(
        self: "MainMenuScreen",
        key: Key,
        dropdown_index: int,
    ) -> str | None:
        if key in (Key.UP, Key.W):
            self._move_dropdown_option_focus(
                dropdown_index=dropdown_index,
                step=1,
            )
            return None

        if key in (Key.DOWN, Key.S):
            self._move_dropdown_option_focus(
                dropdown_index=dropdown_index,
                step=-1,
            )
            return None

        if key in (Key.ENTER, Key.SPACE):
            if self._hovered_option_index is None:
                self._set_focus(
                    "option",
                    dropdown_index,
                    self._dropdown_buttons[dropdown_index].current_index,
                )
                return None
            return self._activate_focused_target()

        if key == Key.ESCAPE:
            self._dropdown_buttons[dropdown_index].state = (
                                    DropdownButtonState.CLOSED)
            self._set_focus("dropdown", dropdown_index, None)
            return None

        return None

    def _handle_key_down(
        self: "MainMenuScreen",
        key: Key | None,
    ) -> str | None:
        if key is None:
            return None

        open_dropdown_index = self._get_open_dropdown_index()

        if open_dropdown_index is not None:
            return self._handle_open_dropdown_key(
                key=key,
                dropdown_index=open_dropdown_index,
            )

        if key in (Key.DOWN, Key.S, Key.RIGHT, Key.D):
            self._move_focus(1)
            return None

        if key in (Key.UP, Key.W, Key.LEFT, Key.A):
            self._move_focus(-1)
            return None

        if key in (Key.ENTER, Key.SPACE):
            return self._activate_focused_target()

        if key == Key.ESCAPE:
            return "quit"

        return None

    def _get_resolutions(self: "MainMenuScreen") -> list[str]:
        res = []
        for resolution in resolutions.keys():
            res.append(resolution)
        print(res)
        return res

    def _get_open_dropdown(
        self: "MainMenuScreen"
    ) -> tuple[int, DropdownButton] | None:
        for index, dropdown in enumerate(self._dropdown_buttons):
            if dropdown.state == DropdownButtonState.OPENED:
                return index, dropdown

        return None

    def _get_resolution_index(
        self: "MainMenuScreen",
        options: list[str],
        current_resolution: str,
    ) -> int:
        try:
            return options.index(current_resolution)
        except ValueError:
            return 0
