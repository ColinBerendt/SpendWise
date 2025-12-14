import os

from agents.mcp import MCPServerStdio

from ._utils import _id_generator
from .errors import InvalidRuntimePermission
from .mcp_manifest import DevMCPManifest, MCPManifest
from .runtime_permissions import (
    DomainPort,
    EnvironmentVariable,
    FSAccess,
    HostPort,
    RuntimePermission,
)

_sandbox_version = "latest"


def set_sandbox_version(version: str) -> None:
    """
    Set a specific version for the sandbox docker image.
    Defaults to "latest".
    """
    global _sandbox_version
    _sandbox_version = version


class SandboxedMCPStdio(MCPServerStdio):
    def __init__(
        self,
        manifest: MCPManifest,
        name: str | None = None,
        runtime_args: list[str] | None = None,
        runtime_permissions: list[RuntimePermission] = [],
        static_environment_vars: dict[str, str] = {},
        client_session_timeout_seconds: int = 60,
        remove_container_after_run: bool = True,
    ):
        # Check the permissions in the manifest against the runtime permissions.
        # If some are off, throw an error.
        illegal = [
            p
            for p in runtime_permissions
            if not p.validate_with_manifest_perms(manifest.permissions)
        ]
        if illegal:
            raise InvalidRuntimePermission(manifest.permissions, illegal)

        # Then, for each runtime permission, ask the user via input, if the permission is allowed or not.
        # Only attach the permissions that the user gave the consent to.
        consented_perms = [p for p in runtime_permissions if p.get_user_consent()]

        allowed_egress = ",".join(
            [
                f"{p.domain}:{p.port}"
                for p in consented_perms
                if isinstance(p, DomainPort)
            ]
            + [f"{p.host}:{p.port}" for p in consented_perms if isinstance(p, HostPort)]
        )

        add_args = []
        if isinstance(manifest, DevMCPManifest):
            add_args.extend(
                [
                    "--mount",
                    f"type=bind,src={manifest.code_mount},dst=/sandbox",
                    "-e",
                    "PRE_INSTALLED=true",
                    "-e",
                    f"EXE={manifest.exec_command}",
                ]
            )

        args = [
            "run",
            *(["--rm"] if remove_container_after_run else []),
            "-i",
            "--cap-add=NET_ADMIN",
            "-e",
            f"PACKAGE={manifest.package_name}",
            *sum(
                [
                    [
                        "--mount",
                        f"type=bind,src={fs.path},dst={fs.container_path or fs.path}"
                        + ("" if fs.write else ",readonly"),
                    ]
                    for fs in consented_perms or []
                    if isinstance(fs, FSAccess)
                ],
                [],
            ),
            *(["-e", f"ALLOWED_EGRESS={allowed_egress}"] if allowed_egress else []),
            *sum(
                [
                    ["-e", f"{p.name}={os.environ.get(p.name)}"]
                    for p in consented_perms or []
                    if isinstance(p, EnvironmentVariable)
                ],
                [],
            ),
            *sum(
                [["-e", f"{k}={v}"] for k, v in static_environment_vars.items()],
                [],
            ),
            *add_args,
            f"ghcr.io/guardiagent/mcp-sandbox-{manifest.registry}:{_sandbox_version}",
            *(runtime_args if runtime_args else []),
        ]

        super().__init__(
            name=name or f"{manifest.name} - {_id_generator()}",
            params={
                "command": "docker",
                "args": args,
            },
            client_session_timeout_seconds=client_session_timeout_seconds,
        )
