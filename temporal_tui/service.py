import os
import tomllib
import typing

import platformdirs
import temporalio.client

from temporal_tui.models import Workflow


class MissingRequiredError(Exception):
    def __init__(self, required: str):
        super().__init__(f"Missing required parameter '{required}'.")


class TemporalService:
    def __init__(
        self,
        address: str,
        namespace: str | None = None,
        server_root_ca_cert: str | None = None,
        client_cert: str | None = None,
        client_private_key: str | None = None,
    ):
        self.address = address
        self.namespace = namespace
        self.server_root_ca_cert = server_root_ca_cert
        self.client_cert = client_cert
        self.client_private_key = client_private_key

        self._client = None

    @classmethod
    def from_config(cls, config_dir: str = "temporal-tui") -> typing.Self:
        config_path = platformdirs.user_config_dir(config_dir)

        with open(os.path.join(config_path, "config.toml"), "rb") as f:
            config = tomllib.load(f)

        return cls(**config)

    @classmethod
    def from_env(cls) -> typing.Self:
        try:
            host = os.environ["TEMPORAL_HOST"]
            port = os.environ["TEMPORAL_PORT"]
            address = f"{host}:{port}"
        except KeyError:
            try:
                address = os.environ["TEMPORAL_ADDRESS"]
            except KeyError:
                raise MissingRequiredError("TEMPORAL_ADDRESS")

        namespace = os.environ.get("TEMPORAL_NAMESPACE", None)
        server_root_ca_cert = os.environ.get("TEMPORAL_SERVER_ROOT_CA_CERT", None)
        client_cert = os.environ.get("TEMPORAL_CLIENT_CERT", None)
        client_private_key = os.environ.get("TEMPORAL_CLIENT_PRIVATE_KEY", None)

        return cls(
            address, namespace, server_root_ca_cert, client_cert, client_private_key
        )

    async def connect(self) -> temporalio.client.Client:
        """Connect to underlying temporalio.client.Client."""
        if self._client is not None:
            return self._client

        namespace = self.namespace or "default"

        if (
            self.server_root_ca_cert is not None
            and self.client_cert is not None
            and self.client_private_key is not None
        ):
            tls = temporalio.client.TLSConfig(
                server_root_ca_cert=bytes(self.server_root_ca_cert, "utf-8"),
                client_cert=bytes(self.client_cert, "utf-8"),
                client_private_key=bytes(self.client_private_key, "utf-8"),
            )
        else:
            tls = False

        client = await temporalio.client.Client.connect(
            self.address, namespace=namespace, tls=tls
        )

        self._client = client

        return client

    async def list_workflows(self) -> list[Workflow]:
        return [workflow async for workflow in self.iter_workflows()]

    async def iter_workflows(
        self, page_size: int = 1000
    ) -> typing.AsyncIterator[Workflow]:
        """Iterate over all Temporal Workflows.

        Workflows will be requested in batches of `page_size` workflows.
        """
        client = await self.connect()

        iterator = client.list_workflows(page_size=page_size)

        async for workflow_execution in iterator:
            yield Workflow.from_workflow_execution(workflow_execution)

    async def fetch_workflow_history(self, workflow: Workflow):
        client = await self.connect()

        handle = client.get_workflow_handle(
            workflow_id=workflow.id, run_id=workflow.run_id
        )

        return await handle.fetch_history()
