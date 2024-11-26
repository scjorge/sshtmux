import click
from rich import box
from rich.console import Console
from rich.table import Table

from sshtmux.services.identities import PasswordManager

HELP = "List all Identities"


@click.command(name="list", short_help=HELP, help=HELP)
def cmd():
    try:
        password_manager = PasswordManager()
        identies = password_manager.get_identities()
    except Exception as e:
        click.echo(str(e))
        exit(1)

    console = Console()
    table = Table(box=box.SQUARE, style="gray35")
    table.add_column("Identity")
    for identity in identies:
        table.add_row(identity)

    console.print(table)
