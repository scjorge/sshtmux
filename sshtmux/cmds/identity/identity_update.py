import click

from sshtmux.exceptions import IdentityException
from sshtmux.services.identities import PasswordManager

HELP = "Update Identity"


@click.command(name="update", short_help=HELP, help=HELP)
@click.argument("identity")
@click.argument("password")
def cmd(identity, password):
    password_manager = PasswordManager()
    try:
        password_manager.set_password(identity, password, True)
    except IdentityException as e:
        print(str(e))
        return

    print(f"Identity {identity} updated")