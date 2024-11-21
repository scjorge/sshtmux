from sshtmux.sshm import SSH_Config, SSH_Group, SSH_Host

#-----------------------------------
# FILE CONTENT SAMPLES FOR PARSING
#-----------------------------------
# Configuration with all lowercase
config1="""
#@host: testinfo
host test
    hostname 1.2.3.4
    port 2222
    user testUSER
"""

# Configuration with alternate style - 1
config_s1="""
# host: testinfo
host test
    hostname 1.2.3.4
    port 2222
    user testUSER
"""
# Configuration with alternate style - 2
config_s2="""
#host  :testinfo
host test
    hostname 1.2.3.4
    port 2222
    user testUSER
"""


# All parsed configuration should result with lowercased keywords for parameters
# while values should be kept case-sensitive
results = [
    SSH_Group(name="default", desc="Default group", hosts=[
        SSH_Host(name="test", group="default", info=["testinfo"], params={
            "hostname":"1.2.3.4",
            "port":"2222",
            "user":"testUSER",
        })
    ])
]


#-----------------------------------
# Tests
#-----------------------------------
def test_parse_lowercase():
    lines = config1.splitlines()
    groups = SSH_Config(lines).parse().groups
    assert groups == results

def test_parse_altstyle1():
    lines = config_s1.splitlines()
    groups = SSH_Config(lines).parse().groups
    assert groups == results

def test_parse_altstyle2():
    lines = config_s2.splitlines()
    groups = SSH_Config(lines).parse().groups
    assert groups == results
