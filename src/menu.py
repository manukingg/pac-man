import pygame as pg

class Menu:
    def __init__(self: "Menu", screen: pg.Surface) -> None:
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()

        self.background_color = (0, 0, 0)
        self.title_color = (255, 255, 0)
        self.text_color = (230, 230, 230)
        self.hover_color = (255, 255, 255)

        self.title_font = pg.font.Font(None, 96)
        self.button_font = pg.font.Font(None, 48)

        self.buttons = [
            ("Start Game", "start"),
            ("Highscores", "highscores"),
            ("Settings", "settings"),
            ("Exit", "quit"),
        ]

        self.selected_index = 0

    def handle_event(self: "Menu", event: pg.event.Event) -> str | None:
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_UP, pg.K_w):
                self.selected_index -= 1
                self.selected_index %= len(self.buttons)

            elif event.key in (pg.K_DOWN, pg.K_s):
                self.selected_index += 1
                self.selected_index %= len(self.buttons)

            elif event.key in (pg.K_RETURN, pg.K_SPACE):
                return self.buttons[self.selected_index][1]
            
            elif event.key == pg.K_ESCAPE:
                return "quit"

        if event.type == pg.MOUSEMOTION:
            self._update_hover(event.pos)
        
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            action = self._get_button_action_at(event.pos)
            if action is not None:
                return action
            
        return None
    
    def update(self: "Menu", dt: float) -> None:
        pass

    def draw(self: "Menu") -> None:
        self.screen.fill(self.background_color)
        self._draw_title()
        self._draw_buttons()

    def _draw_title(self: "Menu") -> None:
        title_surface = self.title_font.render(
            "PAC-MAN",
            True,
            self.title_color
        )
        title_rect = title_surface.get_rect(center=(
            self.width // 2, self.height // 2)
        )
        self.screen.blit(title_surface, title_rect)

    def _draw_buttons(self: "Menu") -> None:
        start_y = 260
        gap = 70

        for index, (label, _) in enumerate(self.buttons):
            color = (self.hover_color if index == self.selected_index
                     else self.text_color)
            text_surface = self.button_font.render(label, True, color)
            text_rect = text_surface.get_rect(
                center=(self.width // 2, start_y + index * gap)
            )
            self.screen.blit(text_surface, text_rect)
    
    def _get_button_rect(self: "Menu", index: int) -> pg.Rect:
        start_y = 260
        gap = 70
        label = self.buttons[index][0]
        text_surface = self.button_font.render(label, True, self.text_color)
        text_rect = text_surface.get_rect(
            center=(self.width // 2, start_y + index * gap)
        )
        return text_rect.inflate(40, 20)
    
    def _update_hover(self: "Menu", mouse_pos: tuple[int, int]) -> None:
        for index in range(len(self.buttons)):
            if self._get_button_rect(index).collidepoint(mouse_pos):
                self.selected_index = index
                return
    
    def _get_button_action_at(
        self: "Menu",
        mouse_pos: tuple[int, int]
    ) -> str | None:
        for index, (_, action) in enumerate(self.buttons):
            if self._get_button_rect(index).collidepoint(mouse_pos):
                return action
        return None