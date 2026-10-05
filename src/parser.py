import json
from pathlib import Path
from typing import Any

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

        if not isinstance(raw_config, dict):
            print("Config root must be a JSON object.")
            print("Using default config")
            return Config()

        return self._validate_with_field_defaults(raw_config)

    def _read_json_with_comments(self: "Parser") -> str:
        parsed_lines: list[str] = []

        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                stripped = line.strip()

                if stripped.startswith("#"):
                    continue

                parsed_lines.append(line)

        return "".join(parsed_lines)

    def _validate_with_field_defaults(
        self: "Parser",
        raw_config: dict[str, Any],
    ) -> Config:
        try:
            return Config.model_validate(raw_config)

        except ValidationError as error:
            defaults = Config()
            default_data = defaults.model_dump()
            fixed_config = dict(raw_config)

            invalid_fields = self._get_invalid_top_level_fields(error)

            for field_name in invalid_fields:
                fixed_config[field_name] = default_data[field_name]
                print(
                    f"Invalig config value for '{field_name}'."
                    f"Using default {default_data[field_name]!r}"
                )
            try:
                return Config.model_validate(fixed_config)

            except ValidationError as second_error:
                print("Config is still invalid after field fallback")
                print(second_error)
                print("Using full default config.")
                return defaults

    def _get_invalid_top_level_fields(
        self: "Parser",
        error: ValidationError,
    ) -> set[str]:
        invalid_fields: set[str] = set()

        for item in error.errors():
            location = item.get("loc", ())

            if not location:
                continue

            field_name = str(location[0])

            if field_name in Config.model_fields:
                invalid_fields.add(field_name)

        return invalid_fields
