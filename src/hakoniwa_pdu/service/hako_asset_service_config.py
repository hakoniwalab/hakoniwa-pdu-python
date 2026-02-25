#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import hakopy
from hakoniwa_pdu.impl.hako_binary import offset_map
from hakoniwa_pdu.impl.pdudef_merge import append_legacy_pdudef
from hakoniwa_pdu.impl.service_pdudef_builder import (
    build_compact_pdudef,
    compact_to_legacy_pdudef,
)
from hakoniwa_pdu.impl.service_config_patch import (
    assign_channel_ids as assign_channel_ids_common,
    patch_service_base_size_file,
)

class HakoAssetServiceConfig:
    def __init__(self, service_config_path:str, offmap:offset_map.OffsetMap):
        self.service_config_path = service_config_path
        self.offmap = offmap
        self.service_config = self._load_json(service_config_path)
        if self.service_config is None:
            raise ValueError(f"Failed to load service config from {service_config_path}")

    def _get_pdu_definition(self):
        return compact_to_legacy_pdudef(self._get_pdu_definition_compact())

    def _get_pdu_definition_compact(self):
        return build_compact_pdudef(
            self.service_config,
            self.offmap,
            self._resolve_channel_ids,
        )

    def _resolve_channel_ids(self, service_id: int, client_id: int) -> tuple[int, int]:
        result = hakopy.asset_service_get_channel_id(service_id, client_id)
        if result is None:
            raise ValueError(f"Failed to get channel ID for service_id={service_id} client_id={client_id}")
        return result
    
    def get_pdu_name(self, robot_name: str, channel_id: int) -> str:
        for robot in self._get_pdu_definition_compact()['robots']:
            if robot['name'] == robot_name:
                for pdu in robot['pdus']:
                    if pdu['channel_id'] == channel_id:
                        return pdu['name']
        raise ValueError(f"PDU with channel ID {channel_id} not found in robot {robot_name}")

    def create_pdus(self):
        compact = self._get_pdu_definition_compact()
        for robot in compact['robots']:
            for pdu in robot['pdus']:
                ret = hakopy.pdu_create(robot['name'], pdu['channel_id'], pdu['pdu_size'])
                if ret == False:
                    print(f"ERROR: pdu_create() failed for {robot['name']} {pdu['channel_id']} {pdu['type']}")
                    continue
                else:
                    print(f"INFO: pdu_create() success for {robot['name']} {pdu['channel_id']} {pdu['type']}")
        self.pdu_definition = compact_to_legacy_pdudef(compact)
        print("INFO: PDU definitions created successfully")
        return self.pdu_definition


    def append_pdu_def(self, pdudef: dict):
        new_def = self._get_pdu_definition()
        return append_legacy_pdudef(pdudef, new_def)

    def _load_json(self, path):
        try:
            with open(path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"ERROR: File not found '{path}'")
        except json.JSONDecodeError:
            print(f"ERROR: Invalid Json fromat '{path}'")
        except PermissionError:
            print(f"ERROR: Permission denied '{path}'")
        except Exception as e:
            print(f"ERROR: {e}")
        return None
    

import argparse
from hakoniwa_pdu.impl.hako_binary.offset_map import create_offmap

def patch_service_base_size(service_json_path, offset_dir, output_path=None):
    offmap = create_offmap(offset_dir)
    updated = patch_service_base_size_file(service_json_path, offmap, output_path)
    if not updated:
        print("No changes made.")
        return
    out_path = output_path if output_path else service_json_path
    print(f"Patched file written to: {out_path}")

def assign_channel_ids(config):
    return assign_channel_ids_common(config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Patch service.json with baseSize")
    parser.add_argument("service_json", help="Path to service.json")
    parser.add_argument("offset_dir", help="Path to offset files")
    parser.add_argument("-o", "--output", help="Output file path", default=None)
    args = parser.parse_args()

    patch_service_base_size(args.service_json, args.offset_dir, args.output)
