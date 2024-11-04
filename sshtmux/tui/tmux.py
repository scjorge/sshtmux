import libtmux

server = libtmux.Server()


def create_window(group, name, attach=False):
    session = server.find_where({"session_name": group})

    if not session:
        session = server.new_session(session_name=group, attach=attach)
        if len(session.windows) == 1:
            session.windows[0].rename_window(name)
            if attach:
                session.attach()
            return True
    else:
        session.new_window(window_name=name, attach=attach)
        if attach:
            session.attach()
        return True
    return False


def attach():
    sessions = server.list_sessions()

    if sessions:
        current_session = sessions[0]

        if current_session:
            current_session.cmd("choose-window")
            current_session.attach()
            return True
    return False
