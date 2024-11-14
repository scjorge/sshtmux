import click
from rich.console import Console

from sshtmux.core.config import T_Host_Style, settings
from sshtmux.sshm import (
    SSH_Config,
    complete_ssh_host_names,
    complete_styles,
    generate_graph,
    trace_jumphosts,
)

console = Console()
styles_str = ",".join(T_Host_Style.__args__)

# ------------------------------------------------------------------------------
# COMMAND: host show
# ------------------------------------------------------------------------------
SHORT_HELP = "Show current host configuration"
LONG_HELP = """
Shows details about host and its configuration

Command can generate nice representation of configuration for given HOST.
If HOST is using "proxyjump" properties, command will try to collect also all info
from intermediate hosts/proxies as well. This relations can then be showed when using
option --follow, to display all interconnected host path. (NOTE: This relations can
only be understand and showed if "proxyjump" hosts are also part of the configuration!!!)

Additionally when using --graph option, command can "draw" visualization of
connection path, and defined end-to-end tunnels
"""

# Parameters help:
FOLLOW_HELP = "Follow and displays all connected hosts via proxyjump (works only for locally defined hosts)"
GRAPH_HELP = "Shows connection to target as graph with tunnels visualizations"
STYLE_HELP = f"Select output rendering style for host details: ({styles_str}), (default: {settings.sshtmux.SSHTMUX_HOST_STYLE})"
# ------------------------------------------------------------------------------


@click.command(name="show", short_help=SHORT_HELP, help=LONG_HELP)
@click.option(
    "--style",
    default="",
    help=STYLE_HELP,
    shell_complete=complete_styles,
)
@click.option("--graph", is_flag=True, help=GRAPH_HELP)
@click.argument("name", shell_complete=complete_ssh_host_names)
@click.pass_context
def cmd(ctx: click.core.Context, name: str, style: str, graph: bool):
    config: SSH_Config = ctx.obj

    # Define host print style from CLI or config or default
    if not style:
        if "host-style" in config.opts:
            style = config.opts["host-style"]
        else:
            print("sodcoas")
            style = settings.sshtmux.SSHTMUX_HOST_STYLE

    if not config.check_host_by_name(name):
        print(
            f"Cannot get info for host '{name}' as it is not defined in configuration!"
        )
        ctx.exit(1)

    # Get info about linked hosts (required for graph and follow)
    traced_hosts = trace_jumphosts(name, config, ctx, style)

    # Normal show, no linked graphs needed
    console.print(traced_hosts[0])

    # TODO: Make better graph output
    if graph:
        console.print(generate_graph(traced_hosts), "")
