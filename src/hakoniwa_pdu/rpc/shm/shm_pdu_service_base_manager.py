from hakoniwa_pdu._optional_hakopy import hakopy
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from ..ipdu_service_manager import IPduServiceManager, ClientId
from ..service_config import ServiceConfig
from hakoniwa_pdu.impl.shm_communication_service import ShmCommunicationService
from hakoniwa_pdu.impl.hako_binary import offset_map


@dataclass(frozen=True)
class ShmClientHandleContext:
    handle: Any
    service_id: int
    native_client_id: int
    request_channel_id: int
    response_channel_id: int


class ShmPduServiceBaseManager(IPduServiceManager):
    """共有メモリ向けPDUサービス共通機能"""

    def __init__(self, asset_name: str, pdu_config_path: str, offset_path: str):
        super().__init__()
        self.asset_name = asset_name
        self.offset_path = offset_path

        # PduManagerの基本的な初期化
        self.initialize(config_path=pdu_config_path, comm_service=ShmCommunicationService())

        # 共有の状態管理
        self.service_config: Optional[ServiceConfig] = None
        self.service_config_path: Optional[str] = None
        self.delta_time_usec: Optional[int] = None
        self.delta_time_sec: Optional[float] = None
        self.offmap: Optional[offset_map.OffsetMap] = None
        self._shared_memory_loaded: bool = False
        self._service_pdudef_prepared: bool = False
        self.service_id_map: Dict[int, str] = {}
        self.client_handles: Dict[ClientId, ShmClientHandleContext] = {}
        self._next_client_handle_id: int = 0
        self.current_server_client_info: Dict[str, Any] = {}

    def allocate_client_handle_id(self) -> ClientId:
        client_handle_id = self._next_client_handle_id
        self._next_client_handle_id += 1
        return client_handle_id

    def get_client_context(self, client_id: ClientId) -> ShmClientHandleContext:
        context = self.client_handles.get(client_id)
        if context is None:
            raise ValueError(f"Invalid client_id: {client_id}")
        return context

    def initialize_services(self, service_config_path: str, delta_time_usec: int) -> int:
        self.service_config_path = service_config_path
        self.delta_time_usec = delta_time_usec
        self.delta_time_sec = delta_time_usec / 1_000_000.0
        self.offmap = offset_map.create_offmap(self.offset_path)
        self.service_config = ServiceConfig(
            self.service_config_path,
            self.offmap,
            hakopy=hakopy,
        )
        self.load_shared_memory_for_safe(self.pdu_config.get_pdudef())
        self._shared_memory_loaded = True
        ret = hakopy.service_initialize(self.service_config_path)
        if ret == 0:
            self.prepare_service_pdudef_once()
        return ret

    def sleep(self, time_sec: float) -> bool:
        ret = hakopy.usleep(int(time_sec * 1_000_000))
        if ret is False:
            sys.exit(1)
        time.sleep(time_sec)
        return True


    def load_shared_memory_for_safe(self, pdudef: Dict[str, Any]) -> bool:
        _ = pdudef  # Kept for backward compatibility of callers.
        readers = self.pdu_config.get_shm_pdu_readers()
        if not readers:
            print("No shm_pdu_readers found in pdudef.")
            return False

        reader = readers[0]
        robot_name = reader.robot_name
        channel_id = reader.channel_id
        pdu_size = reader.pdu_size

        print(f"robot_name={robot_name}")
        print(f"channel_id={channel_id}")
        print(f"pdu_size={pdu_size}")
        # dummy read to initialize shared memory
        _ = hakopy.pdu_read(robot_name, channel_id, pdu_size)
        return True

    def prepare_service_pdudef_once(self) -> None:
        if self._service_pdudef_prepared:
            return
        if self.service_config is None:
            raise RuntimeError("service manager is not initialized")
        pdudef = self.service_config.append_pdu_def(self.pdu_config.get_pdudef())
        self.pdu_config.update_pdudef(pdudef)
        self._service_pdudef_prepared = True
    
__all__ = ["ShmPduServiceBaseManager"]
