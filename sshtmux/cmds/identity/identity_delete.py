import click

from sshtmux.exceptions import IdentityException
from sshtmux.services.identities import PasswordManager
from sshtmux.sshm import complete_identities

HELP = "Delete Identity"


@click.command(name="delete", short_help=HELP, help=HELP)
@click.argument("identity", shell_complete=complete_identities)
def cmd(identity):
    password_manager = PasswordManager()
    try:
        password_manager.delete_password(identity)
    except IdentityException as e:
        print(str(e))
        return

    print(f"Identity {identity} deleted")
