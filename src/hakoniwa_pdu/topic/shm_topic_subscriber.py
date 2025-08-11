from hakoniwa_pdu.service.shm_common import ShmCommon
from hakoniwa_pdu.service.hako_asset_service_config import HakoAssetServiceConfig

class ShmSubscriber:
    def __init__(self, shm: ShmCommon, node_name: str, topic_name: str, decoder):
        self.shm = shm
        self.node_name = node_name
        self.topic_name = topic_name
        self.decoder = decoder
    
    def _on_recv(self):
        raw_data = self.shm.pdu_manager.read_pdu_raw_data(self.node_name, self.topic_name)
        if raw_data is None or len(raw_data) == 0:
            print("No data received")
            return
        msg = self.decoder(raw_data)
        if self.callback:
            self.callback(msg)

    def initialize(self, service_config_path: str, callback=None):
        self.callback = callback
        service_config = HakoAssetServiceConfig(service_config_path, self.shm.pdu_manager.pdu_convertor.offmap)
        service_config.append_pdu_def(self.shm.pdu_manager.pdu_config.get_pdudef())
        service_config.create_pdus()
        self.service_config = service_config
        return self.shm.subscribe_topic(self.node_name, self.topic_name)

    def read(self):
        return self.shm.read_topic(self.node_name, self.topic_name)

    async def spin(self):
        while True:
            msg = self.read()
            if msg and self.callback:
                decoded_msg = self.decoder(msg)
                self.callback(decoded_msg)
            await self.shm.sleep()
