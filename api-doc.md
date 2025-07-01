# Hakoniwa PDU Python API Documentation

## Overview

The `hakoniwa_pdu` package provides a high-level Python interface for managing PDU (Protocol Data Unit) communication in the Hakoniwa simulation environment. It includes two core classes:

* `PduManager`: Manages communication lifecycle, buffer registration, and PDU I/O.
* `PduConvertor`: Converts between binary PDU data and JSON, using offset definitions based on ROS IDL.

---

## PduManager

### Description

`PduManager` is the central class responsible for initializing communication, managing buffer state, and declaring and transferring PDUs. It internally uses `PduConvertor` for binary/JSON conversion.

### Usage Example

```python
from hakoniwa_pdu.pdu_manager import PduManager
from hakoniwa_pdu.impl.websocket_communication_service import WebSocketCommunicationService

manager = PduManager()
manager.initialize(config_path="path/to/config.json", comm_service=WebSocketCommunicationService())
await manager.start_service("ws://localhost:8765")
```

### Public Methods

* `initialize(config_path: str, comm_service: ICommunicationService)`

  * Initialize with PDU configuration and communication service instance.

* `start_service(uri: str) -> bool`

  * Start the underlying communication service.

* `stop_service() -> bool`

  * Stop the communication service.

* `declare_pdu_for_read(robot_name: str, pdu_name: str) -> bool`

  * Register a PDU channel for reading.

* `declare_pdu_for_write(robot_name: str, pdu_name: str) -> bool`

  * Register a PDU channel for writing.

* `read_pdu_raw_data(robot_name: str, pdu_name: str) -> Optional[bytearray]`

  * Read binary data from the buffer.

* `flush_pdu_raw_data(robot_name: str, pdu_name: str, pdu_raw_data: bytearray) -> bool`

  * Send raw binary data to the communication channel.

* `get_pdu_channel_id(robot_name: str, pdu_name: str) -> int`

  * Get internal PDU channel ID.

* `get_pdu_size(robot_name: str, pdu_name: str) -> int`

  * Get size of the binary buffer for the given PDU.

* `log_current_state()`

  * Print internal states for debugging.

### Notes

* Binary/JSON conversion must be performed using `PduConvertor`.
* Offset data directory path can be resolved via `get_default_offset_path()`.

---

## PduConvertor

### Description

`PduConvertor` handles binary serialization and deserialization of PDU data based on ROS IDL-derived offset maps.

### Usage Example

```python
convertor = PduConvertor("/path/to/offset", pdu_config)
data = convertor.create_empty_pdu_json("Drone", "pos")
binary = convertor.convert_json_to_binary("Drone", "pos", data)
json_data = convertor.convert_binary_to_json("Drone", "pos", binary)
```

### Public Methods

* `create_empty_pdu_json(robot_name: str, pdu_name: str) -> dict`

  * Generate an empty JSON dictionary initialized with default values.

* `convert_json_to_binary(robot_name: str, pdu_name: str, json_data: dict) -> bytearray`

  * Convert a structured JSON dictionary to binary.

* `convert_binary_to_json(robot_name: str, pdu_name: str, binary_data: bytearray) -> dict`

  * Convert binary data back into a JSON dictionary.

### Notes

* The offset path should be set from the environment variable `HAKO_BINARY_PATH` or default to `/usr/local/lib/hakoniwa/hako_binary/offset`.
* Offset maps must match the PDU definitions described in the JSON config.

---

## Environment Variables

* `HAKO_BINARY_PATH`: Override the path to `.offset` binary definition files.

---

## See Also

* GitHub: [hakoniwalab/hakoniwa-pdu-python](https://github.com/hakoniwalab/hakoniwa-pdu-python)
* Offset definitions: Typically generated via ROS2 IDL conversion tools.
* Example: See `tests/sample.py` for basic usage.
