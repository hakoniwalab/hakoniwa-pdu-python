import time
import asyncio
from typing import Optional

from ..ipdu_service_manager import IPduServiceManager
from ..service_config import ServiceConfig
from hakoniwa_pdu.impl.icommunication_service import ICommunicationService


class RemotePduServiceBaseManager(IPduServiceManager):
    """Common functionality for remote RPC managers."""

    def __init__(
        self,
        asset_name: str,
        pdu_config_path: str,
        offset_path: str,
        comm_service: ICommunicationService,
        uri: str,
    ) -> None:
        super().__init__(wire_version=comm_service.version)
        self.asset_name = asset_name
        self.offset_path = offset_path
        self.uri = uri
        self.initialize(config_path=pdu_config_path, comm_service=comm_service)

        self.service_config: Optional[ServiceConfig] = None
        self.service_config_path: Optional[str] = None
        self.delta_time_usec: Optional[int] = None
        self.delta_time_sec: Optional[float] = None

    def initialize_services(self, service_config_path: str, delta_time_usec: int) -> int:
        self.service_config_path = service_config_path
        self.delta_time_usec = delta_time_usec
        self.delta_time_sec = delta_time_usec / 1_000_000.0
        return 0

    async def sleep(self, time_sec: float) -> bool:
        await asyncio.sleep(time_sec)
        return True


__all__ = ["RemotePduServiceBaseManager"]
