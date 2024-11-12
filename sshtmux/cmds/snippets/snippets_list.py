import click
from libtmux.exc import LibTmuxException
from rich import box
from rich.console import Console
from rich.table import Table

from sshtmux.services.snippets import get_snippets_files

HELP = "List Snippets"


@click.command(name="list", short_help=HELP, help=HELP)
def cmd():
    console = Console()
    table = Table(box=box.SQUARE, style="gray35")
    table.add_column("Snippets")
    snippets, _ = get_snippets_files()
    for snippet in snippets:
        if snippet == "Cancel":
            continue
        table.add_row(snippet)
    console.print(table)
