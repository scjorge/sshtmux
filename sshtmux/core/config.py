from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings

USER_DIR = Path.home()
SSHTMUX_BASEDIR = USER_DIR / ".config" / "sshtmux"


class Base(BaseSettings):
    class Config:
        extra = "allow"
        env_file = ".env"


class InternalConfig(BaseModel):
    BASE_DIR: str = str(SSHTMUX_BASEDIR)
    TOML_CONFIG_FILE: str = str(SSHTMUX_BASEDIR / "config.toml")


class SSHTMUX(Base):
    SSHTMUX_IDENTITY_KEY: str | None = None
    SSHTMUX_IDENTITY_FILE: str | None = str(SSHTMUX_BASEDIR / "identity.key")
    SSHTMUX_IDENTITY_PASSWORDS_FILE: str | None = str(SSHTMUX_BASEDIR / "identity.json")


class TMUX(Base):
    TMUX_CONFIG_FILE: str = str(SSHTMUX_BASEDIR / "tmux.config")
    TMUX_SOCKET_NAME: str | None = f"sshtmux_{USER_DIR.name}"
    TMUX_SOCKET_PATH: str | None = None
    TMUX_TIMEOUT_COMMANDS: int = 10


class SSH(Base):
    SSH_CONFIG_FILE: str = str(USER_DIR / ".ssh" / "config")


class ConfigModel(BaseModel):
    internal_config: InternalConfig = InternalConfig()
    sshtmux: SSHTMUX = SSHTMUX()
    ssh: SSH = SSH()
    tmux: TMUX = TMUX()


def update_settings(new_settings):
    global settings
    settings = new_settings


try:
    settings = ConfigModel()
except Exception as e:
    print(f"Init Settings Failed: {e}")
    exit(1)
