from pathlib import Path
from pprint import pprint

import toml
from pydantic import ValidationError

from .core.config import ConfigModel, settings, update_settings
from .tools.messages import CONFIG_VALIDATION_ERROR

Path(settings.internal_config.BASE_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.sshtmux.SSHTMUX_SNIPPETS_PATH).mkdir(parents=True, exist_ok=True)


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
    if Path(settings.tmux.TMUX_CONFIG_FILE).exists():
        return

    tmux_config = """
    # Mouse
    set -g mouse on
    set-option -g set-clipboard on

    # Copy Selection to clipboard
    if-shell '[ "$XDG_SESSION_TYPE" = "x11" ]' 'bind-key -T copy-mode MouseDragEnd1Pane send-keys -X copy-pipe "xclip -selection clipboard -i" \\; send-keys C-c'
    if-shell '[ "$XDG_SESSION_TYPE" = "wayland" ]' 'bind-key -T copy-mode MouseDragEnd1Pane send-keys -X copy-pipe "wl-copy" \\; send-keys C-c'

    # Paste Selection
    if-shell '[ "$XDG_SESSION_TYPE" = "x11" ]' 'bind-key -n MouseDown3Pane run-shell "xclip -selection clipboard -o | tmux load-buffer - && tmux paste-buffer"'
    if-shell '[ "$XDG_SESSION_TYPE" = "wayland" ]' 'bind-key -n MouseDown3Pane run-shell "wl-paste -n | tmux load-buffer - && tmux paste-buffer"'

    # Key Binds
    bind-key S run-shell "tmux split-window -v -c '#{pane_current_path}' 'sshm snippets run -s '#{session_name}' -w '#{window_index}' -p '#{pane_index}' '"
    bind-key -n MouseDown1StatusLeft run-shell "tmux choose-window"

    # Status Bar
    set -g status-interval 2
    set -g status-bg colour235
    set -g status-fg white
    set -g status-style bold
    set -g status-left-length 100
    set -g status-right-length 100
    set -g status-left '#[fg=white,bg=colour235,bold] 💻 #S #[default]'
    set -g status-right '#[fg=white]📅 %a %d/%b #[fg=white]🕒 %H:%M #[default]'

    # Windows
    set -g window-status-current-style bg=colour33,fg=white,bold
    set -g window-status-current-format '#[fg=white,bold] 🔵 #I:#W'
    set -g window-status-style bg=colour235,fg=colour250
    set -g window-status-format '#[fg=colour250] ● #I:#W'

    # Panes
    set -g pane-active-border-style fg=colour45
    set -g pane-border-style fg=colour235
    """

    with open(settings.tmux.TMUX_CONFIG_FILE, "a+t") as file:
        file.write(tmux_config)


init_toml_config()
init_tmux()
