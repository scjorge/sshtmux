import click
from libtmux.exc import LibTmuxException

from sshtmux.services.tmux import Tmux

HELP = "Run commands on Tmux (Executed only by Tmux)"


@click.command(name="run", short_help=HELP, help=HELP)
@click.argument("session-name")
@click.argument("window-index")
@click.argument("panel-index")
@click.argument("cmd-ref")
def cmd(session_name, window_index, panel_index, cmd_ref):
    tmux = Tmux()
    try:
        tmux.execute_host_cmd(session_name, window_index, panel_index, cmd_ref)
    except LibTmuxException as e:
        print(str(e))
