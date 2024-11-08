import click

from sshtmux.services.identities import KeyManager

HELP = "Generate a Fernet key - 32 url-safe"


@click.command(name="generate-key", short_help=HELP, help=HELP)
def cmd():
    key = KeyManager.generate_key().decode()
    output = f"""
    Set the env var SSHTMUX_IDENTITY_KEY

    Your key:

    {key}
    """
    print(output)
