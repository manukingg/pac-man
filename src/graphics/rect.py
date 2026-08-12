from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    def contains(self: "Rect", pos: tuple[int, int]) -> bool:
        px, py = pos
        print(pos)
        return (
            self.x <= px <= self.x + self.width
            and self.y <= py <= self.y + self.height
        )

    def inflate(self: "Rect", padding_x: int, padding_y: int) -> "Rect":
        return Rect(
            x=self.x - padding_x,
            y=self.y - padding_y,
            width=self.width + padding_x * 2,
            height=self.height + padding_y * 2,
        )
