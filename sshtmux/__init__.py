from pathlib import Path
from pprint import pprint

import toml
from pydantic import ValidationError

from .core.config import ConfigModel, settings, update_settings
from .tools.messages import CONFIG_VALIDATION_ERROR

Path(settings.internal_config.BASE_DIR).mkdir(parents=True, exist_ok=True)


def init_toml_config():
    toml_file = settings.internal_config.TOML_CONFIG_FILE

    if Path(toml_file).exists():
        with open(toml_file, "r+t") as file:
            toml_dict = toml.load(file)
            try:
                if toml_dict.get("internal_config"):
                    del toml_dict["internal_config"]
                load_settings = ConfigModel(**toml_dict)
                update_settings(load_settings)
            except ValidationError as e:
                print(CONFIG_VALIDATION_ERROR)
                pprint(e.json(), indent=4)
                return

    if not Path(toml_file).exists():
        with open(toml_file, "w+t") as file:
            toml_settings = settings.model_dump()
            if toml_settings.get("internal_config"):
                del toml_settings["internal_config"]
            toml.dump(toml_settings, file)


def init_tmux():
    if not Path(settings.tmux.TMUX_CONFIG_FILE).exists():
        tmux_configs = [
            "set -g mouse on",
        ]

        with open(settings.tmux.TMUX_CONFIG_FILE, "a+t") as file:
            for config in tmux_configs:
                file.write(config + "\n")


init_toml_config()
init_tmux()
