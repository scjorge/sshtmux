import time

import libtmux
from libtmux import Window

from sshtmux.core.config import settings
from sshtmux.sshm import SSH_Host


def _get_server():
    return libtmux.Server(
        socket_name=settings.tmux.TMUX_SOCKET_NAME,
        socket_path=settings.tmux.TMUX_SOCKET_PATH,
        config_file=settings.tmux.TMUX_CONFIG_FILE,
    )


def _check_timeout_reached(timeout_start, result, host: SSH_Host, window: Window):
    if time.time() - timeout_start > settings.tmux.TMUX_TIMEOUT_COMMANDS:
        timeout_mgs = f"Timeout reached! Group: {host.group} - Host: {host.name}"
        window.kill_window()
        if result and len(result) >= 2:
            raise Exception(f"{timeout_mgs} \n\n {result[-2]}")
        raise Exception(f"{timeout_mgs} {host.name} \n\n {result}")


def _validate_ssh_session(window: Window, host: SSH_Host, last_result):
    result = None
    timeout_start = time.time()

    while True:
        _check_timeout_reached(timeout_start, result, host, window)

        result = window.attached_pane.capture_pane()
        if last_result == result:
            time.sleep(0.1)
            continue

        if isinstance(result, str):
            result = [result]

        for text in result:
            if "Permission denied" in text:
                window.kill_window()
                raise Exception("Permission denied! Wrong password!")
        break


def _start_ssh_session(window: Window, host: SSH_Host, identity: str = None):
    result = None
    timeout_start = time.time()
    window.attached_pane.send_keys(
        f"ssh -o StrictHostKeyChecking=no {host.name} && exit"
    )

    password_prompt_found = False
    while not password_prompt_found:
        _check_timeout_reached(timeout_start, result, host, window)

        result = window.attached_pane.capture_pane()
        if isinstance(result, str):
            result = [result]

        for text in result:
            if "password:" in text:
                password_prompt_found = True
                break
            if text.startswith("ssh:"):
                raise Exception(
                    f"SSH Error! Group: {host.group} - Host: {host.name} \n\n {text}"
                )
            elif (
                "Connection reset by peer" in text
                or "Read from socket failed: Connection reset by peer" in text
                or "Timeout, server not responding" in text
                or "Unable to negotiate with" in text
                or "Algorithm negotiation failed" in text
            ):
                raise Exception(
                    f"Connection Error! Group: {host.group} - Host: {host.name} \n\n {text}"
                )

        time.sleep(0.1)

    if password_prompt_found:
        window.attached_pane.send_keys("senha")
        _validate_ssh_session(window, host, result)


def create_window(host: SSH_Host, attach=False, identity: str = None):
    server = _get_server()
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
        _start_ssh_session(window, host, identity)
    else:
        raise Exception(
            f"Something went wrong to find window! Session: {host.group} - Window: {host.name}"
        )

    if attach:
        session.attach()
    return True


def attach():
    server = _get_server()
    sessions = server.list_sessions()

    if sessions:
        current_session = sessions[0]

        if current_session:
            current_session.cmd("choose-window")
            current_session.attach()
            return True
    return False
