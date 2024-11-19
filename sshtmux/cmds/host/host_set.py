import click

from sshtmux.sshm import (
    SSH_Config,
    SSH_Group,
    complete_params,
    complete_ssh_group_names,
    complete_ssh_host_names,
)
from sshtmux.sshm.sshutils import validate_ssh_params, validate_unique_param

# ------------------------------------------------------------------------------
# COMMAND: host set
# ------------------------------------------------------------------------------
SHORT_HELP = "Set/Change host configuration"
LONG_HELP = """
Set/Change host definitions and parameters

If autocompletion is enabled, command will also offer current configured hosts for TAB completion.
"""

INFO_HELP = "Set host info, can be set multiple times, or set to empty value to clear it (example: -i '')"
SET_PARAM_HELP = "Sets parameter for the host, takes 2 values (<sshparam> <value>)"
UNSET_PARAM_HELP = "Unsets/Remove parameter for the host, takes 1 value <sshparam>"
GROUP_HELP = "Group change for host. Moves one or many hosts from their groups (they can be in different ones) to specified group."
FORCE_HELP = "Allows during group host group change, to move host(s) to group that does not exist, by creating it automatically, and moving specified hosts to new group."
# ------------------------------------------------------------------------------


@click.command(name="set", short_help=SHORT_HELP, help=LONG_HELP)
@click.option("-i", "--info", multiple=True, help=INFO_HELP)
@click.option(
    "-p",
    "--parameter",
    nargs=2,
    multiple=True,
    help=SET_PARAM_HELP,
    shell_complete=complete_params,
)
@click.option(
    "-r",
    "--remove-parameter",
    nargs=1,
    multiple=True,
    help=UNSET_PARAM_HELP,
    shell_complete=complete_params,
)
@click.option(
    "-g",
    "--group",
    "target_group_name",
    help=GROUP_HELP,
    shell_complete=complete_ssh_group_names,
)
@click.option("-f", "--force", is_flag=True, help=FORCE_HELP)
@click.argument("name", nargs=1, required=True, shell_complete=complete_ssh_host_names)
@click.pass_context
def cmd(ctx, name, info, parameter, remove_parameter, target_group_name, force):
    config: SSH_Config = ctx.obj

    if not config.check_host_by_name(name, False):
        print(
            f"Cannot set anything on host '{name}' as it is not defined in configuration!"
        )
        ctx.exit(1)

    found_host, found_group = config.get_host_by_name(name)

    if target_group_name:
        target_group_exists = config.check_group_by_name(target_group_name)
        if not target_group_exists and not force:
            print(
                f"Cannot move host '{name}' to group '{target_group_name}' which does not exist!"
            )
            print(
                "Consider using --force to automatically create target group, or create it manually first."
            )
            ctx.exit(1)
        elif not target_group_exists:
            target_group = SSH_Group(name=target_group_name)
            config.groups.append(target_group)
        else:
            target_group = config.get_group_by_name(target_group_name)

        config.move_host_to_group(found_host, found_group, target_group)

    if info:
        if len(info[0]) > 0:
            found_host.info = found_host.info + list(info)
        else:
            found_host.info = []

    valid_ssh_params = validate_ssh_params(parameter)
    validate_unique_param(found_host.params, valid_ssh_params)

    for param, value in valid_ssh_params.items():
        found_host.params[param] = value

    for param in remove_parameter:
        try:
            del found_host.params[param]
        except KeyError:
            print(f"Parameter: {param} not found to be removed. Ignoring...")

    if not config.stdout:
        print(f"Modified host: {name}")

    config.generate_ssh_config().write_out()
