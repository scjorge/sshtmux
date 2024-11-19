import click

from sshtmux.sshm import (
    SSH_Config,
    SSH_Group,
    SSH_Host,
    complete_params,
    complete_ssh_group_names,
)
from sshtmux.sshm.sshutils import validate_ssh_params

# ------------------------------------------------------------------------------
# COMMAND: host create
# ------------------------------------------------------------------------------
SHORT_HELP = "Create new host"
LONG_HELP = """
Create new host and save it to config file

Command can be used to create a single HOST definition, and also set definitions within single command.
Later definitions can be changes with "sshm host set" commands.

If autocomplete is enabled, command will try to give suggestions for your inputs on definition of GROUP and well known PARAM names.
"""

# Parameters help:
INFO_HELP = "Set host info, can be set multiple times, or set to empty value to clear it (example: -i '')"
PARAM_HELP = "Sets parameter for the host, takes 2 values (<sshparam> <value>)."
GROUP_HELP = "Defined in which group host will be created, if not specified, 'default' group will be used"
FORCE_HELP = "Allows during host creation, to create group for host if target group is missing/not yet defined."
# ------------------------------------------------------------------------------


@click.command(name="create", short_help=SHORT_HELP, help=LONG_HELP)
@click.option("-i", "--info", multiple=True, help=INFO_HELP)
@click.option(
    "-p",
    "--parameter",
    nargs=2,
    multiple=True,
    help=PARAM_HELP,
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
@click.argument("name")
@click.pass_context
def cmd(ctx, name, info, parameter, target_group_name, force):
    config: SSH_Config = ctx.obj

    if not target_group_name:
        target_group_name = SSH_Config.DEFAULT_GROUP_NAME
    else:
        if not name.startswith(f"{target_group_name}-"):
            name = f"{target_group_name}-{name}"

    if config.check_host_by_name(name):
        print(f"Cannot create host '{name}' as it already exists in configuration!")
        ctx.exit(1)

    # Find group by name where to store config
    target_group_exists = config.check_group_by_name(target_group_name)

    if not target_group_exists and not force:
        print(
            f"Cannot create host '{name}' in group '{target_group_name}' since the group does not exist"
        )
        print("Create group first, or use '--force' option to create it automatically!")
        ctx.exit(1)
        # unreachable, but avoids issues with static checks
        exit(1)
    elif not target_group_exists:
        target_group = SSH_Group(name=target_group_name)
        config.groups.append(target_group)

        # Create group parttern host
        new_host = SSH_Host(
            name=f"{target_group_name}-*",
            group=target_group_name,
            type="pattern",
            info=[],
        )
        target_group.patterns.append(new_host)
    else:
        target_group = config.get_group_by_name(target_group_name)

    # This is patter host
    target_type = "pattern" if "*" in name else "normal"
    new_host = SSH_Host(
        name=name, group=target_group_name, type=target_type, info=list(info)
    )

    # Add all passed parameters to config
    valid_ssh_params = validate_ssh_params(parameter)
    for param, value in valid_ssh_params.items():
        new_host.params[param] = value

    # Append new host to the group
    if new_host.type == "normal":
        target_group.hosts.append(new_host)
    else:
        target_group.patterns.append(new_host)

    # Generate new config
    config.generate_ssh_config().write_out()

    if not config.stdout:
        print(f"Created host: {name}")
