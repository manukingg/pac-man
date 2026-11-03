from ...ui import (
    MenuButton,
    DropdownButton,
    DropdownButtonState
)

from ...graphics import (
    GraphicsEvent,
    EventType,
    Key,
)


class MenuController:
    def __init__(
        self: "MenuController",
        buttons: list[MenuButton],
        dropdowns: list[DropdownButton],
    ) -> None:
        self.__buttons = buttons
        self.__dropdowns = dropdowns

        self.__focused_menu_index: int | None = None
        self.__focused_dropdown_index: int | None = None
        self.__focused_option_index: int | None = None

        self.__focused_target: tuple[
            str,
            int,
            int | None
        ] = ("menu", 0, None)

        self.__held_scroll_key: Key | None = None
        self.__held_scroll_elapsed = 0.0
        self.__repeat_elapsed = 0.0

        self.__repeat_start_delay = 0.5
        self.__repeat_interval = 0.04

        self.__set_focus("menu", 0, None)

    @property
    def focused_menu_index(self: "MenuController") -> int | None:
        return self.__focused_menu_index

    @property
    def focused_dropdown_index(
        self: "MenuController",
    ) -> int | None:
        return self.__focused_dropdown_index

    @property
    def focused_option_index(
        self: "MenuController",
    ) -> int | None:
        return self.__focused_option_index

    def handle_event(
        self: "MenuController",
        event: GraphicsEvent,
    ) -> str | None:
        if event.type == EventType.KEY_DOWN:
            return self.__handle_key_down(event.key)

        if event.type == EventType.KEY_UP:
            self.__handle_key_up(event.key)
            return None

        return None

    def update(
        self: "MenuController",
        delta_time: float,
    ) -> str | None:
        return self.__update_key_repeat(delta_time)

    def __set_focus(
        self: "MenuController",
        target_type: str,
        first_index: int,
        second_index: int | None = None,
    ) -> None:
        self.__focused_target = (
            target_type,
            first_index,
            second_index
        )

        self.__focused_menu_index = None
        self.__focused_dropdown_index = None
        self.__focused_option_index = None

        if target_type == "menu":
            self.__focused_menu_index = first_index
            return

        elif target_type == "dropdown":
            self.__focused_dropdown_index = first_index
            return

        elif target_type == "option":
            self.__focused_dropdown_index = first_index
            self.__focused_option_index = second_index
            return

    def __close_all_dropdowns(self: "MenuController") -> None:
        for dropdown in self.__dropdowns:
            dropdown.close()

    def __get_open_dropdown_index(self: "MenuController") -> int | None:
        for index, dropdown in enumerate(self.__dropdowns):
            if dropdown.state == DropdownButtonState.OPENED:
                return index

        return None

    def __move_dropdown_option_focus(
        self: "MenuController",
        dropdown_index: int,
        step: int,
    ) -> None:
        dropdown = self.__dropdowns[dropdown_index]

        if not dropdown.options:
            return

        current_index = self.__focused_option_index

        if current_index is None:
            current_index = dropdown.current_index

        next_index = (current_index + step) % len(dropdown.options)

        self.__set_focus("option", dropdown_index, next_index)

    def __activate_focused_target(self: "MenuController") -> str | None:
        target_type, first_index, second_index = self.__focused_target

        if target_type == "menu":
            button = self.__buttons[first_index]
            self.__close_all_dropdowns()
            return button.action

        if target_type == "dropdown":
            dropdown = self.__dropdowns[first_index]

            if dropdown.state == DropdownButtonState.OPENED:
                dropdown.close()
                self.__set_focus("dropdown", first_index, None)
            else:
                self.__close_all_dropdowns()
                dropdown.open()
                self.__set_focus("option", first_index, dropdown.current_index)

            return None

        if target_type == "option":
            dropdown = self.__dropdowns[first_index]

            if second_index is None:
                return None

            if second_index == dropdown.current_index:
                dropdown.close()
                self.__set_focus("dropdown", first_index, None)
                return None

            dropdown.current_index = second_index
            dropdown.close()
            self.__set_focus("dropdown", first_index, None)

            return f"{dropdown.action}:{dropdown.selected_option}"

        return None

    def __get_focus_order(
        self: "MenuController"
    ) -> list[tuple[str, int, int | None]]:
        result: list[tuple[str, int, int | None]] = []

        for index in range(len(self.__buttons)):
            result.append(("menu", index, None))

        for index in range(len(self.__dropdowns)):
            result.append(("dropdown", index, None))

        return result

    def __move_focus(self: "MenuController", step: int) -> None:
        focus_order = self.__get_focus_order()

        if not focus_order:
            return

        try:
            current_index = focus_order.index(self.__focused_target)
        except ValueError:
            current_index = 0

        next_index = (current_index + step) % len(focus_order)
        target_type, first_index, second_index = focus_order[next_index]

        self.__set_focus(target_type, first_index, second_index)

    def __handle_open_dropdown_key(
        self: "MenuController",
        key: Key,
        dropdown_index: int,
    ) -> str | None:
        if key in (Key.UP, Key.W):
            self.__move_dropdown_option_focus(
                dropdown_index=dropdown_index,
                step=1,
            )
            return None

        if key in (Key.DOWN, Key.S):
            self.__move_dropdown_option_focus(
                dropdown_index=dropdown_index,
                step=-1,
            )
            return None

        if key in (Key.ENTER, Key.SPACE):
            if self.__focused_option_index is None:
                self.__set_focus(
                    "option",
                    dropdown_index,
                    self.__dropdowns[dropdown_index].current_index,
                )
                return None
            return self.__activate_focused_target()

        if key == Key.ESCAPE:
            self.__dropdowns[dropdown_index].close()
            self.__set_focus("dropdown", dropdown_index, None)
            return None

        return None

    def __handle_key_down(
        self: "MenuController",
        key: Key | None,
    ) -> str | None:
        if key is None:
            return None

        if self.__is_scroll_key(key):
            is_new_press = self.__start_key_repeat(key)

            if is_new_press:
                return self.__apply_scroll_key(key)

            return None

        open_dropdown_index = self.__get_open_dropdown_index()

        if open_dropdown_index is not None:
            return self.__handle_open_dropdown_key(
                key=key,
                dropdown_index=open_dropdown_index,
            )

        if key in (Key.ENTER, Key.SPACE):
            return self.__activate_focused_target()

        if key == Key.ESCAPE:
            return "quit"

        return None

    def __apply_scroll_key(
        self: "MenuController",
        key: Key,
    ) -> str | None:
        open_dropdown_index = self.__get_open_dropdown_index()

        if open_dropdown_index is not None:
            return self.__handle_open_dropdown_key(
                key=key,
                dropdown_index=open_dropdown_index,
            )

        if key in (Key.DOWN, Key.S, Key.D, Key.RIGHT):
            self.__move_focus(1)
            return None

        if key in (Key.UP, Key.W, Key.A, Key.LEFT):
            self.__move_focus(-1)
            return None

        return None

    def __is_scroll_key(self: "MenuController", key: Key | None) -> bool:
        return key in (
            Key.UP,
            Key.W,
            Key.A,
            Key.LEFT,
            Key.DOWN,
            Key.S,
            Key.D,
            Key.RIGHT,
        )

    def __start_key_repeat(self: "MenuController", key: Key) -> bool:
        if self.__held_scroll_key == key:
            return False

        self.__held_scroll_key = key
        self.__held_scroll_elapsed = 0.0
        self.__repeat_elapsed = 0.0

        return True

    def __stop_key_repeat(self: "MenuController", key: Key | None) -> None:
        if key == self.__held_scroll_key:
            self.__held_scroll_key = None
            self.__held_scroll_elapsed = 0.0
            self.__repeat_elapsed = 0.0

    def __handle_key_up(
        self: "MenuController",
        key: Key | None,
    ) -> None:
        self.__stop_key_repeat(key)

    def __update_key_repeat(
        self: "MenuController",
        delta_time: float,
    ) -> str | None:
        if self.__held_scroll_key is None:
            return None

        previous_elapsed = self.__held_scroll_elapsed
        self.__held_scroll_elapsed += delta_time

        if (
            previous_elapsed < self.__repeat_start_delay
            and self.__held_scroll_elapsed >= self.__repeat_start_delay
        ):
            self.__repeat_elapsed = 0.0
            return self.__apply_scroll_key(self.__held_scroll_key)

        if self.__held_scroll_elapsed < self.__repeat_start_delay:
            return None

        self.__repeat_elapsed += delta_time

        if self.__repeat_elapsed >= self.__repeat_interval:
            self.__repeat_elapsed = 0.0
            return self.__apply_scroll_key(self.__held_scroll_key)

        return None
