class MlxImage:
    def __init__(
        self: "MlxImage",
        img_ptr: object,
        data: memoryview,
        bits_per_pixel: int,
        size_line: int,
        image_format: int,
        width: int,
        height: int,
    ) -> None:
        self._img_ptr = img_ptr
        self._data = self._as_byte_view(data)
        self._bits_per_pixel = bits_per_pixel
        self._size_line = size_line
        self._image_format = image_format
        self._width = width
        self._height = height

        self._opaque_runs: list[list[tuple[int, int]]] | None = None
        if self._bits_per_pixel != 32:
            raise ValueError(
                "Only 32 bits per pixel MLX images are supported")

    @property
    def img_ptr(self: "MlxImage") -> object:
        return self._img_ptr

    @property
    def width(self: "MlxImage") -> int:
        return self._width

    @property
    def height(self: "MlxImage") -> int:
        return self._height

    @property
    def bytes_per_pixel(self: "MlxImage") -> int:
        return self._bits_per_pixel // 8

    @property
    def alpha_offset(self: "MlxImage") -> int:
        if self._image_format == 0:
            return 3

        if self._image_format == 1:
            return 0

        raise ValueError(
            f"Unsupported MLX image format {self._image_format}"
        )

    def set_at(
        self: "MlxImage",
        position: tuple[int, int],
        color: tuple[int, int, int],
        alpha: int = 255,
    ) -> None:
        x, y = position

        if not self._is_inside(x, y):
            return

        offset = self._get_offset(x, y)

        pixel = self._color_to_bytes(color, alpha)

        self._data[offset:offset + self.bytes_per_pixel] = pixel

        self._opaque_runs = None

    def get_at(
        self: "MlxImage",
        x: int,
        y: int,
    ) -> tuple[int, int, int]:
        red, green, blue, _ = (
            self.get_rgba(x, y)
        )

        return red, green, blue

    def get_rgba(
        self: "MlxImage",
        x: int,
        y: int,
    ) -> tuple[int, int, int, int]:
        if not self._is_inside(x, y):
            return 0, 0, 0, 0

        offset = self._get_offset(x, y)

        if self._image_format == 0:
            blue = self._data[offset]
            green = self._data[offset + 1]
            red = self._data[offset + 2]
            alpha = self._data[offset + 3]

        elif self._image_format == 1:
            alpha = self._data[offset]
            red = self._data[offset + 1]
            green = self._data[offset + 2]
            blue = self._data[offset + 3]

        else:
            raise ValueError(
                f"Unsupported MLX image format: {self._image_format}"
            )
        return red, green, blue, alpha

    def blit(
        self: "MlxImage",
        source: "MlxImage",
        position: tuple[int, int],
    ) -> None:
        target_x, target_y = position

        if (self.bytes_per_pixel == source.bytes_per_pixel and
           self._image_format == source._image_format):
            self._fast_blit(
                source,
                target_x,
                target_y,
            )
            return
        self._slow_blit(
            source,
            target_x,
            target_y
        )

    def fill(
        self: "MlxImage",
        color: tuple[int, int, int],
        alpha: int = 255,
    ) -> None:
        pixel = self._color_to_bytes(color, alpha)
        row = pixel * self._width

        for y in range(self._height):
            offset = y * self._size_line
            self._data[offset:offset + len(row)] = row

        self._opaque_runs = None

    def _is_inside(self: "MlxImage", x: int, y: int) -> bool:
        return 0 <= x < self._width and 0 <= y < self._height

    def _get_offset(self: "MlxImage", x: int, y: int) -> int:
        return y * self._size_line + x * self.bytes_per_pixel

    def _as_byte_view(self: "MlxImage", data: memoryview) -> memoryview:
        if data.format == "B":
            return data

        return data.cast("B")

    def _color_to_bytes(
        self: "MlxImage",
        color: tuple[int, int, int],
        alpha: int = 255,
    ) -> bytes:
        red, green, blue = color

        if not 0 <= alpha <= 255:
            raise ValueError("Alpha must be between 0 and 255")

        if self._image_format == 0:
            return bytes((blue, green, red, alpha))

        if self._image_format == 1:
            return bytes((alpha, red, green, blue))

        raise ValueError(
            f"Unsupported MLX image format: {self._image_format}")

    def _fast_blit(
        self: "MlxImage",
        source: "MlxImage",
        target_x: int,
        target_y: int,
    ) -> None:
        bytes_per_pixel = self.bytes_per_pixel

        opaque_runs = source._get_opaque_runs()

        for source_y, runs in enumerate(opaque_runs):
            destination_y = target_y + source_y

            if destination_y < 0 or destination_y >= self.height:
                continue

            for run_start, run_end in runs:
                destination_start = target_x + run_start
                destination_end = target_x + run_end
                source_start = run_start
                source_end = run_end

                if destination_start < 0:
                    clipped = -destination_start

                    source_start += clipped
                    destination_start = 0

                if destination_end > self.width:
                    clipped = destination_end - self.width

                    source_end -= clipped
                    destination_end = self.width

                if source_start >= source_end:
                    continue

                source_offset = (source_y * source._size_line +
                                 source_start * bytes_per_pixel)

                destination_offset = (destination_y * self._size_line +
                                      destination_start * bytes_per_pixel)

                bytes_count = (source_end - source_start) * bytes_per_pixel

                self._data[destination_offset:
                           destination_offset + bytes_count] = source._data[
                               source_offset:
                               source_offset + bytes_count
                           ]
        self._opaque_runs = None

    def _slow_blit(
        self: "MlxImage",
        source: "MlxImage",
        target_x: int,
        target_y: int,
    ) -> None:
        for source_y in range(source.height):
            for source_x in range(source.width):
                destination_x = target_x + source_x
                destination_y = target_y + source_y

                if not self._is_inside(destination_x, destination_y):
                    continue

                red, green, blue, alpha = source.get_rgba(source_x, source_y)

                if alpha == 0:
                    continue

                self.set_at(
                    position=(destination_x, destination_y),
                    color=(red, green, blue),
                    alpha=255,
                )

    def _build_opaque_runs(
        self: "MlxImage",
    ) -> list[list[tuple[int, int]]]:
        rows: list[list[tuple[int, int]]] = []

        bytes_per_pixel = self.bytes_per_pixel
        alpha_offset = self.alpha_offset

        for y in range(self._height):
            runs: list[tuple[int, int]] = []

            run_start: int | None = None
            row_offset = y * self._size_line

            for x in range(self._width):
                pixel_offset = row_offset + x * bytes_per_pixel

                alpha = self._data[pixel_offset + alpha_offset]

                opaque = alpha != 0

                if opaque and run_start is None:
                    run_start = x

                elif not opaque and run_start is not None:
                    runs.append((run_start, x))
                    run_start = None

            if run_start is not None:
                runs.append((run_start, self._width))

            rows.append(runs)

        return rows

    def _get_opaque_runs(
        self: "MlxImage",
    ) -> list[list[tuple[int, int]]]:
        if self._opaque_runs is None:
            self._opaque_runs = self._build_opaque_runs()
        return self._opaque_runs
