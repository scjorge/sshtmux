import click
from rich import print
from rich.prompt import Prompt

from sshtmux.exceptions import IdentityException
from sshtmux.services.identities import PasswordManager
from sshtmux.sshm import complete_identities

HELP = "Update Identity"


@click.command(name="update", short_help=HELP, help=HELP)
@click.argument("identity", shell_complete=complete_identities)
def cmd(identity):
    password_manager = PasswordManager()
    password = Prompt.ask("Type Password", password=True)
    try:
        password_manager.set_password(identity, password, True)
    except IdentityException as e:
        print(str(e))
        return

    print(f"Identity {identity} updated")
