import click

from sshtmux.sshm import SSH_Config, complete_ssh_group_names

# ------------------------------------------------------------------------------
# COMMAND: group set
# ------------------------------------------------------------------------------
SHORT_HELP = "Change group parameters"
LONG_HELP = """
Change/modify group parameters

Command allows to modify current information on the group, like info lines
and description. To rename group, use command "sshm group rename" command.
To move hosts between group, use "sshm host set" command.
"""

# Parameters help:
DESC_HELP = "Short description of group"
INFO_HELP = "Info line, can be set multiple times"
# ------------------------------------------------------------------------------


@click.command(name="set", short_help=SHORT_HELP, help=LONG_HELP)
@click.option("-d", "--desc", help=DESC_HELP)
@click.option("-i", "--info", multiple=True, help=INFO_HELP)
@click.argument("name", shell_complete=complete_ssh_group_names)
@click.pass_context
def cmd(ctx, name, desc, info):
    config: SSH_Config = ctx.obj

    # Nothing was provided
    if not desc and not info:
        click.echo("Calling set on group without specifying any option is not valid!")
        click.echo("Run 'sshm group set -h' for help.")
        ctx.exit(1)

    if not config.check_group_by_name(name):
        click.echo(f"Cannot modify group '{name}', it is not defined in configuration!")
        ctx.exit(1)

    found_group = config.get_group_by_name(name)

    # If new description is set
    if desc:
        found_group.desc = desc.strip()

    # Assuming when "clearing" config only single info is given... we check first info
    # and check if it's empty/falsy. If it is non-empty, we check all of values and if
    # they are non empty we append to existing lines.... if first item is empty we clear the info data
    if info and info[0]:
        for line in info:
            if len(line.strip()) > 0:
                found_group.info.append(line)
    else:
        found_group.info = []

    config.generate_ssh_config().write_out()

    if not config.stdout:
        click.echo(f"Modified group: {name}")
