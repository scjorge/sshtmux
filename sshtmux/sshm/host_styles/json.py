import json

from rich.json import JSON

from ..ssh_host import SSH_Host


# ------------------------------------------------------------------------------
# Render host data as JSON output
# ------------------------------------------------------------------------------
def render(host: SSH_Host):
    host_json = json.dumps(host.__dict__)
    return JSON(host_json)
