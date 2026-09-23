from src.graphics.events import EventType, Key
from src.graphics.mlx_wrapper import MlxWrapper


def main() -> None:
    display = MlxWrapper(
        width=800,
        height=600,
        title="MLX XPM Test",
    )

    frame = display.new_image(
        width=800,
        height=600,
    )

    display.clear(
        image=frame,
        color=(30, 30, 30),
    )

    pacman = display.load_image(
        "assets/pacman-down/1.xpm"
    )

    print(
        f"XPM loaded: {pacman.width}x{pacman.height}"
    )

    display.put_image(
        target=frame,
        source=pacman,
        x=100,
        y=100,
    )

    def run_frame(
        _delta_time: float,
    ) -> bool:
        for event in display.poll_events():
            if event.type == EventType.QUIT:
                return False

            if (
                event.type == EventType.KEY_DOWN
                and event.key == Key.ESCAPE
            ):
                return False

        display.put_image_to_window(
            image=frame,
            x=0,
            y=0,
        )

        display.present()

        return True

    try:
        display.start_loop(run_frame)
    finally:
        display.quit()


if __name__ == "__main__":
    main()
