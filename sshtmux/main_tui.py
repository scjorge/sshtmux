from typing import ClassVar

from rich import box
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Container, VerticalScroll
from textual.widgets import (
    ContentSwitcher,
    Footer,
    Header,
    Input,
    Label,
    OptionList,
    Static,
    Tree,
)
from textual.widgets.option_list import Separator

from sshtmux.core.config import settings
from sshtmux.exceptions import IdentityException, SSHException, TMUXException
from sshtmux.services.identities import PasswordManager
from sshtmux.services.tmux import ConnectionProtocol, ConnectionType, Tmux
from sshtmux.sshm import SSH_Config, SSH_Group, SSH_Host
from sshtmux.tools.messages import (
    NO_TMUX_SESSIONS_AVAILABLE,
    NOT_ALLOWED_NESTED_CONNECTIONS,
    ONLY_NORMAL_HOSTS_ALLOWED,
)


class SSHGroupDataInfo(Static):
    """Widget for SSH Group data"""

    DEFAULT_CSS = """
    .grp_labels {
        width: 100%;
        color: $accent;
        padding: 1 1 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Description", classes="grp_labels")
        yield Static(Panel("...empty...", style="grey42"), id="grp_description")
        yield Label("Extra information", classes="grp_labels")
        yield Static(Panel("...empty...", style="grey42"), id="grp_information")

    def update(self, group: SSH_Group) -> None:
        desc: Static = self.query_one("#grp_description")  # type: ignore
        info: Static = self.query_one("#grp_information")  # type: ignore
        desc.update(Panel(group.desc, border_style="grey42"))
        info.update(Panel("\n".join(group.info), border_style="grey42"))


class SSHHostDataInfo(Static):
    """Widget for SSH Host data"""

    DEFAULT_CSS = """
    .hst_labels {
        width: 100%;
        color: $accent;
        padding: 1 1 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Details", classes="hst_labels")
        yield Static(Panel("...empty...", style="grey42"), id="hst_details")
        yield Label("Extra information", classes="hst_labels")
        yield Static(Panel("...empty...", style="grey42"), id="hst_information")
        yield Label("SSH Parameters", classes="hst_labels")
        yield Static(Panel("...empty...", style="grey42"), id="hst_parameters")

    def update(self, host: SSH_Host) -> None:
        det: Static = self.query_one("#hst_details")  # type: ignore
        info: Static = self.query_one("#hst_information")  # type: ignore
        params: Static = self.query_one("#hst_parameters")  # type: ignore
        det.update(
            Panel(
                f"[bold]Group[/b]: {host.group}\n[bold]Type[/b]:  {host.type}",
                border_style="grey42",
            )
        )
        info.update(
            Panel("\n".join(host.info), border_style="grey42")
            if host.info
            else Panel("...empty...", style="grey42")
        )

        param_table = Table(
            box=box.ROUNDED,
            style="grey42",
            show_header=True,
            show_edge=True,
            expand=True,
        )
        param_table.add_column("Param")
        param_table.add_column("Value")
        param_table.add_column("Inherited-from")

        # Add rows for SSH Config parameter table
        for key, value in host.params.items():
            output_value = value if not isinstance(value, list) else "\n".join(value)
            param_table.add_row(key, output_value)

        # Add rows for inherited SSH Config parameters
        for pattern, pattern_params in host.inherited_params:
            for param, value in pattern_params.items():
                if param not in host.params:
                    output_value = (
                        value if not isinstance(value, list) else "\n".join(value)
                    )
                    param_table.add_row(param, output_value, pattern, style="yellow")

        params.update(param_table)  # type: ignore


class SSHDataView(Static):
    """SSH Item data view panel"""

    def compose(self) -> ComposeResult:
        yield Label(id="data_view_header")
        yield Static(Rule(style="$text"))

        with ContentSwitcher(initial="no-view"):
            yield Static(id="no-view")
            yield SSHGroupDataInfo(id="group-view")
            with VerticalScroll(id="host-view"):
                yield SSHHostDataInfo()

    def update(self, sshitem="") -> None:
        label: Label = self.query_one("#data_view_header")  # type: ignore
        grp = self.query_one(SSHGroupDataInfo)
        hst = self.query_one(SSHHostDataInfo)

        if isinstance(sshitem, SSH_Group):
            group: SSH_Group = sshitem
            label.update(f"Group: {group.name}")
            self.query_one(ContentSwitcher).current = "group-view"
            grp.update(group)

        elif isinstance(sshitem, SSH_Host):
            host: SSH_Host = sshitem
            label.update(f"Host: {host.name}")
            self.query_one(ContentSwitcher).current = "host-view"
            hst.update(host)

        else:
            label.update("Select node from the list")
            self.query_one(ContentSwitcher).current = "no-view"


class CustomOptionList(OptionList):
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("down", "cursor_down", "Down", show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("end", "last", "Last", show=False),
        Binding("enter", "select", "Select", show=False),
        Binding("home", "first", "First", show=False),
        Binding("pagedown", "page_down", "Page down", show=False),
        Binding("pageup", "page_up", "Page up", show=False),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]


class SSHTui(App):
    TITLE = "SSHTMUX"
    SUB_TITLE = "Experimental TUI"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("t", "attach_tmux", "TMUX"),
        ("d", "detached_ssh", "Detached SSH"),
        ("c", "connect_ssh", "Conect SSH"),
        ("f", "connect_sftp", "SFTP to host"),
        ("m", "toggle_dark"),
        ("j", "cursor_down"),
        ("k", "cursor_up"),
        ("l", "cursor_expand"),
        ("h", "cursor_collapse"),
        ("?", "search_groups", "Search Groups"),
        ("/", "search_hosts", "Search Hosts"),
        ("escape", "clean_filters"),
    ]

    CSS = """
    Screen {
        background: $surface-darken-1;
    }

    SSHDataView {
        width: 100%;
        height: 100%;
        padding: 1 2;
        background: $panel;
        content-align: center middle;
    }

    Tree {
        scrollbar-gutter: stable;
        overflow: auto;
        width: 36;
        height: 100%;
        dock: left;
        background: $surface;
    }
    """

    def __init__(self, sshmonf=None):
        self.tmux = Tmux()
        self.password_manager = PasswordManager()
        self.identities = self.password_manager.get_identities()
        self.attach_connection = False
        self.connections_tree = None
        if isinstance(sshmonf, SSH_Config):
            self.sshmonf = sshmonf
        else:
            self.sshmonf = SSH_Config(file=settings.ssh.SSH_CONFIG_FILE).read().parse()

        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container():
            self.connections_tree = Tree(
                f"SSH Configuration ({len(self.sshmonf.groups)} groups)",
                id="sshtree",
                data=None,
            )
            self._generate_tree()

            yield self.connections_tree
            yield SSHDataView()

        self.input_groups_search = Input(
            placeholder="Search Groups...", id="search_groups_input"
        )
        self.input_groups_search.display = False
        self.input_hosts_search = Input(
            placeholder="Search Hosts...", id="search_hosts_input"
        )
        self.input_hosts_search.display = False
        self.type_password = "Type Password"
        self.select_identity = CustomOptionList(
            self.type_password, Separator(), *self.identities, id="select_identity"
        )
        self.select_identity.display = False
        yield self.input_groups_search
        yield self.input_hosts_search
        yield self.select_identity
        yield Footer()

    async def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        """
        Manager identity
        """
        value = event.option.prompt

        if not self._is_sshhost():
            return

        self.connections_tree.focus()
        self.select_identity.display = False

        if value == self.type_password:
            if self.connection == ConnectionProtocol.ssh:
                self._start_connection(ConnectionType.normal, None)
            elif self.connection == ConnectionProtocol.sftp:
                self._start_connection(ConnectionType.sftp_normal, None)
        elif value:
            if self.connection == ConnectionProtocol.ssh:
                self._start_connection(ConnectionType.identity, value)
            elif self.connection == ConnectionProtocol.sftp:
                self._start_connection(ConnectionType.sftp_identity, value)

    def on_mount(self, _) -> None:
        self.ENABLE_COMMAND_PALETTE = False
        self.connections_tree.focus()

    def on_tree_node_highlighted(self, event):
        self.current_node = event.node.data
        self.query_one(SSHDataView).update(self.current_node)

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def action_quit(self) -> None:
        self.exit(0)

    def action_search_groups(self) -> None:
        self.input_hosts_search.value = ""
        self.input_hosts_search.display = False
        self.input_groups_search.display = True
        self.input_groups_search.focus()

    def action_search_hosts(self) -> None:
        self.input_groups_search.value = ""
        self.input_groups_search.display = False
        self.input_hosts_search.display = True
        self.input_hosts_search.focus()

    def action_clean_filters(self) -> None:
        self.input_groups_search.value = ""
        self.input_hosts_search.value = ""
        self.input_groups_search.display = False
        self.input_hosts_search.display = False
        self.select_identity.display = False
        for node in self.connections_tree.root.children:
            node.collapse_all()
        self.connections_tree.focus()

    def action_cursor_down(self) -> None:
        if self.connections_tree.cursor_line == -1:
            self.connections_tree.cursor_line = 0
        else:
            self.connections_tree.cursor_line += 1
        self.connections_tree.scroll_to_line(self.connections_tree.cursor_line)

    def action_cursor_up(self) -> None:
        if self.connections_tree.cursor_line == -1:
            self.connections_tree.cursor_line = self.connections_tree.last_line
        else:
            self.connections_tree.cursor_line -= 1
        self.connections_tree.scroll_to_line(self.connections_tree.cursor_line)

    def action_cursor_expand(self) -> None:
        self.connections_tree.cursor_node.expand()

    def action_cursor_collapse(self) -> None:
        self.connections_tree.cursor_node.collapse()

    def action_attach_tmux(self) -> None:
        attached = self._run_external_func_with_args(self.tmux.attach)
        if not attached:
            self.notify(NO_TMUX_SESSIONS_AVAILABLE, severity="warning")

    def action_connect_ssh(self, attach=True):
        if not self._is_sshhost():
            return

        self.connection = ConnectionProtocol.ssh
        self.atatch_connection = attach
        if not self.identities:
            self._start_connection(ConnectionType.normal, None)
            return
        self.select_identity.display = True
        self.select_identity.focus()

    def action_detached_ssh(self) -> None:
        self.connection = ConnectionProtocol.ssh
        self.action_connect_ssh(False)

    def action_connect_sftp(self) -> None:
        self.connection = ConnectionProtocol.sftp
        self.atatch_connection = True
        if not self._is_sshhost():
            return
        if not self.identities:
            self._start_connection(ConnectionType.sftp_normal, None)
            return
        self.select_identity.display = True
        self.select_identity.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        event.input.display = False
        self.connections_tree.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        filter = event.value
        self.connections_tree.clear()
        if event.input.id == "search_groups_input":
            self._generate_tree(filter_groups=filter)
        elif event.input.id == "search_hosts_input":
            self._generate_tree(filter_hosts=filter)

        for node in self.connections_tree.root.children:
            node.expand()
            for child in node.children:
                child.expand()
        if filter == "":
            for node in self.connections_tree.root.children:
                node.collapse_all()

    def _generate_tree(
        self, *, filter_hosts: str | None = None, filter_groups: str | None = None
    ):
        self.connections_tree.root.expand()

        groups = self.sshmonf.groups
        if filter_hosts:
            groups_filtered = []
            for group in groups:
                hosts = [h for h in group.hosts if filter_hosts in h.name]
                if len(hosts) > 0:
                    group.hosts = hosts
                    groups_filtered.append(group)
            groups = groups_filtered

        elif filter_groups:
            groups = [g for g in groups if filter_groups in g.name]

        for group in groups:
            g = self.connections_tree.root.add(
                f":file_folder: {group.name}", data=group, expand=False
            )
            for host in group.hosts + group.patterns:
                g.add_leaf(host.name, data=host)

    def _is_sshhost(self):
        if not (
            isinstance(self.current_node, SSH_Host)
            and self.current_node.type == "normal"
        ):
            self.notify(ONLY_NORMAL_HOSTS_ALLOWED, severity="warning")
            return False
        return True

    def _start_connection(self, type_connection, identity):
        if not self._is_sshhost():
            return

        if settings.ssh.SSH_CUSTOM_COMMAND:
            type_connection = ConnectionType.custom

        is_conneted = self._run_external_func_with_args(
            self.tmux.create_window,
            type_connection=type_connection,
            host=self.current_node,
            attach=self.atatch_connection,
            identity=identity,
        )

        if is_conneted:
            self.notify(
                f"Connected to:\n\n{self.current_node}",
                severity="information",
            )

    def _run_external_func_with_args(self, func, **kwargs):
        driver = self._driver
        result = None
        if driver is not None:
            driver.stop_application_mode()
            try:
                result = func(**kwargs)
            except TMUXException as e:
                self.notify(str(e), title="Tmux", severity="error")
            except SSHException as e:
                self.notify(str(e), title="SSH", severity="error")
            except IdentityException as e:
                self.notify(str(e), title="Identity", severity="error")
            except Exception as e:
                if "no server running on" in str(e):
                    pass
                elif "sessions should be nested with care" in str(e):
                    self.notify(NOT_ALLOWED_NESTED_CONNECTIONS, severity="warning")
                else:
                    self.notify(str(e), title="Internal", severity="error")
            finally:
                self.refresh()
                driver.start_application_mode()
        return result


def tui():
    SSHTui().run()


if __name__ == "__main__":
    tui()
