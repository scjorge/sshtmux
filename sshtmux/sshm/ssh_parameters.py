import os
import re
from typing import Literal, Optional

from pydantic import BaseModel, IPvAnyAddress, field_validator, model_validator

CIPHERS = [
    "3des-cbc",
    "aes128-cbc",
    "aes192-cbc",
    "aes256-cbc",
    "aes128-ctr",
    "aes192-ctr",
    "aes256-ctr",
    "aes128-gcm@openssh.com",
    "aes256-gcm@openssh.com",
    "chacha20-poly1305@openssh.com",
]
CASIGNATUREALGORITHMS = [
    "+",
    "-",
    "ssh-ed25519",
    "ecdsa-sha2-nistp256",
    "ecdsa-sha2-nistp384",
    "ecdsa-sha2-nistp521",
    "sk-ssh-ed25519@openssh.com",
    "sk-ecdsa-sha2-nistp256@openssh.com",
    "rsa-sha2-512",
    "rsa-sha2-256",
]
KEX_ALGORITHMS = [
    "sntrup761x25519-sha512@openssh.com",
    "curve25519-sha256",
    "curve25519-sha256@libssh.org",
    "ecdh-sha2-nistp256",
    "ecdh-sha2-nistp384",
    "ecdh-sha2-nistp521",
    "diffie-hellman-group-exchange-sha256",
    "diffie-hellman-group16-sha512",
    "diffie-hellman-group18-sha512",
    "diffie-hellman-group14-sha256",
]
MAC_ALGORITHMS = [
    "hmac-sha2-256",
    "hmac-sha2-512",
    "hmac-sha1",
    "umac-64@openssh.com",
    "umac-128@openssh.com",
]
BASEALGORITHMS = [
    "ssh-ed25519-cert-v01@openssh.com",
    "ecdsa-sha2-nistp256-cert-v01@openssh.com",
    "ecdsa-sha2-nistp384-cert-v01@openssh.com",
    "ecdsa-sha2-nistp521-cert-v01@openssh.com",
    "sk-ssh-ed25519-cert-v01@openssh.com",
    "sk-ecdsa-sha2-nistp256-cert-v01@openssh.com",
    "rsa-sha2-512-cert-v01@openssh.com",
    "rsa-sha2-256-cert-v01@openssh.com",
    "ssh-ed25519",
    "ecdsa-sha2-nistp256",
    "ecdsa-sha2-nistp384",
    "ecdsa-sha2-nistp521",
    "sk-ssh-ed25519@openssh.com",
    "sk-ecdsa-sha2-nistp256@openssh.com",
    "rsa-sha2-512",
    "rsa-sha2-256",
]
IPQOS = [
    "af11",
    "af12",
    "af13",
    "af21",
    "af22",
    "af23",
    "af31",
    "af32",
    "af33",
    "af41",
    "af42",
    "af43",
    "cs0",
    "cs1",
    "cs2",
    "cs3",
    "cs4",
    "cs5",
    "cs6",
    "cs7",
    "ef",
    "le",
    "lowdelay",
    "throughput",
    "reliability",
    "none",
]
KBDINTERACTIVEDEVICES = ["pam", "bsdauth", "skey", "null", "default"]
LOG_LEVEL = [
    "QUIET",
    "FATAL",
    "ERROR",
    "INFO",
    "VERBOSE",
    "DEBUG",
    "DEBUG1",
    "DEBUG2",
    "DEBUG3",
]
PREFERREDAUTHENTICATIONS = [
    "gssapi-with-mic",
    "hostbased",
    "publickey",
    "keyboard-interactive",
    "password",
]
STRICTHOSTKEYCHECKING = Literal["yes", "no", "ask", "accept-new", "off"]
YES_NO = Literal["yes", "no"]
SYSLOGFACILITY = Literal[
    "DAEMON",
    "USER",
    "AUTH",
    "LOCAL0",
    "LOCAL1",
    "LOCAL2",
    "LOCAL3",
    "LOCAL4",
    "LOCAL5",
    "LOCAL6",
    "LOCAL7",
]
PORT_RANGE = (1, 65535)
SSH_HOSTNAME_REGEX = r"^[a-zA-Z0-9.-]+$"


