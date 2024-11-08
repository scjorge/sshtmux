import click

from .identity import identity_generate


# ------------------------------------------------------------------------------
# Identity Commands
# ------------------------------------------------------------------------------
@click.group(name="identity", help="Manager Identities")
def generate():
    pass


# // Linking other sub-commands
generate.add_command(identity_generate.cmd)
