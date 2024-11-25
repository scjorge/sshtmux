from dataclasses import dataclass, field
from typing import List

from .ssh_host import SSH_Host


@dataclass
class SSH_Group:
    """Class for SSH Group config structure"""

    name: str
    desc: str = ""
    info: list = field(default_factory=list)
    hosts: List[SSH_Host] = field(default_factory=list)
    patterns: List[SSH_Host] = field(default_factory=list)

    print_style: str = ""

    def deep_filter(self, value: str) -> bool:
        """
        Method returns bool value
        This filter any match value with name, desc ou info
        """
        values = [self.name, self.desc] + self.info
        return any(
            string_part in item for item in values for string_part in value.split()
        )

    def __rich__(self):
        pass
