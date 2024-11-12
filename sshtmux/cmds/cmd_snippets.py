import click

from .snippets import snippets_list, snippets_run


# ------------------------------------------------------------------------------
# Identity Commands
# ------------------------------------------------------------------------------
@click.group(name="snippets", help="Execute a Snippet")
def generate():
    pass


# // Linking other sub-commands
generate.add_command(snippets_run.cmd)
generate.add_command(snippets_list.cmd)
