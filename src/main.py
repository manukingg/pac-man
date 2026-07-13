import pygame as pg

from src.menu import Menu


class App:
    FPS = 60

    def __init__(self: "App") -> None:
        pg.init()

        try:
            pg.mixer.init()
        except pg.error:
            print("Audio is not avaialbe")
        
        self.settings = GameSettings()
        self.screen = self._create_display()

        pg.display.set_caption("Pac-Man")

        self.clock = pg.time.Clock()
        self.running = True
        self.current_screen: Menu | SettingsScreen = Menu(self.screen)

        self._apply_audio_settings()

    def run(self: "App") -> None:
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    continue

                action = self.current_screen.handle_event(event)
                self._handle_action(action)
            
            self.current_screen.update(dt)
            self.current_screen.draw()

            pg.display.flip()
        
        pg.quit()
    
    def _create_display(self: "App") -> pg.Surface:
        flags = pg.FULLSCREEN if self.settings.fullscreen else pg.RESIZABLE
        return pg.display.set_mode(self.settings.resolution, flags)
    
    def _apply_display_settings(self: "App") -> None:
        self.screen = self._create_display()
        self.current_screen.set_screen(self.screen)

    def _apply_audio_settings(self: "App") -> None:
        if pg.mixer.get_init() is not None:
            pg.mixer.music.set_volume(self.settings.volume / 100)

    def _handle_action(self: "App", action: str | None) -> None:
        if action is None:
            return
        
        if action == "quit":
            self.running = False
        
        elif action == "settings":
            self.current_screen = SettingsScreen(self.screen, self.settings)

        elif action == "menu":
            self.current_screen = Menu(self.screen)
        
        elif action == "apply_settings":
            if isinstance(self.current_screen, SettingsScreen):
                self.settings = self.current_screen.get_settings()
                self._apply_audio_settings()
                self._apply_display_settings()