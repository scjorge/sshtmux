from .globals import TMUX_CONFIG_FILE

if not TMUX_CONFIG_FILE.exists():
    configs = ["set -g mouse on"]
    with open(TMUX_CONFIG_FILE, "a+t") as file:
        for config in configs:
            file.write(config + "\n")
