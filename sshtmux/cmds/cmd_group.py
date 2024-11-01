import click

from .group import (
    group_create,
    group_delete,
    group_list,
    group_rename,
    group_set,
    group_show,
)


# ------------------------------------------------------------------------------
# GROUP Commands
# ------------------------------------------------------------------------------
@click.group(name="group", help="Command group for managing groups")
def ssh_group():
    pass


# // Linking other sub-commands
ssh_group.add_command(group_create.cmd)
ssh_group.add_command(group_delete.cmd)
ssh_group.add_command(group_list.cmd)
ssh_group.add_command(group_set.cmd)
ssh_group.add_command(group_show.cmd)
ssh_group.add_command(group_rename.cmd)
