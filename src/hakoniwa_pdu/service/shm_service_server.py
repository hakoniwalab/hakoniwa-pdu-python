import asyncio
from hakoniwa_pdu.service.hako_asset_service_server import HakoAssetServiceServer
from hakoniwa_pdu.service.hako_asset_service_config import HakoAssetServiceConfig
from hakoniwa_pdu.service.shm_common import ShmCommon

class ShmServiceServer:
    def __init__(self, asset_name: str, service_name: str, delta_time_usec: int = 1000, req_encoder=None, req_decoder=None, res_encoder=None, res_decoder=None):
        self.asset_name = asset_name
        self.service_name = service_name
        self.delta_time_usec = float(delta_time_usec)
        self.service_server = None
        self.req_encoder = req_encoder
        self.req_decoder = req_decoder
        self.res_encoder = res_encoder
        self.res_decoder = res_decoder

    def initialize(self, shm: ShmCommon):
        self.service_server = HakoAssetServiceServer(shm.pdu_manager, self.asset_name, self.service_name, self.req_encoder, self.req_decoder, self.res_encoder, self.res_decoder)
        service_config = HakoAssetServiceConfig(shm.service_config_path, shm.pdu_manager.pdu_convertor.offmap)
        service_config.append_pdu_def(shm.pdu_manager.pdu_config.get_pdudef())
        service_config.create_pdus()
        self.service_server.service_config = service_config

        self.shm = shm
        if not self.service_server.initialize():
            raise RuntimeError("Failed to create asset service server")
        print(f"Service server initialized for {self.service_name}")
        return True


    async def serve(self, handler):
        while True:
            event = self.service_server.poll()
            if event < 0:
                raise RuntimeError(f"Failed to poll asset service server: {event}")
            elif self.service_server.is_request_in(event):
                req = self.service_server.get_request()
                print(f"Request received: {req}")
                res = await handler(req)
                print(f"Response data: {res}")
                while not self.service_server.normal_reply(res):
                    print("Waiting to send reply...")
                    await self.shm.sleep()
            else:
                await self.shm.sleep()
