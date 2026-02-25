import json
import os
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
        self._base_dir = os.path.dirname(os.path.abspath(json_file_path))
        with open(json_file_path, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        self.config_dict = self._normalize_to_legacy(config_dict, self._base_dir)
        self._rebuild_indices()

    def update_pdudef(self, pdudef: dict):
        self.config_dict = self._normalize_to_legacy(pdudef, self._base_dir)
        self._rebuild_indices()

    def get_pdudef(self) -> dict:
        return self.config_dict

    def get_pdudef_compact(self) -> dict:
        robots_compact = []
        for robot in self.config_dict.get("robots", []):
            seen = set()
            pdus = []
            channels = robot.get("shm_pdu_readers", []) + robot.get("shm_pdu_writers", [])
            for ch in channels:
                pdu_name = ch.get("org_name")
                pdu_type = ch.get("type")
                channel_id = ch.get("channel_id")
                pdu_size = ch.get("pdu_size")
                key = (pdu_name, channel_id, pdu_type)
                if key in seen:
                    continue
                seen.add(key)
                pdus.append({
                    "name": pdu_name,
                    "type": pdu_type,
                    "channel_id": channel_id,
                    "pdu_size": pdu_size,
                })
            robots_compact.append({
                "name": robot.get("name"),
                "pdus": pdus,
            })
        return {"robots": robots_compact}

    def _normalize_to_legacy(self, pdudef: dict, base_dir: str) -> dict:
        if "paths" in pdudef:
            return self._convert_compact_to_legacy(pdudef, base_dir)
        return self._ensure_legacy_shape(pdudef)

    def _ensure_legacy_shape(self, pdudef: dict) -> dict:
        robots = []
        for robot in pdudef.get("robots", []):
            robots.append({
                "name": robot.get("name"),
                "rpc_pdu_readers": robot.get("rpc_pdu_readers", []),
                "rpc_pdu_writers": robot.get("rpc_pdu_writers", []),
                "shm_pdu_readers": robot.get("shm_pdu_readers", []),
                "shm_pdu_writers": robot.get("shm_pdu_writers", []),
            })
        return {"robots": robots}

    def _convert_compact_to_legacy(self, pdudef: dict, base_dir: str) -> dict:
        pdutypes_map = {}
        for path_info in pdudef.get("paths", []):
            pdutypes_id = path_info.get("id")
            pdutypes_path = path_info.get("path")
            if not pdutypes_id or not pdutypes_path:
                continue
            if os.path.isabs(pdutypes_path):
                resolved_path = pdutypes_path
            else:
                resolved_path = os.path.join(base_dir, pdutypes_path)
            with open(resolved_path, 'r', encoding='utf-8') as f:
                pdutypes_map[pdutypes_id] = json.load(f)

        robots = []
        for robot in pdudef.get("robots", []):
            robot_name = robot.get("name")
            pdutypes_id = robot.get("pdutypes_id")
            pdutypes = pdutypes_map.get(pdutypes_id, [])
            seen = set()
            shm_pdus = []
            for pdu in pdutypes:
                org_name = pdu.get("name")
                pdu_type = pdu.get("type")
                channel_id = pdu.get("channel_id")
                pdu_size = pdu.get("pdu_size")
                dedup_key = (org_name, channel_id, pdu_type)
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)
                shm_pdus.append({
                    "type": pdu_type,
                    "org_name": org_name,
                    "name": f"{robot_name}_{org_name}",
                    "channel_id": channel_id,
                    "pdu_size": pdu_size,
                    "write_cycle": 1,
                    "method_type": "SHM",
                })
            robots.append({
                "name": robot_name,
                "rpc_pdu_readers": [],
                "rpc_pdu_writers": [],
                "shm_pdu_readers": list(shm_pdus),
                "shm_pdu_writers": list(shm_pdus),
            })
        return {"robots": robots}

    def _rebuild_indices(self):
        self._name_by_robot_channel = {}
        self._size_by_robot_name = {}
        self._type_by_robot_name = {}
        self._channel_by_robot_name = {}

        for robot in self.config_dict.get("robots", []):
            robot_name = robot.get("name")
            channels = robot.get("shm_pdu_readers", []) + robot.get("shm_pdu_writers", [])
            for ch in channels:
                channel_id = ch.get("channel_id")
                org_name = ch.get("org_name")
                if robot_name is None or channel_id is None or org_name is None:
                    continue
                self._name_by_robot_channel[(robot_name, channel_id)] = org_name
                self._size_by_robot_name[(robot_name, org_name)] = ch.get("pdu_size", -1)
                self._type_by_robot_name[(robot_name, org_name)] = ch.get("type")
                self._channel_by_robot_name[(robot_name, org_name)] = channel_id

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
        return self._name_by_robot_channel.get((robot_name, channel_id))

    def get_pdu_size(self, robot_name: str, pdu_name: str) -> int:
        return self._size_by_robot_name.get((robot_name, pdu_name), -1)
    def get_pdu_type(self, robot_name: str, pdu_name: str) -> Optional[str]:
        return self._type_by_robot_name.get((robot_name, pdu_name))

    def get_pdu_channel_id(self, robot_name: str, pdu_name: str) -> int:
        return self._channel_by_robot_name.get((robot_name, pdu_name), -1)