class SSHParams(BaseModel):
    AddKeysToAgent: Optional[Literal["yes", "no", "ask", "confirm"]] = None
    AddressFamily: Optional[Literal["any", "inet", "inet6"]] = None
    BatchMode: Optional[YES_NO] = None
    BindAddress: Optional[IPvAnyAddress] = None
    BindInterface: Optional[str] = None
    CanonicalDomains: Optional[str] = None
    CanonicalizeFallbackLocal: Optional[YES_NO] = None
    CanonicalizeHostname: Optional[YES_NO] = None
    CanonicalizeMaxDots: Optional[str] = None
    CanonicalizePermittedCNAMEs: Optional[str] = None
    CASignatureAlgorithms: Optional[str] = None
    CertificateFile: Optional[str] = None
    ChannelTimeout: Optional[str] = None
    CheckHostIP: Optional[YES_NO] = None
    Ciphers: Optional[str] = None
    ClearAllForwardings: Optional[YES_NO] = None
    Compression: Optional[YES_NO] = None
    ConnectionAttempts: Optional[str] = None
    ConnectTimeout: Optional[str] = None
    ControlMaster: Optional[Literal["yes", "no", "ask", "auto", "autoask"]] = None
    ControlPath: Optional[str] = None
    ControlPersist: Optional[YES_NO] = None
    DynamicForward: Optional[str] = None
    EnableEscapeCommandline: Optional[str] = None
    EnableSSHKeysign: Optional[YES_NO] = None
    EscapeChar: Optional[str] = None
    ExitOnForwardFailure: Optional[YES_NO] = None
    FingerprintHash: Optional[Literal["sha256", "md5"]] = None
    ForkAfterAuthentication: Optional[YES_NO] = None
    ForwardAgent: Optional[YES_NO] = None
    ForwardX11: Optional[YES_NO] = None
    ForwardX11Timeout: Optional[str] = None
    ForwardX11Trusted: Optional[YES_NO] = None
    GatewayPorts: Optional[YES_NO] = None
    GlobalKnownHostsFile: Optional[str] = None
    GSSAPIAuthentication: Optional[YES_NO] = None
    GSSAPIKeyExchange: Optional[str] = None
    GSSAPIClientIdentity: Optional[str] = None
    GSSAPIDelegateCredentials: Optional[str] = None
    GSSAPIKexAlgorithms: Optional[str] = None
    GSSAPIRenewalForcesRekey: Optional[str] = None
    GSSAPIServerIdentity: Optional[str] = None
    GSSAPITrustDns: Optional[str] = None
    HashKnownHosts: Optional[YES_NO] = None
    HostbasedAcceptedAlgorithms: Optional[str] = None
    HostbasedAuthentication: Optional[YES_NO] = None
    HostKeyAlgorithms: Optional[str] = None
    HostKeyAlias: Optional[str] = None
    Hostname: Optional[str] = None
    IdentitiesOnly: Optional[YES_NO] = None
    IdentityAgent: Optional[str] = None
    IdentityFile: Optional[str] = None
    IgnoreUnknown: Optional[str] = None
    Include: Optional[str] = None
    IPQoS: Optional[str] = None
    KbdInteractiveAuthentication: Optional[YES_NO] = None
    KbdInteractiveDevices: Optional[str] = None
    KexAlgorithms: Optional[str] = None
    KnownHostsCommand: Optional[str] = None
    LocalCommand: Optional[str] = None
    LocalForward: Optional[str] = None
    LogLevel: Optional[str] = None
    LogVerbose: Optional[str] = None
    MACs: Optional[str] = None
    NoHostAuthenticationForLocalhost: Optional[YES_NO] = None
    NumberOfPasswordPrompts: Optional[str] = None
    ObscureKeystrokeTiming: Optional[YES_NO] = None
    PasswordAuthentication: Optional[YES_NO] = None
    PermitLocalCommand: Optional[YES_NO] = None
    PermitRemoteOpen: Optional[str] = None
    PKCS11Provider: Optional[str] = None
    Port: Optional[str] = None
    PreferredAuthentications: Optional[str] = None
    ProxyCommand: Optional[str] = None
    ProxyJump: Optional[str] = None
    ProxyUseFdpass: Optional[YES_NO] = None
    PubkeyAcceptedAlgorithms: Optional[str] = None
    PubkeyAuthentication: Optional[Literal["yes", "no", "unbound", "host-bound"]] = None
    RekeyLimit: Optional[str] = None
    RemoteCommand: Optional[str] = None
    RemoteForward: Optional[str] = None
    RequestTTY: Optional[Literal["yes", "no", "force", "auto"]] = None
    RequiredRSASize: Optional[str] = None
    RevokedKeys: Optional[str] = None
    RevokedHostKeys: Optional[str] = None
    SecurityKeyProvider: Optional[str] = None
    SendEnv: Optional[str] = None
    ServerAliveCountMax: Optional[str] = None
    ServerAliveInterval: Optional[str] = None
    SessionType: Optional[str] = None
    StdinNull: Optional[YES_NO] = None
    StreamLocalBindMask: Optional[str] = None
    StreamLocalBindUnlink: Optional[YES_NO] = None
    StrictHostKeyChecking: Optional[STRICTHOSTKEYCHECKING] = None
    SyslogFacility: Optional[SYSLOGFACILITY] = None
    Tag: Optional[str] = None
    TCPKeepAlive: Optional[YES_NO] = None
    Tunnel: Optional[Literal["yes", "no", "point-to-point", "ethernet"]] = None
    TunnelDevice: Optional[str] = None
    UpdateHostKeys: Optional[Literal["yes", "no", "ask"]] = None
    User: Optional[str] = None
    UserKnownHostsFile: Optional[str] = None
    VerifyHostKeyDNS: Optional[STRICTHOSTKEYCHECKING] = None
    VisualHostKey: Optional[YES_NO] = None
    XAuthLocation: Optional[str] = None

    class Config:
        extra = "forbid"

    @staticmethod
    def validate_list_values(v, list_values, divisor=","):
        if v:
            values = v.split(divisor)
            for value in values:
                if value not in list_values:
                    raise ValueError(f"Value list should be one of: {list_values}")
        return v

    @staticmethod
    def is_valid_time_format(value: str) -> None:
        if value == "0":
            return
        pattern = re.compile(r"^(\d+[smhdwSMHDW]?)+$")
        is_valid = bool(pattern.match(value))
        if not is_valid:
            raise ValueError(f"Invalid Time Format: {value}")

    @staticmethod
    def is_valid_bind(value: str) -> bool:
        pattern = r"^((\d{1,3}\.){3}\d{1,3}|\[::1\]|0\.0\.0\.0)?(:)?(\d+)$"
        match = re.match(pattern, value)
        if not match:
            raise ValueError("Invalid format. must be [bind_address:]port")

        port_str = match.group(4)
        if port_str is None:
            raise ValueError(f"Port not found: {value}")

        port = int(port_str)
        if not (PORT_RANGE[0] <= port <= PORT_RANGE[1]):
            raise ValueError(f"Port must be (1-65535): {port}")

    @staticmethod
    def is_valid_string_integer(value: str) -> None:
        if not isinstance(value, str) or value.startswith("0"):
            raise ValueError(f"Invalid number. Can not starts with 0: {value}")
        try:
            value = int(value)
        except ValueError:
            raise ValueError(f"Should be a integer number: {value}")
        if not value >= 1:
            raise ValueError("Shoud be greater then 0")

    @model_validator(mode="before")
    def validate_all_fields(cls, values):
        new_values = {k.strip(): v.strip() for k, v in values.items()}
        for field, value in new_values.items():
            if value == "":
                raise ValueError(f"{field} Can not be empty string")
        return new_values

    @field_validator("Hostname")
    def validate_hostname(cls, v):
        try:
            IPvAnyAddress(v)
        except ValueError:
            domain_pattern = re.compile(SSH_HOSTNAME_REGEX)
            if not domain_pattern.match(v):
                raise ValueError(f"Hostname invalid: {v}")
        return v

    @field_validator("Port")
    def validate_port(cls, v):
        SSHParams.is_valid_string_integer(v)
        if not (PORT_RANGE[0] <= int(v) <= PORT_RANGE[1]):
            raise ValueError(f"Port must be (1-65535): {v}")
        return v

    @field_validator("ControlPersist")
    def validate_controlpersist(cls, v):
        if v in ["yes", "no", "auto"]:
            return v
        SSHParams.is_valid_time_format(v)
        return v

    @field_validator("DynamicForward", "PermitRemoteOpen")
    def validate_dynamic_forward(cls, v):
        SSHParams.is_valid_bind(v)

    @field_validator(
        "ConnectionAttempts",
        "ConnectTimeout",
        "ServerAliveCountMax",
        "ServerAliveInterval",
        "CanonicalizeMaxDots",
        "NumberOfPasswordPrompts",
        "RequiredRSASize",
    )
    def validate_greater_then_0(cls, v):
        SSHParams.is_valid_string_integer(v)
        return v

    @field_validator("ChannelTimeout", "ForwardX11Timeout")
    def validate_greater_then_0_and_time_formats(cls, v):
        SSHParams.is_valid_string_integer(v)
        SSHParams.is_valid_time_format(v)
        return v

    @field_validator("CASignatureAlgorithms")
    def validate_casignaturealgorithms(cls, v):
        SSHParams.validate_list_values(v, CASIGNATUREALGORITHMS)
        return v

    @field_validator(
        "HostbasedAuthentication",
        "HostbasedAcceptedAlgorithms",
        "HostKeyAlgorithms",
        "PubkeyAcceptedAlgorithms",
    )
    def validate_hostbasedacceptedalgorithms(cls, v):
        SSHParams.validate_list_values(v, BASEALGORITHMS)
        return v

    @field_validator("Ciphers")
    def validate_ciphers(cls, v):
        SSHParams.validate_list_values(v, CIPHERS)
        return v

    @field_validator("KexAlgorithms")
    def validate_kexs(cls, v):
        SSHParams.validate_list_values(v, KEX_ALGORITHMS)
        return v

    @field_validator("IPQoS")
    def validate_ipqos(cls, v):
        SSHParams.validate_list_values(v, IPQOS, " ")
        return v

    @field_validator("KbdInteractiveDevices")
    def validate_kbdinteractivedevices(cls, v):
        SSHParams.validate_list_values(v, KBDINTERACTIVEDEVICES)
        return v

    @field_validator("LogLevel")
    def validate_loglevel(cls, v):
        SSHParams.validate_list_values(v, LOG_LEVEL)
        return v

    @field_validator("MACs")
    def validate_macs(cls, v):
        SSHParams.validate_list_values(v, MAC_ALGORITHMS)
        return v

    @field_validator("PreferredAuthentications")
    def validate_preferredauthentications(cls, v):
        SSHParams.validate_list_values(v, PREFERREDAUTHENTICATIONS)
        return v

    @field_validator("RekeyLimit")
    def validate_rekey_limit(cls, v):
        pattern = r"^(\d+)([kKmMgGhHs])$"
        match = re.match(pattern, v.strip())
        if match:
            number = int(match.group(1))
            unit = match.group(2).lower()
            valid_units = ["k", "m", "g", "h", "s"]
            if unit in valid_units and number > 0:
                return True
        raise ValueError(f"Invalid Format: {v}")

    @field_validator(
        "IdentityFile",
        "CertificateFile",
        "UserKnownHostsFile",
        "GlobalKnownHostsFile",
        "PKCS11Provider",
        "ControlPath",
        "RevokedHostKeys",
        "RevokedKeys",
        "SecurityKeyProvider",
    )
    def validate_path(cls, v):
        if v and not os.path.exists(v):
            raise ValueError(f"File or Path does not exits: {v}")
        return v

    @field_validator("LocalForward", "RemoteForward")
    def validate_forward(cls, v):
        pattern = r"^(\d+)\s+((localhost|[\w.-]+|\[.*\])):(\d+)$"
        match = re.match(pattern, v)

        if not match:
            raise ValueError(
                "Invalid format. Expected format: <port> <host>:<port> (e.g., '4000 localhost:4000')"
            )

        local_port, host, _, remote_port = match.groups()
        if local_port.startswith("0"):
            raise ValueError(f"Invalid Port number: {local_port}")
        if remote_port.startswith("0"):
            raise ValueError(f"Invalid Port number: {remote_port}")

        local_port = int(local_port)
        remote_port = int(remote_port)

        if not (PORT_RANGE[0] <= local_port <= PORT_RANGE[1]):
            raise ValueError(
                f"Local port must be between {PORT_RANGE[0]} and {PORT_RANGE[1]}: {local_port}"
            )
        if not (PORT_RANGE[0] <= remote_port <= PORT_RANGE[1]):
            raise ValueError(
                f"Remote port must be between {PORT_RANGE[0]} and {PORT_RANGE[1]}: {remote_port}"
            )
        if not re.match(SSH_HOSTNAME_REGEX, host):
            raise ValueError(
                f"Invalid hostname format for SSH: {host}. It must follow the SSH hostname rules."
            )
        return v
