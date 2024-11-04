import libtmux

from sshtmux.globals import TMUX_CONFIG_FILE


server = libtmux.Server(
    socket_name="sshtmux",
    config_file=TMUX_CONFIG_FILE,
)


def create_window(session_name, window_name, attach=False):
    session = server.find_where({"session_name": session_name})

    if not session:
        server.cmd("new-session", "-d", "-P", "-F#{session_id}", "-s", session_name)
        session = server.find_where({"session_name": session_name})
        if len(session.windows) == 1:
            session.windows[0].rename_window(window_name)
    else:
        session.new_window(window_name=window_name, attach=attach)

    session.refresh()
    if attach:
        session.attach()
    return True


def attach():
    sessions = server.list_sessions()

    if sessions:
        current_session = sessions[0]

        if current_session:
            current_session.cmd("choose-window")
            current_session.attach()
            return True
    return False
