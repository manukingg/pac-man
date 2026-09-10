from src.graphics.mlx_wrapper import MlxWrapper


ESC_KEY = 65307


def on_key(keycode: int, display: MlxWrapper) -> int:
    if keycode == ESC_KEY:
        display._mlx.mlx_loop_exit(display._mlx_ptr)

    return 0


def main() -> None:
    display = MlxWrapper(
        width=800,
        height=600,
        title="MLX Image Test",
    )

    frame = display.new_image(800, 600)
    display.clear(frame, (0, 0, 0))

    for y in range(100, 300):
        for x in range(100, 300):
            display.put_pixel(frame, x, y, (255, 255, 0))

    display.put_image_to_window(frame, 0, 0)
    display.present()

    display._mlx.mlx_key_hook(display._window, on_key, display)
    display._mlx.mlx_loop(display._mlx_ptr)


if __name__ == "__main__":
    main()
