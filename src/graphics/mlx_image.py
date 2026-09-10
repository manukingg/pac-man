from .image import Image


class MlxImage(Image):
    def __init__(
        self: "MlxImage",
        ptr,
        data: memoryview,
        width: int,
        height: int,
        bits_per_pixel: int,
        size_line: int,
        image_format: int,
    ) -> None:
        self._ptr = ptr
        self._data = data
        self._width = width
        self._height = height
        self._bits_per_pixel = bits_per_pixel
        self._size_line = size_line
        self._image_format = image_format
        self._opaque_runs: (
            tuple[tuple[tuple[int, int], ...], ...]
            | None
        ) = None

    @property
    def ptr(self):
        return self._ptr

    @property
    def width(self: "MlxImage") -> int:
        return self._width

    @property
    def height(self: "MlxImage") -> int:
        return self._height

    @property
    def size_line(self: "MlxImage") -> int:
        return self._size_line

    @property
    def image_format(self: "MlxImage") -> int:
        return self._image_format

    def _build_opaque_runs(
        self: "MlxImage",
    ) -> tuple[
        tuple[tuple[int, int], ...],
        ...
    ]:
        rows: list[
            tuple[tuple[int, int], ...]
        ] = []

        for y in range(self._height):
            runs: list[tuple[int, int]] = []
            start: int | None = None

            for x in range(self._width):
                _, _, _, alpha = self.get_rgba(
                    x,
                    y,
                )

                if alpha != 0:
                    if start is None:
                        start = x

                elif start is not None:
                    runs.append(
                        (
                            start,
                            x,
                        )
                    )

                    start = None

            if start is not None:
                runs.append(
                    (
                        start,
                        self._width,
                    )
                )

            rows.append(
                tuple(runs)
            )

        return tuple(rows)


    def blit_to(
        self: "MlxImage",
        target: "MlxImage",
        x: int,
        y: int,
    ) -> None:
        if (
            self._image_format
            != target._image_format
        ):
            raise ValueError(
                "Image formats do not match"
            )

        if self._opaque_runs is None:
            self._opaque_runs = (
                self._build_opaque_runs()
            )

        for source_y, runs in enumerate(
            self._opaque_runs
        ):
            target_y = y + source_y

            if not (
                0 <= target_y < target.height
            ):
                continue

            for start_x, end_x in runs:
                source_start_x = max(
                    start_x,
                    -x,
                )

                source_end_x = min(
                    end_x,
                    target.width - x,
                )

                if (
                    source_start_x
                    >= source_end_x
                ):
                    continue

                target_x = (
                    x + source_start_x
                )

                byte_count = (
                    source_end_x
                    - source_start_x
                ) * 4

                source_offset = (
                    source_y
                    * self._size_line
                    + source_start_x * 4
                )

                target_offset = (
                    target_y
                    * target._size_line
                    + target_x * 4
                )

                target._data[
                    target_offset:
                    target_offset + byte_count
                ] = self._data[
                    source_offset:
                    source_offset + byte_count
                ]

    def _get_pixel_bytes(
        self: "MlxImage",
        color: tuple[int, int, int, int],
    ) -> bytes:
        red, green, blue, alpha = color

        if self._image_format == 0:
            return bytes(
                (
                    blue,
                    green,
                    red,
                    alpha,
                )
            )

        return bytes(
            (
                alpha,
                red,
                green,
                blue,
            )
        )

    def fill(
        self: "MlxImage",
        color: tuple[int, int, int, int],
    ) -> None:
        pixel = self._get_pixel_bytes(color)

        row = pixel * self._width

        for y in range(self._height):
            offset = y * self._size_line

            self._data[
                offset:offset + self._width * 4
            ] = row

    def fill_rect(
        self: "MlxImage",
        x: int,
        y: int,
        width: int,
        height: int,
        color: tuple[int, int, int, int],
    ) -> None:
        start_x = max(0, x)
        start_y = max(0, y)

        end_x = min(
            self._width,
            x + width,
        )

        end_y = min(
            self._height,
            y + height,
        )

        if start_x >= end_x or start_y >= end_y:
            return

        pixel = self._get_pixel_bytes(color)

        row_width = end_x - start_x
        row = pixel * row_width

        for current_y in range(start_y, end_y):
            offset = (
                current_y * self._size_line
                + start_x * 4
            )

            self._data[
                offset:offset + row_width * 4
            ] = row

    def get_rgba(
        self: "MlxImage",
        x: int,
        y: int,
    ) -> tuple[int, int, int, int]:
        offset = (
            y * self._size_line
            + x * 4
        )

        if self._image_format == 0:
            blue = self._data[offset]
            green = self._data[offset + 1]
            red = self._data[offset + 2]
            alpha = self._data[offset + 3]

            return (
                red,
                green,
                blue,
                alpha,
            )

        alpha = self._data[offset]
        red = self._data[offset + 1]
        green = self._data[offset + 2]
        blue = self._data[offset + 3]

        return (
            red,
            green,
            blue,
            alpha,
        )

    def set_rgba(
        self: "MlxImage",
        x: int,
        y: int,
        color: tuple[int, int, int, int],
    ) -> None:
        offset = (
            y * self._size_line
            + x * 4
        )

        red, green, blue, alpha = color

        if self._image_format == 0:
            self._data[offset] = blue
            self._data[offset + 1] = green
            self._data[offset + 2] = red
            self._data[offset + 3] = alpha
            return

        self._data[offset] = alpha
        self._data[offset + 1] = red
        self._data[offset + 2] = green
        self._data[offset + 3] = blue

    def get_at(
        self: "MlxImage",
        x: int,
        y: int,
    ) -> tuple[int, int, int]:
        red, green, blue, _ = self.get_rgba(
            x,
            y,
        )

        return red, green, blue