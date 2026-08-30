resolutions: dict = {
    "3840 x 2022 (16:9)": {
        "name_font": 32,
        "buttons_font": 16,
        "next_button_start": 800,
        "name_top_gap": 200,
        "gap_between_buttons": 200,
        "dropdown_font_size": 10,
        "dropdown_options_font_size": 8,
        },
    "1920 x 1200 (16:9)": {
        "name_font": 18,
        "buttons_font": 9,
        "next_button_start": 500,
        "name_top_gap": 100,
        "gap_between_buttons": 100,
        "dropdown_font_size": 6,
        "dropdown_options_font_size": 4,
        },
    "1920 x 1080 (16:9)": {
        "name_font": 20,
        "buttons_font": 9,
        "next_button_start": 450,
        "name_top_gap": 100,
        "gap_between_buttons": 100,
        "dropdown_font_size": 6,
        "dropdown_options_font_size": 4,
        },
    "1680 x 1050 (16:9)": {
        "name_font": 16,
        "buttons_font": 8,
        "next_button_start": 400,
        "name_top_gap": 100,
        "gap_between_buttons": 100,
        "dropdown_font_size": 5,
        "dropdown_options_font_size": 3,
        },
    "1600 x 1200 (4:3)": {
        "name_font": 18,
        "buttons_font": 9,
        "next_button_start": 500,
        "name_top_gap": 100,
        "gap_between_buttons": 100,
        "dropdown_font_size": 5,
        "dropdown_options_font_size": 3,
        },
    "1440 x 900 (16:10)": {
        "name_font": 14,
        "buttons_font": 7,
        "next_button_start": 320,
        "name_top_gap": 80,
        "gap_between_buttons": 90,
        "dropdown_font_size": 4,
        "dropdown_options_font_size": 3,
    },
    "1280 x 1024 (5:4)": {
        "name_font": 14,
        "buttons_font": 7,
        "next_button_start": 400,
        "name_top_gap": 80,
        "gap_between_buttons": 90,
        "dropdown_font_size": 4,
        "dropdown_options_font_size": 3,
    },
    "1280 x 720 (16:9)": {
        "name_font": 12,
        "buttons_font": 5,
        "next_button_start": 300,
        "name_top_gap": 70,
        "gap_between_buttons": 70,
        "dropdown_font_size": 3,
        "dropdown_options_font_size": 2,
        },
    "1024 x 768 (4:3)": {
        "name_font": 12,
        "buttons_font": 5,
        "next_button_start": 300,
        "name_top_gap": 70,
        "gap_between_buttons": 70,
        "dropdown_font_size": 3,
        "dropdown_options_font_size": 2,
    },
    "800 x 600 (4:3)": {
        "name_font": 10,
        "buttons_font": 4,
        "next_button_start": 250,
        "name_top_gap": 60,
        "gap_between_buttons": 50,
        "dropdown_font_size": 3,
        "dropdown_options_font_size": 2,
    },
}

settings_resolutions: dict = {
    (3840, 2022): "3840 x 2022 (16:9)",
    (1920, 1200): "1920 x 1200 (16:9)",
    (1920, 1080): "1920 x 1080 (16:9)",
    (1680, 1050): "1680 x 1050 (16:9)",
    (1600, 1200): "1600 x 1200 (4:3)",
    (1440, 900): "1440 x 900 (16:10)",
    (1280, 1024): "1280 x 1024 (5:4)",
    (1280, 720): "1280 x 720 (16:9)",
    (1024, 768): "1024 x 768 (4:3)",
    (800, 600): "800 x 600 (4:3)",
}

SUPPORTED_WINDOW_RESOLUTIONS: list[tuple[int, int]] = [
    (800, 600),
    (1024, 768),
    (1280, 720),
    (1280, 1024),
    (1440, 900),
    (1600, 1200),
    (1680, 1050),
    (1920, 1080),
    (1920, 1200),
    (3840, 2022),
]


def resolution_to_text(width: int, height: int) -> str:
    return f"{width}x{height}"


def parse_resolution_text(value: str) -> tuple[int, int] | None:
    parts = value.lower().split("x")
    if len(parts) != 2:
        return None

    try:
        width = int(parts[0])
        height = int(parts[1].split()[0])
    except ValueError:
        return None

    if width <= 0 or height <= 0:
        return None

    return width, height


def get_available_resolution(
    desktop_width: int,
    desktop_height: int,
) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []

    for width, height in SUPPORTED_WINDOW_RESOLUTIONS:
        if width <= desktop_width and height <= desktop_height:
            result.append(f"{width}x{height}")

    if not result:
        result.append((800, 600))

    return result


def get_available_resolution_options(
    desktop_width: int,
    desktop_height: int,
) -> list[str]:
    return [
        resolution_to_text(width, height)
        for width, height in get_available_resolution(
            desktop_width=desktop_width,
            desktop_height=desktop_height,
        )
    ]


def get_nearest_available_resolution(
    requested_width: int,
    requested_height: int,
    available_resolutions: list[tuple[int, int]],
) -> tuple[int, int]:
    if not available_resolutions:
        return 800, 600

    return min(
        available_resolutions,
        key=lambda size: (
            abs(size[0] - requested_width)
            + abs(size[1] - requested_height)
        ),
    )
