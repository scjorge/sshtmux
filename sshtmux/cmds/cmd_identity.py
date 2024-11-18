import click

from .identity import (
    identity_create,
    identity_delete,
    identity_generate,
    identity_list,
    identity_run,
    identity_update,
)


# ------------------------------------------------------------------------------
# Identity Commands
# ------------------------------------------------------------------------------
@click.group(name="identity", help="Command group for managing identities")
def generate():
    pass


# // Linking other sub-commands
generate.add_command(identity_generate.cmd)
generate.add_command(identity_list.cmd)
generate.add_command(identity_create.cmd)
generate.add_command(identity_update.cmd)
generate.add_command(identity_delete.cmd)
generate.add_command(identity_run.cmd)
