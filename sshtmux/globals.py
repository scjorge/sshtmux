from pathlib import Path

SSHTMUX_BASEDIR = Path(Path.home(), ".config", "sshtmux")
TMUX_CONFIG_FILE = Path(SSHTMUX_BASEDIR, "tmux.config")
USER_SSH_CONFIG = Path(Path.home(), ".ssh", "config")
SSHTMUX_BASEDIR.mkdir(parents=True, exist_ok=True)
DEFAULT_HOST_STYLE = "panels"
ENABLED_HOST_STYLES = ["panels", "card", "simple", "table", "table2", "json"]
