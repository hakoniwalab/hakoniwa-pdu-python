import json
import os
import hakopy
import asyncio
from hakoniwa_pdu.pdu_manager import PduManager
from hakoniwa_pdu.impl.shm_communication_service import ShmCommunicationService

class ShmCommon:
    def __init__(self, service_config_path: str, pdu_offset_path: str = '/usr/local/lib/hakoniwa/hako_binary/offset', delta_time_usec: int = 1000):
        self.pdu_offset_path = pdu_offset_path
        if self.pdu_offset_path is None:
            self.pdu_offset_path = os.getenv('HAKO_BINARY_PATH', '/usr/local/lib/hakoniwa/hako_binary/offset')
            if self.pdu_offset_path is None:
                raise RuntimeError("HAKO_BINARY_PATH is not set")
        
        self.service_config_path = service_config_path
        self.service_json = self.load_json(service_config_path)
        if self.service_json is None:
            raise RuntimeError(f"Failed to load service config file: {service_config_path}")
        if self.service_json.get('pdu_config_path') is None:
            raise RuntimeError(f"pdu_config_path is not set in {service_config_path}")
        self.pdu_config_path = self.service_json['pdu_config_path']
        if not os.path.exists(self.pdu_config_path):
            raise RuntimeError(f"pdu_config_path does not exist: {self.pdu_config_path}")

        self.delta_time_usec = delta_time_usec
        self.pdu_manager = PduManager()
        self.pdu_manager.initialize(config_path=self.pdu_config_path, comm_service=ShmCommunicationService())
        self.pdu_manager.start_service_nowait()


    def initialize(self):
        ret = hakopy.init_for_external()
        if ret == False:
            raise RuntimeError("Failed to initialize hakopy")
        ret = hakopy.service_initialize(self.service_config_path)
        if ret == False:
            raise RuntimeError("Failed to initialize service")
        return ret

    async def sleep(self):
        await asyncio.sleep(self.delta_time_usec / 1000000)

    def load_json(self, path):
        try:
            with open(path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"ERROR: File not found '{path}'")
        except json.JSONDecodeError:
            print(f"ERROR: Invalid Json fromat '{path}'")
        except PermissionError:
            print(f"ERROR: Permission denied '{path}'")
        except Exception as e:
            print(f"ERROR: {e}")
        return None

    def start_conductor(self):
        ret = hakopy.conductor_start(self.delta_time_usec, self.delta_time_usec)
        if ret < 0:
            raise RuntimeError(f"Failed to start conductor: {ret}")
        return ret
    def stop_conductor(self):
        ret = hakopy.conductor_stop()
        if ret < 0:
            raise RuntimeError(f"Failed to stop conductor: {ret}")
        return ret
    def start_service(self):
        hakopy.trigger_event(hakopy.HAKO_TRIGGER_EVENT_ID_START)
        return True
    
    def stop_service(self):
        hakopy.trigger_event(hakopy.HAKO_TRIGGER_EVENT_ID_STOP)
        return True

    def reset_service(self):
        hakopy.trigger_event(hakopy.HAKO_TRIGGER_EVENT_ID_RESET)
        return True

    def read_topic(self, node_name: str, topic_name: str):
        if self.pdu_manager is None:
            raise RuntimeError("PDU manager is not initialized")
        channel_id = self.pdu_manager.get_pdu_channel_id(node_name, topic_name)
        if channel_id is None:
            raise RuntimeError(f"PDU not found: {node_name}, {topic_name}")

        ret = hakopy.check_data_recv_event(node_name, channel_id)
        if ret == False:
            return None
        self.pdu_manager.run_nowait()
        raw_data = self.pdu_manager.read_pdu_raw_data(node_name, topic_name)
        if raw_data is None or len(raw_data) == 0:
            return None
        return raw_data

    def subscribe_topic(self, node_name: str, topic_name: str):
        if self.pdu_manager is None:
            raise RuntimeError("PDU manager is not initialized")
        channel_id = self.pdu_manager.get_pdu_channel_id(node_name, topic_name)
        if channel_id is None:
            raise RuntimeError(f"PDU not found: {node_name}, {topic_name}")
        ret = hakopy.register_data_recv_event(node_name, channel_id, None)
        if ret != 0:
            raise RuntimeError(f"Failed to register data receive event: {node_name}, {topic_name}")
        return True