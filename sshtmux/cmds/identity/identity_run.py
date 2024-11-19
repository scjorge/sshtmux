import click
from libtmux.exc import LibTmuxException

from sshtmux.services.tmux import Tmux

HELP = "Prompt Identity on Tmux (Executed only by Tmux)"


@click.command(name="run", short_help=HELP, help=HELP)
@click.argument("session-name")
@click.argument("window-index")
@click.argument("panel-index")
def cmd(session_name, window_index, panel_index):
    tmux = Tmux()
    try:
        tmux.execute_identity(session_name, window_index, panel_index)
    except LibTmuxException as e:
        print(str(e))
