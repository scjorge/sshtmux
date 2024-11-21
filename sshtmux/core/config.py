from pathlib import Path
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings

USER_DIR = Path.home()
SSHTMUX_BASEDIR = USER_DIR / ".config" / "sshtmux"
T_Host_Style = Literal["panels", "card", "simple", "table", "table2", "json"]
FAST_CONNECTIONS_GROUP_NAME = "fast-connections"
FAST_SESSIONS_NAME = "fast-session"
SFTP_CLI = "sftp"
MULTICOMMNAD_CLI = "multi_command"


class Base(BaseSettings):
    class Config:
        extra = "allow"
        env_file = ".env"


class InternalConfig(BaseModel):
    BASE_DIR: str = str(SSHTMUX_BASEDIR)
    BASE_SERVICE: str = "sshtmux"
    TOML_CONFIG_FILE: str = str(SSHTMUX_BASEDIR / "config.toml")


class SSHTMUX(Base):
    SSHTMUX_IDENTITY_KEY: str | None = None
    SSHTMUX_IDENTITY_KEY_FILE: str | None = str(SSHTMUX_BASEDIR / "identity.key")
    SSHTMUX_IDENTITY_PASSWORDS_FILE: str | None = str(SSHTMUX_BASEDIR / "identity.json")
    SSHTMUX_SNIPPETS_PATH: str | None = str(SSHTMUX_BASEDIR / "snippets")
    SSHTMUX_HOST_STYLE: T_Host_Style = "panels"


class TMUX(Base):
    TMUX_CONFIG_FILE: str = str(SSHTMUX_BASEDIR / "tmux.config")
    TMUX_SOCKET_NAME: str | None = f"sshtmux_{USER_DIR.name}"
    TMUX_SOCKET_PATH: str | None = None
    TMUX_TIMEOUT_COMMANDS: int = 10


class SSH(Base):
    SSH_CONFIG_FILE: str = str(USER_DIR / ".ssh" / "config")
    SSH_COMMAND: str = (
        "ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no ${hostname}"
    )
    SFTP_COMMAND: str = (
        "sftp -o ConnectTimeout=10 -o StrictHostKeyChecking=no ${hostname}"
    )
    SSH_CUSTOM_COMMAND: str | bool = False


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
