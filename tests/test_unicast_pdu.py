import asyncio
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from hakoniwa_pdu.impl.data_packet import DataPacket, REQUEST_PDU_READ
from hakoniwa_pdu.rpc.remote.remote_pdu_service_server_manager import (
    RemotePduServiceServerManager,
)


class MockCommService:
    version = "v2"

    def __init__(self):
        self.calls = []
        self.fail_clients = set()
        self.on_disconnect = None

    def set_channel_config(self, _cfg):
        pass

    def register_event_handler(self, handler):
        self.handler = handler

    async def send_data_to(self, client_id, robot_name, channel_id, data):
        self.calls.append((client_id, robot_name, channel_id, bytes(data)))
        return client_id not in self.fail_clients


pdu_config_path = "tests/pdu_config.json"
offset_path = "tests/config/offset"
uri = "ws://localhost"

pytestmark = pytest.mark.asyncio


async def _make_manager():
    comm = MockCommService()
    mgr = RemotePduServiceServerManager("srv", pdu_config_path, offset_path, comm, uri)
    return mgr, comm


async def test_unicast_send_only_target_client():
    mgr, comm = await _make_manager()
    received = []

    def on_request(cid, pkt):
        received.append(cid)
        asyncio.create_task(
            mgr.send_pdu_to(cid, pkt.robot_name, pkt.channel_id, b"abc")
        )

    mgr.register_handler_request_pdu_read(on_request)

    pkt = DataPacket("test_server", 1, bytearray())
    pkt.meta_pdu.meta_request_type = REQUEST_PDU_READ
    await mgr.handler(pkt, "clientA")
    await asyncio.sleep(0)

    assert received == ["clientA"]
    assert comm.calls == [("clientA", "test_server", 1, b"abc")]


async def test_reply_latest_to_uses_buffer():
    mgr, comm = await _make_manager()
    mgr.comm_buffer.put_packet_direct("test_server", 1, bytearray(b"xyz"))

    ok = await mgr.reply_latest_to("clientA", "test_server", 1)
    assert ok is True
    assert comm.calls == [("clientA", "test_server", 1, b"xyz")]


async def test_request_handler_receives_client_id():
    mgr, comm = await _make_manager()
    captured = {}

    def on_request(cid, pkt):
        captured["cid"] = cid
        captured["robot"] = pkt.robot_name
        captured["ch"] = pkt.channel_id

    mgr.register_handler_request_pdu_read(on_request)

    pkt = DataPacket("test_server", 1, bytearray())
    pkt.meta_pdu.meta_request_type = REQUEST_PDU_READ
    await mgr.handler(pkt, "clientA")

    assert captured == {"cid": "clientA", "robot": "test_server", "ch": 1}


async def test_send_pdu_to_after_disconnect_returns_false():
    mgr, comm = await _make_manager()
    comm.fail_clients.add("clientA")
    mgr.on_disconnect("clientA")

    ok = await mgr.send_pdu_to("clientA", "test_server", 1, b"abc")
    assert ok is False
    assert comm.calls == [("clientA", "test_server", 1, b"abc")]
