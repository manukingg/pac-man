from .image import Image


def get_text_width(text: str, font_size: int) -> int:
    if not text:
        return 0

    return (len(text) * 5 + (len(text) - 1)) * font_size


def get_aligned_position(
    align: tuple[str | int | float],
    text: str,
    font_size: int,
    image: Image
) -> tuple[int]:
    allowed_alignes_x = ("left", "center", "right")
    allowed_alignes_y = ("top", "center", "bottom")
    align_x, align_y = align
    sized_text_width = (5 * font_size * len(text) +
                        (len(text) - 1) * font_size)
    sized_text_height = 8 * font_size
    result_x = 0
    result_y = 0

    if isinstance(align_x, str):
        if align_x.lower() not in allowed_alignes_x:
            raise KeyError("X-align unknown."
                           "Supported types: left | center | right")
        if align_x.lower() == "left":
            result_x = font_size
        elif align_x.lower() == "center":
            result_x = (image.width - sized_text_width) // 2
        elif align_x.lower() == "right":
            result_x = image.width - font_size - sized_text_width
    elif isinstance(align_x, int):
        result_x = align_x
    elif isinstance(align_x, float):
        result_x = round((image.width - sized_text_width) * align_x)
    else:
        raise Exception("Unknown type for X-align")
    if isinstance(align_y, str):
        if align_y.lower() not in allowed_alignes_y:
            raise KeyError("Y-align unknown"
                           "Supported types: top | center | bottom")
        if align_y.lower() == "top":
            result_y = font_size
        elif align_y.lower() == "center":
            result_y = (image.height - sized_text_height) // 2
        elif align_y.lower() == "bottom":
            result_y = image.height - font_size - sized_text_height
    elif isinstance(align_y, int):
        result_y = align_y
    elif isinstance(align_y, float):
        result_y = round((image.height - sized_text_height) * align_y)
    else:
        raise Exception("Unknown type for Y-align")
    if result_x < 0:
        result_x = font_size
    elif result_x > image.width:
        result_x = image.width - sized_text_width - font_size
    if result_y < 0:
        result_y = font_size
    elif result_y > image.height:
        result_y = image.height - sized_text_height - font_size
    return result_x, result_y
