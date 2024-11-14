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
    # Base
    set -g default-terminal "screen-256color"
    set -g visual-activity on
    set-option -g aggressive-resize on

    # Window
    set -g set-titles on
    set-option -g renumber-windows on
    set -g history-limit 100000
    set -g base-index 1
    setw -g pane-base-index 1
    bind '"' split-window -v -c "#{pane_current_path}"
    bind % split-window -h -c "#{pane_current_path}"
    bind-key -n MouseDown1StatusLeft choose-window

    # Mouse
    set -g mouse on
    set-option -g set-clipboard on

    # SSHTMUX Key Binds
    bind-key S run-shell "tmux split-window -h -c '#{pane_current_path}' 'sshm snippets run -s '#{session_name}' -w '#{window_index}' -p '#{pane_index}' '"
    bind-key I run-shell "tmux split-window -h -c '#{pane_current_path}' 'sshm identity run '#{session_name}' '#{window_index}' '#{pane_index}' '"
    bind-key F run-shell "tmux split-window -v -c '#{pane_current_path}' 'sshm host run '#{session_name}' '#{window_index}' '#{pane_index}' sftp '"
    bind-key M run-shell "tmux split-window -v -c '#{pane_current_path}' 'sshm host run '#{session_name}' '#{window_index}' '#{pane_index}' multi_command '"

    # Key Binds useful
    bind-key -n M-s choose-session
    bind-key -n M-t choose-window
    bind-key -n M-n swap-window -t :- \\; select-window -t :-
    bind-key -n M-m swap-window -t :+ \\; select-window -t :+
    bind-key -n M-Left swap-window -t :- \\; select-window -t :-
    bind-key -n M-Right swap-window -t :+ \\; select-window -t :+
    bind-key -n M-f switch -t fast-connections
    bind-key -n M-d switch -t default
    bind-key -n M-r switch-client -n
    bind-key -n M-e switch-client -p
    bind-key -n M-o switch-client -p
    bind-key -n M-p switch-client -n
    bind-key -n M-q select-window -t :-
    bind-key -n M-w select-window -t :+1
    bind-key -n M-1 select-window -t 1
    bind-key -n M-2 select-window -t 2
    bind-key -n M-3 select-window -t 3
    bind-key -n M-4 select-window -t 4
    bind-key -n M-5 select-window -t 5
    bind-key -n M-6 select-window -t 6
    bind-key -n M-7 select-window -t 7
    bind-key -n M-8 select-window -t 8
    bind-key -n M-9 select-window -t 9

    # Copy Mouse Selection to clipboard
    # xclip=X11 | xsel=X11 | wl-cop=Wayland | pbcopy=MacOS
    if-shell 'command -v xclip >/dev/null' 'set-option -g @copy-command "xclip -selection clipboard -i"'
    if-shell 'command -v xsel >/dev/null' 'set-option -g @copy-command "xsel --clipboard -i"'
    if-shell 'command -v wl-copy >/dev/null' 'set-option -g @copy-command "wl-copy"'
    if-shell 'command -v pbcopy >/dev/null' 'set-option -g @copy-command "pbcopy"'
    bind-key -T copy-mode-vi MouseDragEnd1Pane send-keys -X copy-pipe-and-cancel "#{@copy-command}"
    bind-key -T copy-mode MouseDragEnd1Pane send-keys -X copy-pipe-and-cancel "#{@copy-command}"

    # Status Bar
    set -g status-interval 2
    set -g status-bg colour235
    set -g status-fg white
    set -g status-style bold
    set -g status-left-length 100
    set -g status-right-length 100
    set -g status-left '#[fg=white,bg=colour235,bold] 📚 #S #[default]'
    set -g status-right '#[fg=white]#{?#{==:#{pane_current_command},ssh},🔒 SSH,#{?#{==:#{pane_current_command},sftp},📂 SFTP,💻 Local}} #[fg=white]📅 %a %d/%b #[fg=white]🕒 %H:%M #[default]'

    # Tabs
    set -g window-status-current-style bg=colour33,fg=white,bold
    set -g window-status-current-format '#[fg=white,bold] #{?#{==:#{pane_current_command},ssh},🔒,#{?#{==:#{pane_current_command},sftp},📂,💻}} #I #W'
    set -g window-status-format '#[fg=colour250] #{?#{==:#{pane_current_command},ssh},🔒,#{?#{==:#{pane_current_command},sftp},📂,💻}} #I #W'
    set -g window-status-style bg=colour235,fg=colour250

    # Panes
    set -g pane-active-border-style fg=colour45
    set -g pane-border-style fg=colour235
    """

    with open(settings.tmux.TMUX_CONFIG_FILE, "a+t") as file:
        file.write(tmux_config)


init_toml_config()
init_tmux()
