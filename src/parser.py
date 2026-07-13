import json
from pathlib import Path

from pydantic import ValidationError

from src.models.config_model import Config


class Parser:
    def __init__(self: "Parser", path: Path | str) -> None:
        self.path = Path(path)

    def parse(self: "Parser") -> Config:
        if self.path.suffix != ".json":
            print(
                f"Invalid config extension: {self.path}. "
                "Expected a .json file. Using default config."
            )
            return Config()

        try:
            json_text = self._read_json_with_comments()
            raw_config = json.loads(json_text)
            return Config.model_validate(raw_config)

        except FileNotFoundError:
            print(f"No config file found by path: {self.path}")
            print("Using default config.")
            return Config()

        except json.JSONDecodeError as error:
            print(f"Invalid JSON config: {error}")
            print("Using default config.")
            return Config()

        except ValidationError as error:
            print(f"Invalid config values: {error}")
            print("Using default config.")
            return Config()

        except OSError as error:
            print(f"Could not read config file: {error}")
            print("Using default config.")
            return Config()

    def _read_json_with_comments(self: "Parser") -> str:
        parsed_lines: list[str] = []

        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                stripped = line.strip()

                if stripped.startswith("#"):
                    continue

                parsed_lines.append(line)

        return "".join(parsed_lines)
