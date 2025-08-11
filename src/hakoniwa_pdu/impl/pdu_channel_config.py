import json
from typing import Optional

class PduIoInfo:
    def __init__(self, robot_name: str, channel_id: int, org_name: str, pdu_size: int, pdu_type: str):
        self.robot_name = robot_name
        self.channel_id = channel_id
        self.org_name = org_name
        self.pdu_size = pdu_size
        self.pdu_type = pdu_type

    def __repr__(self):
        return f"PduIoInfo(robot_name={self.robot_name}, channel_id={self.channel_id}, org_name={self.org_name}, pdu_size={self.pdu_size}, pdu_type={self.pdu_type})"

    def __eq__(self, other):
        if not isinstance(other, PduIoInfo):
            return NotImplemented
        return (self.robot_name, self.channel_id, self.org_name, self.pdu_size, self.pdu_type) == \
               (other.robot_name, other.channel_id, other.org_name, other.pdu_size, other.pdu_type)

    def __hash__(self):
        return hash((self.robot_name, self.channel_id, self.org_name, self.pdu_size, self.pdu_type))

class PduChannelConfig:
    def __init__(self, json_file_path: str):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            self.config_dict = json.load(f)

    def update_pdudef(self, pdudef: dict):
        self.config_dict = pdudef

    def get_pdudef(self) -> dict:
        return self.config_dict

    def get_shm_pdu_readers(self) -> list:
        """Get the list of PDU readers."""
        pdu_readers = []
        for robot in self.config_dict.get("robots", []):
            for reader in robot.get("shm_pdu_readers", []):
                pdu_readers.append(PduIoInfo(
                    robot_name=robot.get("name"),
                    channel_id=reader.get("channel_id"),
                    org_name=reader.get("org_name"),
                    pdu_size=reader.get("pdu_size", -1),
                    pdu_type=reader.get("type")
                ))
        return pdu_readers

    def get_shm_pdu_writers(self) -> list:
        """Get the list of PDU writers."""
        pdu_writers = []
        for robot in self.config_dict.get("robots", []):
            for writer in robot.get("shm_pdu_writers", []):
                pdu_writers.append(PduIoInfo(
                    robot_name=robot.get("name"),
                    channel_id=writer.get("channel_id"),
                    org_name=writer.get("org_name"),
                    pdu_size=writer.get("pdu_size", -1),
                    pdu_type=writer.get("type")
                ))
        return pdu_writers

    def get_pdu_name(self, robot_name: str, channel_id: int) -> Optional[str]:
        for robot in self.config_dict.get("robots", []):
            if robot.get("name") == robot_name:
                for ch in robot.get("shm_pdu_readers", []) + robot.get("shm_pdu_writers", []):
                    if ch.get("channel_id") == channel_id:
                        return ch.get("org_name")
        return None

    def get_pdu_size(self, robot_name: str, pdu_name: str) -> int:
        for robot in self.config_dict.get("robots", []):
            if robot.get("name") == robot_name:
                for ch in robot.get("shm_pdu_readers", []) + robot.get("shm_pdu_writers", []):
                    if ch.get("org_name") == pdu_name:
                        return ch.get("pdu_size", -1)
        return -1
    def get_pdu_type(self, robot_name: str, pdu_name: str) -> Optional[str]:
        for robot in self.config_dict.get("robots", []):
            if robot.get("name") == robot_name:
                for ch in robot.get("shm_pdu_readers", []) + robot.get("shm_pdu_writers", []):
                    if ch.get("org_name") == pdu_name:
                        return ch.get("type")
        return None

    def get_pdu_channel_id(self, robot_name: str, pdu_name: str) -> int:
        for robot in self.config_dict.get("robots", []):
            if robot.get("name") == robot_name:
                for ch in robot.get("shm_pdu_readers", []) + robot.get("shm_pdu_writers", []):
                    if ch.get("org_name") == pdu_name:
                        return ch.get("channel_id", -1)
        return -1
