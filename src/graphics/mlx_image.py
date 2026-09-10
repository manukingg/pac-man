class MlxImage:
    def __init__(
        self: "MlxImage",
        img_ptr: int,
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

        if self._bits_per_pixel != 32:
            raise ValueError("Only 32 bits per pixel MLX images are supported")

    @property
    def img_ptr(self: "MlxImage") -> int:
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

    def fill(
        self: "MlxImage",
        color: tuple[int, int, int],
    ) -> None:
        pixel = self._color_to_bytes(color)
        row = pixel * self._width

        for y in range(self._height):
            offset = y * self._size_line
            self._data[offset:offset + len(row)] = row

    def set_at(
        self: "MlxImage",
        position: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        x, y = position

        if not self._is_inside(x, y):
            return

        offset = self._get_offset(x, y)
        pixel = self._color_to_bytes(color)

        self._data[offset:offset + self.bytes_per_pixel] = pixel

    def get_at(
        self: "MlxImage",
        x: int,
        y: int,
    ) -> tuple[int, int, int]:
        if not self._is_inside(x, y):
            return 0, 0, 0

        offset = self._get_offset(x, y)

        if self._image_format == 0:
            blue = self._data[offset]
            green = self._data[offset + 1]
            red = self._data[offset + 2]
            return red, green, blue

        if self._image_format == 1:
            red = self._data[offset + 1]
            green = self._data[offset + 2]
            blue = self._data[offset + 3]
            return red, green, blue

        return 0, 0, 0

    def blit(
        self: "MlxImage",
        source: "MlxImage",
        position: tuple[int, int],
    ) -> None:
        target_x, target_y = position

        if (
            self._bits_per_pixel == source._bits_per_pixel
            and self._image_format == source._image_format
        ):
            self._fast_blit(source, target_x, target_y)
            return

        self._slow_blit(source, target_x, target_y)

    def _fast_blit(
        self: "MlxImage",
        source: "MlxImage",
        position: tuple[int, int],
        target_x: int,
        target_y: int,
    ) -> None:
        bytes_per_pixel = self.bytes_per_pixel

        for source_y in range(source.height):
            destination_y = target_y + source_y

            if destination_y < 0 or destination_y >= self._height:
                continue

            source_x = 0
            destination_x = target_x
            copy_width = source.width

            if destination_x < 0:
                source_x = -destination_x
                copy_width -= source_x
                destination_x = 0

            if destination_x + copy_width > self.width:
                copy_width = self.width - destination_x

            if copy_width <= 0:
                continue

            source_offset = (
                source_y * self._size_line
                + destination_x * bytes_per_pixel
            )
            destination_offset = (
                destination_y * self._size_line
                + destination_x * bytes_per_pixel
            )
            bytes_count = copy_width * bytes_per_pixel

            self._data[
                destination_offset:destination_offset + bytes_count
            ] = source._data[source_offset:source_offset + bytes_count]

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

                self.set_at(
                    position=(destination_x, destination_y),
                    color=source.get_at(source_x, source_y)
                )

    def _get_offset(self: "MlxImage", x: int, y: int) -> int:
        return y * self._size_line + x * self.bytes_per_pixel

    def _is_inside(self: "MlxImage", x: int, y: int) -> bool:
        return 0 <= x < self._width and 0 <= y <= self._height

    def _color_to_bytes(
        self: "MlxImage",
        color: tuple[int, int, int],
    ) -> bytes:
        red, green, blue = color

        if self._image_format == 0:
            return bytes((blue, green, red, 0))

        if self._image_format == 1:
            return bytes((0, red, green, blue))

        return bytes((blue, green, red, 0))

    def _as_byte_view(self: "MlxImage", data: memoryview) -> memoryview:
        if data.format == "B":
            return data

        return data.cast("B")
