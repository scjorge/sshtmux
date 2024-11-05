import time

import libtmux
from libtmux import Window

from sshtmux.core.config import settings
from sshtmux.sshm import SSH_Host


def get_server():
    return libtmux.Server(
        socket_name=settings.tmux.TMUX_SOCKET_NAME,
        socket_path=settings.tmux.TMUX_SOCKET_PATH,
        config_file=settings.tmux.TMUX_CONFIG_FILE,
    )


def validate_ssh_session(window: Window, host: SSH_Host, last_result):
    timeout_start = time.time()

    while True:
        if time.time() - timeout_start > settings.tmux.TMUX_TIMEOUT_COMMANDS:
            raise Exception(f"Timeout reached! Group: {host.group} - Host: {host.name}")

        result = window.attached_pane.capture_pane()
        if last_result == result:
            time.sleep(0.1)
            continue

        if isinstance(result, str):
            if "Permission denied" in result:
                window.kill_window()
                raise Exception("Permission denied! Wrong password!")
        elif isinstance(result, list) or isinstance(result, tuple):
            for text in result:
                if "Permission denied" in text:
                    window.kill_window()
                    raise Exception("Permission denied! Wrong password!")
        break


def start_ssh_session(window: Window, host: SSH_Host, identity: str = None):
    timeout_start = time.time()
    window.attached_pane.send_keys(f"ssh -o StrictHostKeyChecking=no {host.name}; exit")

    password_prompt_found = False
    while not password_prompt_found:
        if time.time() - timeout_start > settings.tmux.TMUX_TIMEOUT_COMMANDS:
            raise Exception(f"Timeout reached! Group: {host.group} - Host: {host.name}")

        result = window.attached_pane.capture_pane()
        if isinstance(result, str):
            if "password:" in result:
                password_prompt_found = True
                break
        elif isinstance(result, list) or isinstance(result, tuple):
            for text in result:
                if "password:" in text:
                    password_prompt_found = True
                    break
        time.sleep(0.1)

    if password_prompt_found:
        window.attached_pane.send_keys("senha")
        validate_ssh_session(window, host, result)


def create_window(host: SSH_Host, attach=False, identity: str = None):
    server = get_server()
    window = None
    session = server.find_where({"session_name": host.group})

    if not session:
        server.cmd("new-session", "-d", "-P", "-F#{session_id}", "-s", host.group)
        session = server.find_where({"session_name": host.group})
        if not session:
            raise Exception(f"Something went wrong to find session: {host.group}")

        if len(session.windows) == 1:
            window = session.windows[0].rename_window(host.name)
        else:
            raise Exception(
                f"Something went wrong to find inicial window! Session: {host.group}"
            )
    else:
        window = session.new_window(window_name=host.name, attach=attach)

    if window:
        start_ssh_session(window, host, identity)
    else:
        raise Exception(
            f"Something went wrong to find window! Session: {host.group} - Window: {host.name}"
        )

    if attach:
        session.attach()
    return True


def attach():
    server = get_server()
    sessions = server.list_sessions()

    if sessions:
        current_session = sessions[0]

        if current_session:
            current_session.cmd("choose-window")
            current_session.attach()
            return True
    return False
