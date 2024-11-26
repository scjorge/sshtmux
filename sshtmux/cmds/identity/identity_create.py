import click
from rich.prompt import Prompt

from sshtmux.exceptions import IdentityException
from sshtmux.services.identities import PasswordManager

HELP = "Create Identity"


@click.command(name="create", short_help=HELP, help=HELP)
@click.argument("identity")
def cmd(identity):
    password_manager = PasswordManager()
    password = Prompt.ask("Type Password", password=True)
    try:
        password_manager.set_password(identity, password)
    except IdentityException as e:
        click.echo(str(e))
        exit(1)

    click.echo(f"Identity {identity} created")
