from pathlib import Path

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings

USER_DIR = Path.home()
SSHTMUX_BASEDIR = str(Path(USER_DIR, ".config", "sshtmux"))


class Base(BaseSettings):
    class Config:
        extra = "allow"
        env_file = ".env"


class InternalConfig(BaseModel):
    BASE_DIR: str = SSHTMUX_BASEDIR
    TOML_CONFIG_FILE: str = str(Path(SSHTMUX_BASEDIR, "config.toml"))


class SSHTMUX(Base):
    SSHTMUX_IDENTITY_FILE: str | None = ""
    SSHTMUX_IDENTITY_KEY: str | SecretStr | None = None


class TMUX(Base):
    TMUX_CONFIG_FILE: str = str(Path(SSHTMUX_BASEDIR, "tmux.config"))
    TMUX_SOCKET_NAME: str | None = f"{USER_DIR.name}_sshmm"
    TMUX_SOCKET_PATH: str | None = str(Path(SSHTMUX_BASEDIR, ".tmux.sock"))
    TMUX_TIMEOUT_COMMANDS: int = 10


class SSH(Base):
    SSH_CONFIG_FILE: str = str(Path(USER_DIR, ".ssh", "config"))


class ConfigModel(Base):
    internal_config: InternalConfig = InternalConfig()
    sshtmux: SSHTMUX = SSHTMUX()
    tmux: TMUX = TMUX()
    ssh: SSH = SSH()


settings = ConfigModel()


def update_settings(new_settings):
    global settings
    settings = new_settings
