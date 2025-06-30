import json
from typing import Optional


class PduChannelConfig:
    def __init__(self, json_file_path: str):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            self.config_dict = json.load(f)

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
