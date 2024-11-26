import click
from rich import print

from sshtmux.services.identities import KeyManager

HELP = "Generate a Fernet key - 32 url-safe"


@click.command(name="generate-key", short_help=HELP, help=HELP)
def cmd():
    key = KeyManager.generate_key().decode()
    output = f"""
    [bold yellow]Warning[/bold yellow]: When saving identities using a key, you cannot recover passwords without the corresponding key.
    If you have already saved passwords and are using the [u]~/.config/sshtmux/identity.key[/u] file, you can configure this key by setting the [u]SSHTMUX_IDENTITY_KEY[/u] environment variable.
    Otherwise, you can generate a new key below.

    Set the environment variable [u]SSHTMUX_IDENTITY_KEY[/u].

    Your key:

    {key}
    """
    print(output)
