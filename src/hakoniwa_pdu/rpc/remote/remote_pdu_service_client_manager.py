from typing import Optional
import asyncio
import time

from .remote_pdu_service_base_manager import RemotePduServiceBaseManager
from ..ipdu_service_manager import (
    IPduServiceClientManagerBlocking,
    ClientId,
    PduData,
    Event,
)
from ..service_config import ServiceConfig
from hakoniwa_pdu.impl.hako_binary import offset_map
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_RegisterClientResponse import (
    RegisterClientResponse,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_RegisterClientRequestPacket import (
    RegisterClientRequestPacket,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_RegisterClientResponsePacket import (
    RegisterClientResponsePacket,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_RegisterClientRequestPacket import (
    py_to_pdu_RegisterClientRequestPacket,
)
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_RegisterClientResponsePacket import (
    pdu_to_py_RegisterClientResponsePacket,
)
from hakoniwa_pdu.impl.data_packet import (
    REGISTER_RPC_CLIENT,
    PDU_DATA_RPC_REQUEST,
    PDU_DATA_RPC_REPLY,
)


class RemotePduServiceClientManager(
    RemotePduServiceBaseManager, IPduServiceClientManagerBlocking
):
    """Client-side implementation for remote RPC."""

    def __init__(
        self,
        asset_name: str,
        pdu_config_path: str,
        offset_path: str,
        comm_service,
        uri: str,
    ) -> None:
        super().__init__(asset_name, pdu_config_path, offset_path, comm_service, uri)
        self.request_id = 0
        self.service_name: Optional[str] = None
        self.client_name: Optional[str] = None
        self.timeout_msec: Optional[int] = None
        self.call_start_time_msec: Optional[int] = None
        self.request_buffer: Optional[bytes] = None
        self.poll_interval_msec: Optional[int] = None

    async def register_client(
        self, service_name: str, client_name: str, timeout: float = 1.0
    ) -> Optional[ClientId]:
        if self.service_config_path is None:
            raise RuntimeError(
                "service_config_path is not set. Call initialize_services() first."
            )
        self.service_name = service_name
        self.client_name = client_name
        offmap = offset_map.create_offmap(self.offset_path)
        self.service_config = ServiceConfig(
            self.service_config_path, offmap, hakopy=None
        )
        pdudef = self.service_config.append_pdu_def(self.pdu_config.get_pdudef())
        self.pdu_config.update_pdudef(pdudef)
        print("Service PDU definitions prepared.")

        packet = RegisterClientRequestPacket()
        packet.header.request_id = 0
        packet.header.service_name = service_name
        packet.header.client_name = client_name
        packet.header.opcode = 0
        packet.header.status_poll_interval_msec = 0
        packet.body.dummy = 0

        pdu_data = py_to_pdu_RegisterClientRequestPacket(packet)
        raw_data = self._build_binary(REGISTER_RPC_CLIENT, service_name, -1, pdu_data)
        if not await self.comm_service.send_binary(raw_data):
            return None
        loop = asyncio.get_event_loop()
        end_time = loop.time() + timeout
        response_buffer = None
        while loop.time() < end_time:
            if self.comm_buffer.contains_buffer(service_name, client_name):
                response_buffer = self.comm_buffer.get_buffer(service_name, client_name)
                break
            await asyncio.sleep(0.05)
        if response_buffer is None:
            return None

        response = pdu_to_py_RegisterClientResponsePacket(response_buffer)
        if response.header.result_code != self.API_RESULT_CODE_OK:
            print(
                f"Failed to register client '{client_name}' to service '{service_name}': {response.header.result_code}"
            )
            return None
        return response.body

    async def call_request(
        self, client_id: ClientId, pdu_data: PduData, timeout_msec: int
    ) -> bool:
        self.timeout_msec = timeout_msec
        self.call_start_time_msec = int(time.time() * 1000)
        client_info: RegisterClientResponse = client_id
        raw_data = self._build_binary(
            PDU_DATA_RPC_REQUEST,
            self.service_name,
            client_info.request_channel_id,
            pdu_data,
        )
        if not await self.comm_service.send_binary(raw_data):
            return False
        self.request_buffer = raw_data
        return True

    def get_request_buffer(
        self, client_id: int, opcode: int, poll_interval_msec: int, request_id: int
    ) -> bytes:
        self.poll_interval_msec = poll_interval_msec
        py_pdu_data = self.cls_req_packet()
        py_pdu_data.header.request_id = request_id
        py_pdu_data.header.service_name = self.service_name
        py_pdu_data.header.client_name = self.client_name
        py_pdu_data.header.opcode = opcode
        py_pdu_data.header.status_poll_interval_msec = poll_interval_msec
        return self.req_encoder(py_pdu_data)

    def poll_response(self, client_id: ClientId) -> Event:
        if self.comm_buffer.contains_buffer(self.service_name, self.client_name):
            raw_data = self.comm_buffer.peek_buffer(self.service_name, self.client_name)
            response = self.res_decoder(raw_data)
            if response.header.result_code == self.API_RESULT_CODE_CANCELED:
                self.request_id += 1
                return self.CLIENT_API_EVENT_REQUEST_CANCEL_DONE
            self.request_id += 1
            return self.CLIENT_API_EVENT_RESPONSE_IN
        current_time_msec = int(time.time() * 1000)
        if (current_time_msec - self.call_start_time_msec) > self.timeout_msec:
            return self.CLIENT_API_EVENT_REQUEST_TIMEOUT
        return self.CLIENT_API_EVENT_NONE

    def get_response(self, service_name: str, client_id: ClientId) -> PduData:
        if self.comm_buffer.contains_buffer(self.service_name, self.client_name):
            raw_data = self.comm_buffer.get_buffer(self.service_name, self.client_name)
            return raw_data
        raise RuntimeError("No response data available. Call poll_response() first.")

    async def cancel_request(self, client_id: ClientId) -> bool:
        client_info: RegisterClientResponse = client_id
        py_pdu_data = self.req_decoder(self.request_buffer)
        py_pdu_data.header.opcode = self.CLIENT_API_OPCODE_CANCEL
        py_pdu_data.header.status_poll_interval_msec = -1
        pdu_data = self.req_encoder(py_pdu_data)
        raw_data = self._build_binary(
            PDU_DATA_RPC_REQUEST,
            self.service_name,
            client_info.request_channel_id,
            pdu_data,
        )
        if not await self.comm_service.send_binary(raw_data):
            return False
        self.request_buffer = raw_data
        return True

    def is_client_event_response_in(self, event: Event) -> bool:
        return event == self.CLIENT_API_EVENT_RESPONSE_IN

    def is_client_event_timeout(self, event: Event) -> bool:
        return event == self.CLIENT_API_EVENT_REQUEST_TIMEOUT

    def is_client_event_cancel_done(self, event: Event) -> bool:
        return event == self.CLIENT_API_EVENT_REQUEST_CANCEL_DONE

    def is_client_event_none(self, event: Event) -> bool:
        return event == self.CLIENT_API_EVENT_NONE

    @property
    def requires_external_request_id(self) -> bool:
        return True


__all__ = ["RemotePduServiceClientManager"]
