import click
from libtmux.exc import LibTmuxException

from sshtmux.services.tmux import Tmux

HELP = "Show Snippets menu to execute one"


@click.command(name="run", short_help=HELP, help=HELP)
@click.option("--session-name", "-s", default=None, help="Session Name (opcional)")
@click.option("--window-index", "-w", default=None, help="Window Index (opcional)")
@click.option("--panel-index", "-p", default=None, help="Panel Index (opcional)")
def cmd(session_name, window_index, panel_index):
    tmux = Tmux()
    try:
        tmux.execute_snippet(session_name, window_index, panel_index)
    except LibTmuxException as e:
        print(str(e))
