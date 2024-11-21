import os
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Union

import libtmux
from libtmux import Window
from rich import print
from rich.prompt import Prompt

from sshtmux.core.config import (
    FAST_CONNECTIONS_GROUP_NAME,
    FAST_SESSIONS_NAME,
    MULTICOMMNAD_CLI,
    SFTP_CLI,
    settings,
)
from sshtmux.exceptions import IdentityException, SSHException, TMUXException
from sshtmux.services.connections_erros import CONNECTIONS_ERRORS
from sshtmux.services.identities import PasswordManager, prompt_identity
from sshtmux.services.snippets import prompt_snippet
from sshtmux.sshm import SSH_Config, SSH_Host


class ConnectionAbstract(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.password_manager = PasswordManager()
        self.connection_cmd = settings.ssh.SSH_COMMAND

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
                error_msg = (
                    pane_output[-2] if len(pane_output) >= 2 else str(pane_output)
                )
                raise SSHException(f"{host}\n\nConnection Error!\n\n{error_msg}")

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
                error_msg = (
                    pane_output[-2] if len(pane_output) >= 2 else str(pane_output)
                )
                raise SSHException(f"{timeout_mgs} \n\n {error_msg}")
            raise SSHException(f"{timeout_mgs} \n\n {host} \n\n {pane_output}")


class NormalConnection(ConnectionAbstract):
    def start(
        self,
        window: Window,
        host: SSH_Host,
        identity: Union[str, None],
    ):
        pane_output = None
        cmd = self.connection_cmd.replace("${hostname}", host.name)
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


class IdentityConnection(ConnectionAbstract):
    def start(
        self,
        window: Window,
        host: SSH_Host,
        identity: Union[str, None],
    ):
        pane_output = None
        cmd = self.connection_cmd.replace("${hostname}", host.name)
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


class CustomConnection(ConnectionAbstract):
    def start(
        self,
        window: Window,
        host: SSH_Host,
        identity: Union[str, None],
    ):
        if not settings.ssh.SSH_CUSTOM_COMMAND:
            raise TMUXException("SSH_CUSTOM_COMMAND not set")

        cmd = settings.ssh.SSH_CUSTOM_COMMAND.replace("${hostname}", host.name)
        if identity:
            try:
                password = self.password_manager.get_password(identity)
            except IdentityException as e:
                window.kill_window()
                raise e
            cmd = cmd.replace("${password}", password)
        else:
            cmd = cmd.replace("${password}", "")
        window.attached_pane.send_keys(cmd)


class SFTPNormalConnection(NormalConnection):
    def __init__(self):
        super().__init__()
        self.connection_cmd = settings.ssh.SFTP_COMMAND


class SFTPIdentityConnection(IdentityConnection):
    def __init__(self):
        super().__init__()
        self.connection_cmd = settings.ssh.SFTP_COMMAND


class ConnectionProtocol(Enum):
    ssh = "SSH"
    sftp = "SFTP"


class ConnectionType(Enum):
    normal = NormalConnection
    identity = IdentityConnection
    custom = CustomConnection
    sftp_normal = SFTPNormalConnection
    sftp_identity = SFTPIdentityConnection


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
        overwritten_group: str = None,
    ):
        window = None
        window_name = host.name
        session_name = host.group
        connection: ConnectionAbstract = type_connection.value()
        if overwritten_group:
            session_name = overwritten_group
        session = self.server.find_where({"session_name": session_name})

        if window_name.startswith(session_name):
            window_name = window_name.replace(f"{session_name}-", "")

        if not session:
            self.server.cmd(
                "new-session", "-d", "-P", "-F#{session_id}", "-s", session_name
            )
            session = self.server.find_where({"session_name": session_name})
            if not session:
                raise TMUXException(f"{host}\n\n Something went wrong to find session!")

            if len(session.windows) == 1:
                window = session.windows[0].rename_window(window_name)
            else:
                raise TMUXException(
                    f"{host}\n\n Something went wrong to find inicial window!"
                )
        else:
            window = session.new_window(window_name=window_name, attach=attach)

        if window:
            try:
                connection.start(window, host, identity)
            except KeyboardInterrupt as e:
                raise TMUXException(str(e))
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
                current_session.cmd("choose-session")
                current_session.attach()
                return True
        return False

    def execute_cmd_tmux(self, cmd, session_name, window_index, panel_index):
        session = self.server.find_where({"session_name": session_name})
        if not session:
            print("No Tmux session available")
            return
        window = [w for w in session.windows if str(w.index) == str(window_index)][0]
        panel = [p for p in window.panes if str(p.index) == str(panel_index)][0]
        panel.send_keys(cmd)

    def execute_cmd_shell(self, cmd):
        if not cmd:
            return
        cmd = cmd.split()
        os.execvp(cmd[0], cmd)

    def execute_snippet(self, session_name, window_index, panel_index):
        snippet = prompt_snippet()
        if not snippet:
            print("No Snippets found")
            return

        is_tmux = all([session_name, window_index, panel_index])
        if is_tmux:
            self.execute_cmd_tmux(snippet, session_name, window_index, panel_index)
        else:
            self.execute_cmd_shell(snippet)

    def execute_identity(self, session_name, window_index, panel_index):
        identity = prompt_identity()
        if not identity:
            print("No Identity found")
            return
        self.execute_cmd_tmux(identity, session_name, window_index, panel_index)

    def execute_multi_command(self, session):
        cmd = Prompt.ask("Multi Session Command")
        if not cmd:
            return
        for window in session.windows:
            for panel in window.panes:
                panel.send_keys(cmd)

    def execute_host_cmd(self, session_name, window_index, panel_index, cmd_ref):
        cmd = None
        session = self.server.find_where({"session_name": session_name})
        if not session:
            print("No Tmux session available")
            return

        window = [w for w in session.windows if str(w.index) == str(window_index)][0]
        if session_name in [
            FAST_CONNECTIONS_GROUP_NAME,
            FAST_SESSIONS_NAME,
            SSH_Config.DEFAULT_GROUP_NAME,
        ]:
            hostname = window.name
        else:
            if not window.name.startswith(f"{session_name}-"):
                hostname = f"{session_name}-{window.name}"
            else:
                hostname = window.name

        if cmd_ref == SFTP_CLI:
            cmd = (
                settings.ssh.SFTP_COMMAND.replace("${hostname}", hostname)
                .replace("&& exit", "")
                .replace("; exit", "")
            )
            self.execute_cmd_shell(cmd)

        if cmd_ref == MULTICOMMNAD_CLI:
            self.execute_multi_command(session)
