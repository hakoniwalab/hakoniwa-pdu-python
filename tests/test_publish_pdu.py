import os
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from hakoniwa_pdu.impl.data_packet import DataPacket, DECLARE_PDU_FOR_READ
from hakoniwa_pdu.rpc.remote.remote_pdu_service_server_manager import RemotePduServiceServerManager


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


def _declare(manager, cid, robot="R", ch=1):
    pkt = DataPacket(robot, ch, bytearray())
    pkt.meta_pdu.meta_request_type = DECLARE_PDU_FOR_READ
    return manager.handler(pkt, cid)


async def _make_manager():
    comm = MockCommService()
    mgr = RemotePduServiceServerManager("srv", pdu_config_path, offset_path, comm, uri)
    mgr.register_handler_pdu_for_read(lambda cid, pkt: None)
    return mgr, comm


async def test_publish_multiple_clients():
    mgr, comm = await _make_manager()
    await _declare(mgr, "c1")
    await _declare(mgr, "c2")
    sent = await mgr.publish_pdu("R", 1, b"abc")
    assert sent == 2
    assert len(comm.calls) == 2
    assert set(comm.calls) == {
        ("c1", "R", 1, b"abc"),
        ("c2", "R", 1, b"abc"),
    }


async def test_duplicate_declare_single_send():
    mgr, comm = await _make_manager()
    await _declare(mgr, "c1")
    await _declare(mgr, "c1")
    sent = await mgr.publish_pdu("R", 1, b"abc")
    assert sent == 1
    assert comm.calls == [("c1", "R", 1, b"abc")]


async def test_publish_no_subscribers():
    mgr, comm = await _make_manager()
    sent = await mgr.publish_pdu("R", 999, b"x")
    assert sent == 0
    assert comm.calls == []


async def test_disconnect_cleanup():
    mgr, comm = await _make_manager()
    await _declare(mgr, "c1")
    await _declare(mgr, "c2")
    mgr.on_disconnect("c1")
    sent = await mgr.publish_pdu("R", 1, b"abc")
    assert sent == 1
    assert comm.calls == [("c2", "R", 1, b"abc")]
    assert mgr._read_index.get(("R", 1)) == {"c2"}


async def test_send_failure():
    mgr, comm = await _make_manager()
    await _declare(mgr, "c1")
    await _declare(mgr, "c2")
    comm.fail_clients.add("c1")
    sent = await mgr.publish_pdu("R", 1, b"abc")
    assert sent == 1
    assert len(comm.calls) == 2
    assert set(comm.calls) == {
        ("c1", "R", 1, b"abc"),
        ("c2", "R", 1, b"abc"),
    }
