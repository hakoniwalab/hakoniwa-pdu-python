import json


def assign_channel_ids(config: dict) -> bool:
    updated = False
    for node in config.get("nodes", []):
        current_id = 0
        for topic in node.get("topics", []):
            topic["channel_id"] = current_id
            current_id += 1
            updated = True
    return updated


def patch_service_base_size_data(config: dict, offmap) -> bool:
    updated = False
    for srv in config.get("services", []):
        pdu_size = srv.get("pduSize", {})
        if "server" in pdu_size and "baseSize" not in pdu_size["server"]:
            req_type = srv["type"] + "RequestPacket"
            pdu_size["server"]["baseSize"] = offmap.get_pdu_size(req_type)
            updated = True
        if "client" in pdu_size and "baseSize" not in pdu_size["client"]:
            res_type = srv["type"] + "ResponsePacket"
            pdu_size["client"]["baseSize"] = offmap.get_pdu_size(res_type)
            updated = True

    if assign_channel_ids(config):
        updated = True
    return updated


def patch_service_base_size_file(service_json_path: str, offmap, output_path: str | None = None) -> bool:
    with open(service_json_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    updated = patch_service_base_size_data(config, offmap)
    if not updated:
        return False

    out_path = output_path if output_path else service_json_path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    return True
