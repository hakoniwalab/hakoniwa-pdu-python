from typing import Callable, Optional


def build_legacy_pdudef(
    service_config: dict,
    offmap,
    channel_id_resolver: Optional[Callable[[int, int], tuple[int, int]]] = None,
) -> dict:
    compact = build_compact_pdudef(service_config, offmap, channel_id_resolver)
    return compact_to_legacy_pdudef(compact)


def build_compact_pdudef(
    service_config: dict,
    offmap,
    channel_id_resolver: Optional[Callable[[int, int], tuple[int, int]]] = None,
) -> dict:
    pdu_meta_size = service_config["pduMetaDataSize"]
    robots = []
    _append_service_robots_compact(robots, service_config, pdu_meta_size, offmap, channel_id_resolver)
    _append_node_robots_compact(robots, service_config, pdu_meta_size, offmap)
    return {"robots": robots}


def compact_to_legacy_pdudef(compact_pdudef: dict) -> dict:
    robots = []
    for robot in compact_pdudef.get("robots", []):
        readers = []
        writers = []
        for pdu in robot.get("pdus", []):
            org_name = pdu["name"]
            entry = {
                "type": pdu["type"],
                "org_name": org_name,
                "name": f"{robot['name']}_{org_name}",
                "channel_id": pdu["channel_id"],
                "pdu_size": pdu["pdu_size"],
                "write_cycle": 1,
                "method_type": "SHM",
            }
            direction = pdu.get("io", "both")
            if direction in ("read", "both"):
                readers.append(entry)
            if direction in ("write", "both"):
                writers.append(entry)
        robots.append({
            "name": robot["name"],
            "rpc_pdu_readers": [],
            "rpc_pdu_writers": [],
            "shm_pdu_readers": readers,
            "shm_pdu_writers": writers,
        })
    return {"robots": robots}


def _append_service_robots_compact(
    robots: list,
    service_config: dict,
    pdu_meta_size: int,
    offmap,
    channel_id_resolver: Optional[Callable[[int, int], tuple[int, int]]],
):
    service_id = 0
    for entry in service_config.get("services", []):
        name = entry["name"]
        pdu_type = entry["type"]
        max_clients = entry["maxClients"]
        pdu_size = entry["pduSize"]

        robot = {
            "name": name,
            "pdus": [],
        }

        for client_id in range(max_clients):
            if channel_id_resolver is None:
                req_id, res_id = (-1, -1)
            else:
                req_id, res_id = channel_id_resolver(service_id, client_id)
            req_type = pdu_type + "RequestPacket"
            res_type = pdu_type + "ResponsePacket"
            req_base_size = offmap.get_pdu_size(req_type)
            res_base_size = offmap.get_pdu_size(res_type)
            robot["pdus"].append({
                "type": req_type,
                "name": "req_" + str(client_id),
                "channel_id": req_id,
                "pdu_size": pdu_meta_size + req_base_size + pdu_size["server"]["heapSize"],
                "io": "read",
            })
            robot["pdus"].append({
                "type": res_type,
                "name": "res_" + str(client_id),
                "channel_id": res_id,
                "pdu_size": pdu_meta_size + res_base_size + pdu_size["client"]["heapSize"],
                "io": "write",
            })
        robots.append(robot)
        service_id += 1


def _append_node_robots_compact(robots: list, service_config: dict, pdu_meta_size: int, offmap):
    for node in service_config.get("nodes", []):
        robot = {
            "name": node["name"],
            "pdus": [],
        }
        for topic in node.get("topics", []):
            base_size = offmap.get_pdu_size(topic["type"])
            robot["pdus"].append({
                "type": topic["type"],
                "name": topic["topic_name"],
                "channel_id": topic["channel_id"],
                "pdu_size": pdu_meta_size + base_size + topic["pduSize"]["heapSize"],
                "io": "both",
            })
        robots.append(robot)
