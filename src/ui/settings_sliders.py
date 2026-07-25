from dataclasses import dataclass


@dataclass
class SettingsSlider:
    current_index: int
    options: list[str]
