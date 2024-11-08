import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Union

import libtmux
from libtmux import Window

from sshtmux.core.config import settings
from sshtmux.exceptions import IdentityException, SSHException, TMUXException
from sshtmux.services.connections_erros import CONNECTIONS_ERRORS
from sshtmux.services.identities import PasswordManager
from sshtmux.sshm import SSH_Host


class ConnectionAbstract(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.password_manager = PasswordManager("sshtmux")

    @abstractmethod
    def start(
        self,
        window: Window,
        host: SSH_Host,
        identity: Union[str, None],
    ):
        """
        Start SSH connection
        """

    def _check_connections_errors(
        self,
        window: Window,
        pane_output: Union[str, List[str]],
        host: SSH_Host,
    ):
        if isinstance(pane_output, str):
            pane_output = [pane_output]

        is_failed = False
        for text in pane_output:
            text = text.lower()
            if text.startswith("ssh:") or text.startswith(
                "ssh_exchange_identification:"
            ):
                is_failed = True
            else:
                for error in CONNECTIONS_ERRORS:
                    if error.lower() in text.lower():
                        is_failed = True
                        break

            if is_failed:
                window.kill_window()
                raise SSHException(f"{host}\n\n Connection Error! {text}")

    def _check_timeout_reached(
        self,
        timeout_start,
        pane_output: List[str],
        host: SSH_Host,
        window: Window,
    ):
        if time.time() - timeout_start > settings.tmux.TMUX_TIMEOUT_COMMANDS:
            timeout_mgs = f"{host}\n\n Timeout reached!"
            window.kill_window()
            if pane_output and len(pane_output) >= 2:
                raise SSHException(f"{timeout_mgs} \n\n {pane_output[-2]}")
            raise SSHException(f"{timeout_mgs} \n\n {host} \n\n {pane_output}")


class IdentityConnection(ConnectionAbstract):
    def start(
        self,
        window: Window,
        host: SSH_Host,
        identity: Union[str, None],
    ):
        pane_output = None
        cmd = f"ssh -o StrictHostKeyChecking=no {host.name} && exit"
        try:
            password = self.password_manager.get_password(identity)
        except IdentityException as e:
            window.kill_window()
            raise e
        window.attached_pane.send_keys(cmd)

        timeout_start = time.time()
        password_prompt_found = False
        while not password_prompt_found:
            self._check_timeout_reached(timeout_start, pane_output, host, window)

            pane_output = window.attached_pane.capture_pane()
            self._check_connections_errors(window, pane_output, host)

            for text in pane_output:
                if "password:" in text:
                    password_prompt_found = True
                    break
            time.sleep(0.1)

        if password_prompt_found:
            window.attached_pane.send_keys(password)
            self._validate_ssh_session_identity(window, host, pane_output)

    def _validate_ssh_session_identity(
        self,
        window: Window,
        host: SSH_Host,
        last_pane_output: List[str],
    ):
        pane_output = None
        timeout_start = time.time()

        while True:
            self._check_timeout_reached(timeout_start, pane_output, host, window)

            pane_output = window.attached_pane.capture_pane()
            if last_pane_output == pane_output:
                time.sleep(0.1)
                continue
            self._check_connections_errors(window, pane_output, host)
            break


class ConnectionType(Enum):
    normal = None
    identity = IdentityConnection
    custom = None


class Tmux:
    def __init__(self) -> None:
        self.server = libtmux.Server(
            socket_name=settings.tmux.TMUX_SOCKET_NAME,
            socket_path=settings.tmux.TMUX_SOCKET_PATH,
            config_file=settings.tmux.TMUX_CONFIG_FILE,
        )

    def create_window(
        self,
        type_connection: ConnectionType,
        host: SSH_Host,
        attach=False,
        identity: Union[str, None] = None,
    ):
        window = None
        session = self.server.find_where({"session_name": host.group})
        connection: ConnectionAbstract = type_connection.value()

        if not session:
            self.server.cmd(
                "new-session", "-d", "-P", "-F#{session_id}", "-s", host.group
            )
            session = self.server.find_where({"session_name": host.group})
            if not session:
                raise TMUXException(f"{host}\n\n Something went wrong to find session!")

            if len(session.windows) == 1:
                window = session.windows[0].rename_window(host.name)
            else:
                raise TMUXException(
                    f"{host}\n\n Something went wrong to find inicial window!"
                )
        else:
            window = session.new_window(window_name=host.name, attach=attach)

        if window:
            connection.start(window, host, identity)
        else:
            raise TMUXException(f"{host}\n\n Something went wrong to find window!")

        if attach:
            session.attach()
        return True

    def attach(self):
        sessions = self.server.list_sessions()

        if sessions:
            current_session = sessions[0]

            if current_session:
                current_session.cmd("choose-window")
                current_session.attach()
                return True
        return False
