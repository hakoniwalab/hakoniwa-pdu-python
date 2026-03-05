import struct
from typing import Optional
from hakoniwa_pdu.pdu_msgs.hako_msgs.pdu_pytype_MetaPdu import MetaPdu

# 固定値（必要に応じて既存定義と統合）
HAKO_META_MAGIC = 0x48414B4F  # "HAKO"
HAKO_META_VER   = 0x0002
ROBOT_NAME_FIXED_SIZE = 128
META_FIXED_SIZE = 176
TOTAL_PDU_META_SIZE = ROBOT_NAME_FIXED_SIZE + META_FIXED_SIZE

# Magic numbers used for special control packets
DECLARE_PDU_FOR_READ = 0x52455044   # "REPD"
DECLARE_PDU_FOR_WRITE = 0x57505044  # "WPPD"
# Request the server to immediately send the latest PDU for the given channel
REQUEST_PDU_READ = 0x57505045

PDU_DATA     = 0x42555043   # "CPUB"
REGISTER_RPC_CLIENT    = 0x43505244   # "DRPC"
PDU_DATA_RPC_REQUEST     = 0x43505243   # "CRPC"
PDU_DATA_RPC_REPLY       = 0x43505253   # "SRPC"

class DataPacket:
    def __init__(self, robot_name: str = "", channel_id: int = 0, body_data: bytearray | None = None,
                 *, meta: MetaPdu | None = None):
        if meta is not None:
            # Metaから復元
            self.meta_pdu: MetaPdu = meta
            self.robot_name = meta.robot_name
            self.channel_id = meta.channel_id
            self.body_data = body_data if body_data is not None else bytearray()
        else:
            # レガシー流儀
            self.meta_pdu = MetaPdu()
            self.robot_name = robot_name
            self.channel_id = channel_id
            self.meta_pdu.robot_name = robot_name
            self.meta_pdu.channel_id = channel_id
            self.body_data = body_data if body_data is not None else bytearray()

        self.set_hako_time_usec(0)
        self.set_asset_time_usec(0)
        self.set_real_time_usec(0)

    def set_hako_time_usec(self, time_usec: int):
        self.meta_pdu.hako_time_us = time_usec

    def set_asset_time_usec(self, time_usec: int):
        self.meta_pdu.asset_time_us = time_usec

    def set_real_time_usec(self, time_usec: int):
        self.meta_pdu.real_time_us = time_usec

    def set_robot_name(self, name: str):
        self.robot_name = name
        self.meta_pdu.robot_name = name

    def set_channel_id(self, channel_id: int):
        self.channel_id = channel_id
        self.meta_pdu.channel_id = channel_id

    def set_pdu_data(self, data: bytearray):
        self.body_data = data

    def get_robot_name(self) -> str:
        return self.robot_name

    def get_channel_id(self) -> int:
        return self.channel_id

    def get_pdu_data(self) -> bytearray:
        return self.body_data

    def encode(self, version: str = "v1", meta_request_type: int = None) -> bytearray:
        # バージョンに応じたエンコード処理を実装
        if version == "v1":
            return self._encode_v1()
        else:
            return self._encode_v2(meta_request_type)

    def _encode_v2(self, meta_request_type: int) -> bytearray:
        # setter経由の値ズレを防ぐため、送信直前に同期
        self.meta_pdu.robot_name = self.robot_name
        self.meta_pdu.channel_id = self.channel_id

        body_len = len(self.body_data)  # = [HakoMeta24 + Base+Heap] の総長
        self.meta_pdu.magicno = HAKO_META_MAGIC
        self.meta_pdu.version = HAKO_META_VER
        self.meta_pdu.flags = 0
        self.meta_pdu.meta_request_type = meta_request_type if meta_request_type is not None else 0
        self.meta_pdu.body_len = body_len
        # 「自分（4B）を除く残り」
        self.meta_pdu.total_len = (META_FIXED_SIZE - 4) + body_len
        header = bytearray(TOTAL_PDU_META_SIZE)
        self._write_fixed_string(header, 0, ROBOT_NAME_FIXED_SIZE, self.meta_pdu.robot_name)
        base_off = ROBOT_NAME_FIXED_SIZE
        struct.pack_into("<I", header, base_off + 0, self.meta_pdu.magicno)
        struct.pack_into("<H", header, base_off + 4, self.meta_pdu.version)
        struct.pack_into("<H", header, base_off + 6, self.meta_pdu.flags)
        struct.pack_into("<I", header, base_off + 8, 0)  # reserved
        struct.pack_into("<I", header, base_off + 12, self.meta_pdu.meta_request_type)
        struct.pack_into("<I", header, base_off + 16, self.meta_pdu.total_len)
        struct.pack_into("<I", header, base_off + 20, self.meta_pdu.body_len)
        struct.pack_into("<Q", header, base_off + 24, self.meta_pdu.hako_time_us)
        struct.pack_into("<Q", header, base_off + 32, self.meta_pdu.asset_time_us)
        struct.pack_into("<Q", header, base_off + 40, self.meta_pdu.real_time_us)
        struct.pack_into("<i", header, base_off + 48, self.meta_pdu.channel_id)
        header.extend(self.body_data)
        return header


    def _encode_v1(self) -> bytearray:
        robot_name_bytes = self.robot_name.encode("utf-8")
        name_len = len(robot_name_bytes)
        header_len = 4 + name_len + 4  # name_len(4) + name + channel_id(4)
        total_len = 4 + header_len + len(self.body_data)

        result = bytearray()
        result.extend(struct.pack("<I", header_len))         # Header Length
        result.extend(struct.pack("<I", name_len))           # Name Length
        result.extend(robot_name_bytes)                      # Name Bytes
        result.extend(struct.pack("<I", self.channel_id))    # Channel ID
        result.extend(self.body_data)                        # Body

        return result


    @staticmethod
    def _slice_body_safely(buf: bytes) -> Optional[memoryview]:
        start = TOTAL_PDU_META_SIZE
        end = len(buf)
        return memoryview(buf)[start:end]

    @staticmethod
    def decode(data: bytearray, version: str = "v1") -> Optional['DataPacket']:
        if len(data) < 12:
            print("[ERROR] Data too short")
            return None
        # バージョンに応じたデコード処理を実装
        if version == "v1":
            return DataPacket._decode_v1(data)
        else:
            return DataPacket._decode_v2(data)

    @classmethod
    def _decode_v2(cls, frame: bytes) -> Optional['DataPacket']:
        if frame is None or len(frame) < TOTAL_PDU_META_SIZE:
            return None

        base_off = ROBOT_NAME_FIXED_SIZE
        meta = MetaPdu()
        meta.robot_name = cls._read_fixed_string(frame, 0, ROBOT_NAME_FIXED_SIZE)
        meta.magicno = struct.unpack_from("<I", frame, base_off + 0)[0]
        meta.version = struct.unpack_from("<H", frame, base_off + 4)[0]
        meta.flags = struct.unpack_from("<H", frame, base_off + 6)[0]
        meta.meta_request_type = struct.unpack_from("<I", frame, base_off + 12)[0]
        meta.total_len = struct.unpack_from("<I", frame, base_off + 16)[0]
        meta.body_len = struct.unpack_from("<I", frame, base_off + 20)[0]
        meta.hako_time_us = struct.unpack_from("<Q", frame, base_off + 24)[0]
        meta.asset_time_us = struct.unpack_from("<Q", frame, base_off + 32)[0]
        meta.real_time_us = struct.unpack_from("<Q", frame, base_off + 40)[0]
        meta.channel_id = struct.unpack_from("<i", frame, base_off + 48)[0]
        if meta.version != HAKO_META_VER or meta.magicno != HAKO_META_MAGIC:
            return None
        end = TOTAL_PDU_META_SIZE + meta.body_len
        if len(frame) < end:
            return None

        pkt = cls(meta=meta, body_data=bytearray(frame[TOTAL_PDU_META_SIZE:end]))
        return pkt

    @staticmethod
    def _decode_v1(data: bytearray) -> Optional['DataPacket']:
        index = 0

        header_len = struct.unpack_from("<I", data, index)[0]
        index += 4

        name_len = struct.unpack_from("<I", data, index)[0]
        index += 4

        if index + name_len + 4 > len(data):
            print("[ERROR] Invalid robot name length")
            return None

        robot_name_bytes = data[index:index+name_len]
        robot_name = robot_name_bytes.decode("utf-8")
        index += name_len

        channel_id = struct.unpack_from("<I", data, index)[0]
        index += 4

        body = data[index:] if index < len(data) else bytearray()

        return DataPacket(robot_name, channel_id, bytearray(body))

    @staticmethod
    def _write_fixed_string(buf: bytearray, off: int, size: int, value: str) -> None:
        buf[off:off + size] = b"\x00" * size
        raw = (value or "").encode("utf-8")
        copy_len = min(len(raw), size - 1)
        buf[off:off + copy_len] = raw[:copy_len]

    @staticmethod
    def _read_fixed_string(buf: bytes, off: int, size: int) -> str:
        raw = bytes(buf[off:off + size])
        nul = raw.find(b"\x00")
        if nul >= 0:
            raw = raw[:nul]
        return raw.decode("utf-8", errors="ignore")
