import click

from sshtmux.services.identities import KeyManager

HELP = "Generate a Fernet key - 32 url-safe"


@click.command(name="generate-key", short_help=HELP, help=HELP)
def cmd():
    key = KeyManager.generate_key().decode()
    output = f"""
    Be careful, when saving identities using a key, you cannot recover passwords without the key.
    If you have saved passwords and are using the ~/.config/sshtmux/identity.key file, you can configure the key of this file in the env var 'SSHTMUX_IDENTITY_KEY'.
    Otherwise you can use a new key belowS

    Set the env var SSHTMUX_IDENTITY_KEY

    Your key:

    {key}
    """
    print(output)
