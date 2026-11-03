from ...ui import MenuButton, DropdownButton, DropdownButtonState
from .menu_layout import MenuLayout

from ...graphics import (
    GraphicsBackend,
    get_aligned_position,
    get_text_width,
    Image,
    Rect,
    Color,
)
from ...constants import (
    MENU_DEFAULT_COLOR,
    MENU_FOCUS_COLOR,
    MENU_TITLE_COLOR
)


class MenuRenderer:
    def __init__(self: "MenuRenderer"):
        self.__cache: dict[tuple[str, int, Color], Image] = {}
        self.__prepared_cache_key: tuple[int, int, int, int] | None = None
        self.__layout_key: tuple[int, ...] | None = None

    def render(
        self: "MenuRenderer",
        display: GraphicsBackend,
        image: Image,
        buttons: list[MenuButton],
        dropdowns: list[DropdownButton],
        focused_menu_index: int | None,
        focused_dropdown_index: int | None,
        focused_option_index: int | None,
    ) -> None:
        layout: MenuLayout = MenuLayout.calculate(
            width=image.width,
            height=image.height,
        )
        self.__update_layout(
            image=image,
            buttons=buttons,
            dropdowns=dropdowns,
            font_size=layout.button_font_size,
            start_y=layout.buttons_start_y,
            gap_between_buttons=layout.button_gap,
            dropdown_font_size=layout.dropdown_font_size,
            dropdown_options_font_size=layout.dropdown_option_font_size,
        )

        self.__prepare_text_cache(
            display=display,
            buttons=buttons,
            dropdowns=dropdowns,
            name_font=layout.title_font_size,
            buttons_font=layout.button_font_size,
            dropdown_font_size=layout.dropdown_font_size,
            dropdown_options_font_size=layout.dropdown_option_font_size,
        )

        self.__render_title(
            display=display,
            image=image,
            font_size=layout.title_font_size,
            top=layout.title_top,
        )

        for index, button in enumerate(buttons):
            self.__render_menu_button(
                display=display,
                button=button,
                is_focused=(index == focused_menu_index),
                font_size=layout.button_font_size,
                image=image,
            )

        for index, dropdown in enumerate(dropdowns):
            self.__render_dropdown_button(
                display=display,
                image=image,
                button=dropdown,
                is_focused=(index == focused_dropdown_index),
                focused_option_index=focused_option_index,
                dropdown_font_size=layout.dropdown_font_size,
                dropdown_options_font_size=layout.dropdown_option_font_size,
            )

    def __render_title(
        self: "MenuRenderer",
        display: GraphicsBackend,
        image: Image,
        font_size: int,
        top: int,
    ) -> None:
        title_image = self.__get_text_image(
            display=display,
            text="PAC-MAN",
            font_size=font_size,
            color=MENU_TITLE_COLOR,
        )

        title_x, title_y = get_aligned_position(
            align=("center", top),
            text="PAC-MAN",
            font_size=font_size,
            image=image
        )
        display.put_image(
            target=image,
            source=title_image,
            x=title_x,
            y=title_y,
        )

    def __render_menu_button(
        self: "MenuRenderer",
        display: GraphicsBackend,
        image: Image,
        button: MenuButton,
        is_focused: bool,
        font_size: int,
    ) -> None:
        color = MENU_FOCUS_COLOR if is_focused else MENU_DEFAULT_COLOR

        self.__draw_cached_text_at(
            display=display,
            image=image,
            text=button.label,
            font_size=font_size,
            color=color,
            x=button.rect.x,
            y=button.rect.y,
        )

        if is_focused:
            self.__draw_focus_arrows(
                display=display,
                button_rect=button.rect,
                font_size=font_size,
                color=MENU_FOCUS_COLOR,
                image=image,
            )

    def __prepare_text_cache(
        self: "MenuRenderer",
        display: GraphicsBackend,
        buttons: list[MenuButton],
        dropdowns: list[DropdownButton],
        name_font: int,
        buttons_font: int,
        dropdown_font_size: int,
        dropdown_options_font_size: int,
    ) -> None:
        cache_key = (
            name_font,
            buttons_font,
            dropdown_font_size,
            dropdown_options_font_size,
        )

        if self.__prepared_cache_key == cache_key:
            return

        self.__get_text_image(
            display=display,
            text="PAC-MAN",
            font_size=name_font,
            color=MENU_TITLE_COLOR,
        )

        for button in buttons:
            self.__get_text_image(
                display=display,
                text=button.label,
                font_size=buttons_font,
                color=MENU_DEFAULT_COLOR,
            )
            self.__get_text_image(
                display=display,
                text=button.label,
                font_size=buttons_font,
                color=MENU_FOCUS_COLOR,
            )

        for dropdown in dropdowns:
            for option in dropdown.options:
                self.__get_text_image(
                    display=display,
                    text=option,
                    font_size=dropdown_options_font_size,
                    color=MENU_DEFAULT_COLOR,
                )
                self.__get_text_image(
                    display=display,
                    text=option,
                    font_size=dropdown_options_font_size,
                    color=MENU_FOCUS_COLOR,
                )
                self.__get_text_image(
                    display=display,
                    text=f"{option} v",
                    font_size=dropdown_font_size,
                    color=MENU_DEFAULT_COLOR,
                )
                self.__get_text_image(
                    display=display,
                    text=f"{option} v",
                    font_size=dropdown_font_size,
                    color=MENU_FOCUS_COLOR,
                )
                self.__get_text_image(
                    display=display,
                    text=f"{option} ^",
                    font_size=dropdown_font_size,
                    color=MENU_DEFAULT_COLOR,
                )
                self.__get_text_image(
                    display=display,
                    text=f"{option} ^",
                    font_size=dropdown_font_size,
                    color=MENU_FOCUS_COLOR,
                )
            for symbol in (">", "<"):
                self.__get_text_image(
                    display=display,
                    text=symbol,
                    font_size=buttons_font,
                    color=MENU_FOCUS_COLOR,
                )

        self.__prepared_cache_key = cache_key

    def __draw_cached_text_at(
        self: "MenuRenderer",
        display: GraphicsBackend,
        image: Image,
        text: str,
        font_size: int,
        color: Color,
        x: int,
        y: int,
    ) -> None:
        text_image = self.__get_text_image(
            display=display,
            text=text,
            font_size=font_size,
            color=color,
        )

        display.put_image(
            target=image,
            source=text_image,
            x=x,
            y=y,
        )

    def __draw_focus_arrows(
        self: "MenuRenderer",
        display: GraphicsBackend,
        image: Image,
        button_rect: Rect,
        font_size: int,
        color: Color,
    ) -> None:
        arrow_gap = font_size * 2
        arrow_width = 5 * font_size

        arrow_y = button_rect.y + button_rect.height // 2 - 4 * font_size

        left_x = button_rect.x - arrow_gap - arrow_width
        right_x = button_rect.x + button_rect.width + arrow_gap

        left_arrow = self.__get_text_image(
            display=display,
            text=">",
            font_size=font_size,
            color=color,
        )

        right_arrow = self.__get_text_image(
            display=display,
            text="<",
            font_size=font_size,
            color=color,
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

    def __get_text_image(
        self: "MenuRenderer",
        display: GraphicsBackend,
        text: str,
        font_size: int,
        color: Color,
    ) -> Image:
        key = (text, font_size, color)

        if key not in self.__cache:
            width = get_text_width(text=text, font_size=font_size)
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
            self.__cache[key] = image

        return self.__cache[key]

    def __render_dropdown_button(
        self: "MenuRenderer",
        display: GraphicsBackend,
        image: Image,
        button: DropdownButton,
        is_focused: bool,
        focused_option_index: int | None,
        dropdown_font_size: int,
        dropdown_options_font_size: int,
    ) -> None:
        color = (
            MENU_FOCUS_COLOR
            if is_focused
            else MENU_DEFAULT_COLOR
        )

        label_x = button.rect.x
        label_y = button.rect.y

        value_x = (button.rect.x +
                   get_text_width(button.label, dropdown_font_size)
                   + dropdown_font_size * 4)
        value_y = button.rect.y

        arrow = "v" if button.state == DropdownButtonState.OPENED else "^"
        value_text = f"{button.selected_option} {arrow}"

        self.__draw_cached_text_at(
            display=display,
            image=image,
            text=button.label,
            font_size=dropdown_font_size,
            color=color,
            x=label_x,
            y=label_y,
        )

        self.__draw_cached_text_at(
            display=display,
            image=image,
            text=value_text,
            font_size=dropdown_font_size,
            color=color,
            x=value_x,
            y=value_y,
        )

        if button.state == DropdownButtonState.OPENED:
            self.__render_dropdown_options(
                display=display,
                image=image,
                button=button,
                is_dropdown_focused=is_focused,
                focused_option_index=focused_option_index,
                dropdown_options_font_size=dropdown_options_font_size,
            )

    def __render_dropdown_options(
        self: "MenuRenderer",
        display: GraphicsBackend,
        image: Image,
        button: DropdownButton,
        is_dropdown_focused: bool,
        focused_option_index: int | None,
        dropdown_options_font_size: int,
    ) -> None:
        for option_index, option in enumerate(button.options):
            option_rect = button.option_rects[option_index]

            is_focused = (
                is_dropdown_focused
                and focused_option_index == option_index
            )

            color = (
                MENU_FOCUS_COLOR
                if is_focused
                else MENU_DEFAULT_COLOR
            )

            self.__draw_cached_text_at(
                display=display,
                image=image,
                text=option,
                font_size=dropdown_options_font_size,
                color=color,
                x=option_rect.x,
                y=option_rect.y,
            )

    def __update_layout(
        self: "MenuRenderer",
        image: Image,
        buttons: list[MenuButton],
        dropdowns: list[DropdownButton],
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
            tuple(
                dropdown.current_index
                for dropdown in dropdowns
            ),
        )

        if self.__layout_key == layout_key:
            return

        self.__layout_key = layout_key

        for index, button in enumerate(buttons):
            x, y = get_aligned_position(
                image=image,
                align=("center", start_y + index * gap_between_buttons),
                text=button.label,
                font_size=font_size,
            )

            button.rect = Rect(
                x=x,
                y=y,
                width=get_text_width(
                    button.label,
                    font_size,
                ),
                height=8 * font_size,
            )

        for dropdown in dropdowns:
            dropdown_text = (
                dropdown.label
                + dropdown.selected_option
                + " ^"
            )

            x, y = get_aligned_position(
                image=image,
                align=("left", "bottom"),
                text=dropdown_text,
                font_size=dropdown_font_size,
            )
            row_height = 8 * dropdown_font_size
            row_width = (
                get_text_width(
                    dropdown_text,
                    dropdown_font_size
                )
                + 4 * dropdown_font_size
            )
            dropdown.rect = Rect(
                x,
                y,
                row_width,
                row_height
            )

            option_rects: list[Rect] = []

            for option_index, option in enumerate(
                dropdown.options
            ):

                option_x = (
                    dropdown.rect.x
                    + get_text_width(
                        dropdown.label,
                        dropdown_font_size
                    )
                    + dropdown_font_size * 4
                )
                option_height = 8 * dropdown_options_font_size
                option_width = get_text_width(
                    dropdown.options[option_index],
                    dropdown_options_font_size
                )

                option_rects.append(
                    Rect(
                        x=option_x,
                        y=(
                            y
                            - row_height
                            - option_index
                            * (
                                option_height
                                + font_size
                            )
                        ),
                        width=option_width,
                        height=option_height,
                    )
                )

            dropdown.option_rects = option_rects
