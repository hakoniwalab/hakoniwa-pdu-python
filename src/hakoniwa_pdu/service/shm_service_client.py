import asyncio
from hakoniwa_pdu.service.hako_asset_service_client import HakoAssetServiceClient
from hakoniwa_pdu.service.hako_asset_service_config import HakoAssetServiceConfig
from hakoniwa_pdu.service.shm_common import ShmCommon

class ShmServiceClient:
    def __init__(
            self, 
            asset_name: str, 
            service_name: str, 
            client_name:str, 
            delta_time_usec: int = 1000,
            req_encoder=None,
            req_decoder=None,
            res_encoder=None,
            res_decoder=None):
        self.asset_name = asset_name
        self.service_name = service_name
        self.client_name = client_name
        self.delta_time_usec = float(delta_time_usec)
        self.service_client = None
        self.req_encoder = req_encoder
        self.req_decoder = req_decoder
        self.res_encoder = res_encoder
        self.res_decoder = res_decoder

    # user must initialize the shm
    def initialize(self, shm: ShmCommon):
        # Initialize the asset service
        self.service_client = HakoAssetServiceClient(shm.pdu_manager, self.asset_name, self.service_name, self.client_name,
                                                     req_encoder=self.req_encoder,
                                                     req_decoder=self.req_decoder,
                                                     res_encoder=self.res_encoder,
                                                     res_decoder=self.res_decoder)
        service_config = HakoAssetServiceConfig(shm.service_config_path, shm.pdu_manager.pdu_convertor.offmap)
        service_config.append_pdu_def(shm.pdu_manager.pdu_config.get_pdudef())
        service_config.create_pdus()
        self.service_client.service_config = service_config

        self.shm = shm
        if self.service_client.initialize() == False:
            raise RuntimeError("Failed to create asset service")
        print(f"Service client handle: {self.service_client.handle}")
        return True


    async def call_async(self, req, timeout_msec = -1) -> dict:
        while not self.service_client.request(req, timeout_msec):
            print("INFO: Can not send request")
            await self.shm.sleep()
        res = await self._wait_for_response()
        if res is None:
            print("WARNING: APL cancel request is happened.")
            return await self._do_cancel()
        return res

    async def _wait_for_response(self):
        while True:
            event = self.service_client.poll()
            if event < 0:
                raise RuntimeError(f"Failed to poll asset service client: {event}")
            elif self.service_client.is_response_in(event):
                print("INFO: APL wait for response")
                res = self.service_client.get_response()
                return res
            elif self.service_client.is_request_timeout(event):
                print("INFO: Request timeout")
                return None
            await self.shm.sleep()
            print("INFO: APL wait for response")

    async def _do_cancel(self):
        while self.service_client.cancel_request() == False:
            print("INFO: APL cancel_request() is not done")
            await self.shm.sleep()

        print("INFO: APL cancel_request() is done")
        while True:
            event = self.service_client.poll()
            if event < 0:
                raise RuntimeError(f"Failed to poll asset service client: {event}")
            elif self.service_client.is_request_cancel_done(event):
                print("INFO: Request cancel done")
                break
            elif self.service_client.is_response_in(event):
                res = self.service_client.get_response()
                return res
            else:
                print("INFO: Request cancel is not done")
            await self.shm.sleep()
        return None
