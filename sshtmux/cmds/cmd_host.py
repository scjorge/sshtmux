import click

from .host import (
    host_create,
    host_delete,
    host_list,
    host_rename,
    host_run,
    host_set,
    host_show,
)


# ------------------------------------------------------------------------------
# HOST Commands
# ------------------------------------------------------------------------------
@click.group(name="host", help="Command group for managing hosts")
def ssh_host():
    pass


# // Linking other sub-commands

ssh_host.add_command(host_create.cmd)
ssh_host.add_command(host_delete.cmd)
ssh_host.add_command(host_list.cmd)
ssh_host.add_command(host_set.cmd)
ssh_host.add_command(host_show.cmd)
ssh_host.add_command(host_rename.cmd)
ssh_host.add_command(host_run.cmd)
