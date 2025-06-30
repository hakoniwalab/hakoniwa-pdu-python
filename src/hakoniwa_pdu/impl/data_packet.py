import struct

class DataPacket:
    def __init__(self, robot_name: str = "", channel_id: int = 0, body_data: bytearray = None):
        self.robot_name = robot_name
        self.channel_id = channel_id
        self.body_data = body_data if body_data is not None else bytearray()

    def set_robot_name(self, name: str):
        self.robot_name = name

    def set_channel_id(self, channel_id: int):
        self.channel_id = channel_id

    def set_pdu_data(self, data: bytearray):
        self.body_data = data

    def get_robot_name(self) -> str:
        return self.robot_name

    def get_channel_id(self) -> int:
        return self.channel_id

    def get_pdu_data(self) -> bytearray:
        return self.body_data

    def encode(self) -> bytearray:
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
    def decode(data: bytearray):
        if len(data) < 12:
            print("[ERROR] Data too short")
            return None

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
