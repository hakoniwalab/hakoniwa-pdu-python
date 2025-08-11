from hakoniwa_pdu.service.shm_common import ShmCommon
from hakoniwa_pdu.service.hako_asset_service_config import HakoAssetServiceConfig

class ShmPublisher:
    def __init__(self, shm: ShmCommon, node_name: str, topic_name: str, encoder):
        self.shm = shm
        self.node_name = node_name
        self.topic_name = topic_name
        self.encoder = encoder

    def initialize(self, service_config_path: str):
        service_config = HakoAssetServiceConfig(service_config_path, self.shm.pdu_manager.pdu_convertor.offmap)
        service_config.append_pdu_def(self.shm.pdu_manager.pdu_config.get_pdudef())
        service_config.create_pdus()
        self.service_config = service_config
        return True

    def publish(self, msg):
        raw_data = self.encoder(msg)
        return self.shm.pdu_manager.flush_pdu_raw_data_nowait(self.node_name, self.topic_name, raw_data)
