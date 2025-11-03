import hakopy
import sys
import time
from typing import Any, Dict, Optional

from ..ipdu_service_manager import IPduServiceManager, ClientId
from ..service_config import ServiceConfig
from hakoniwa_pdu.impl.shm_communication_service import ShmCommunicationService


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
        self.service_id_map: Dict[int, str] = {}
        self.client_handles: Dict[ClientId, Any] = {}
        self.current_server_client_info: Dict[str, Any] = {}

    def initialize_services(self, service_config_path: str, delta_time_usec: int) -> int:
        self.service_config_path = service_config_path
        self.delta_time_usec = delta_time_usec
        self.delta_time_sec = delta_time_usec / 1_000_000.0
        return hakopy.service_initialize(self.service_config_path)

    def sleep(self, time_sec: float) -> bool:
        ret = hakopy.usleep(int(time_sec * 1_000_000))
        if ret is False:
            sys.exit(1)
        time.sleep(time_sec)
        return True


    def load_shared_memory_for_safe(self, pdudef: Dict[str, Any]) -> bool:
        robots = pdudef.get("robots", [])
        if robots:
            robot = robots[0]
            robot_name = robot.get("name")
            readers = robot.get("shm_pdu_readers", [])
            if readers:
                reader = readers[0]
                channel_id = reader.get("channel_id")
                pdu_size = reader.get("pdu_size")

                print(f"robot_name={robot_name}")
                print(f"channel_id={channel_id}")
                print(f"pdu_size={pdu_size}")
                #dummy read to initialize shared memory
                _ = hakopy.pdu_read(robot_name, channel_id, pdu_size)
            else:
                print("No shm_pdu_readers found in pdudef.")
                return False
        else:
            print("No robots found in pdudef.")
            return False

        return True
    
__all__ = ["ShmPduServiceBaseManager"]

