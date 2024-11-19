import click
from rich import box
from rich.console import Console
from rich.table import Table

from sshtmux.exceptions import IdentityException
from sshtmux.services.identities import PasswordManager

HELP = "List all Identities"


@click.command(name="list", short_help=HELP, help=HELP)
def cmd():
    password_manager = PasswordManager()
    identies = password_manager.get_identities()
    try:
        identies = password_manager.get_identities()
    except IdentityException as e:
        print(str(e))
        return
    console = Console()
    table = Table(box=box.SQUARE, style="gray35")
    table.add_column("Identity")
    for identity in identies:
        table.add_row(identity)

    console.print(table)
