from typing import Any


def append_legacy_pdudef(pdudef: dict | None, new_def: dict) -> dict:
    """
    Merge a generated legacy pdudef into an existing pdudef object.
    Existing objects may already be legacy, compact-like, or mixed.
    """
    if pdudef is None:
        return new_def

    pdudef.setdefault("robots", [])

    def update_or_add_pdu(robot_entry: dict, pdu_list_name: str, new_pdu: dict):
        pdu_list = robot_entry.setdefault(pdu_list_name, [])
        for idx, existing_pdu in enumerate(pdu_list):
            if existing_pdu["channel_id"] == new_pdu["channel_id"]:
                pdu_list[idx] = new_pdu
                return
        pdu_list.append(new_pdu)

    def find_robot_by_name(_pdudef: dict, name: str) -> Any:
        for robot in _pdudef["robots"]:
            if robot["name"] == name:
                return robot
        return None

    for new_robot in new_def.get("robots", []):
        new_name = new_robot["name"]
        existing_robot = find_robot_by_name(pdudef, new_name)

        if not existing_robot:
            pdudef["robots"].append(new_robot)
            continue

        for reader in new_robot.get("shm_pdu_readers", []):
            update_or_add_pdu(existing_robot, "shm_pdu_readers", reader)
        for writer in new_robot.get("shm_pdu_writers", []):
            update_or_add_pdu(existing_robot, "shm_pdu_writers", writer)

    return pdudef
