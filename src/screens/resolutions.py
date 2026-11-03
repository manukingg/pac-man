SUPPORTED_WINDOW_RESOLUTIONS: list[tuple[int, int]] = [
    (3840, 2022),
    (1920, 1200),
    (1920, 1080),
    (1680, 1050),
    (1600, 1200),
    (1440, 900),
    (1280, 1024),
    (1280, 720),
    (1024, 768),
    (800, 600),
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


def get_available_resolutions(
    desktop_width: int,
    desktop_height: int,
) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []

    for width, height in SUPPORTED_WINDOW_RESOLUTIONS:
        if width <= desktop_width and height <= desktop_height:
            result.append((width, height))

    if not result:
        result.append((800, 600))

    return result


def get_available_resolution_options(
    desktop_width: int,
    desktop_height: int,
) -> list[str]:
    return [
        resolution_to_text(width, height)
        for width, height in get_available_resolutions(
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
