# hakoniwa-pdu-python

[![tests](https://github.com/hakoniwalab/hakoniwa-pdu-python/actions/workflows/tests.yml/badge.svg)](https://github.com/hakoniwalab/hakoniwa-pdu-python/actions/workflows/tests.yml)

This is a Python PDU communication library for the Hakoniwa simulator.
It allows easy sending/receiving of PDU binary data and conversion to/from JSON over WebSocket.

---

## 📦 Installation

```bash
pip install hakoniwa-pdu
```

Check the installed version:

```bash
pip show hakoniwa-pdu
```

---

## 🔧 Environment Variables

You can specify the directory containing `.offset` files used for PDU conversion:

```bash
export HAKO_BINARY_PATH=/your/path/to/offset
```

If not set, the default path will be:

```
/usr/local/lib/hakoniwa/hako_binary/offset
```

---

## 🚀 Example Usage

### Read a PDU from drone using test script

The following sample script receives the `pos` PDU from the drone and converts it into JSON.

`tests/sample.py`:

```python
# (your existing sample.py content goes here)
```

### Run example

```bash
python tests/sample.py \
  --config ./config/pdudef/webavatar.json \
  --uri ws://localhost:8765
```

---

## 📁 Package Structure

```
hakoniwa_pdu/
├── pdu_manager.py                  # Core PDU manager
├── impl/                           # Transport and utilities
│   ├── icommunication_service.py   # Transport interface
│   ├── websocket_communication_service.py      # WebSocket client
│   ├── websocket_server_communication_service.py  # WebSocket server
│   ├── shm_communication_service.py            # Shared memory transport
│   ├── pdu_convertor.py            # Binary ⇔ JSON conversion
│   ├── hako_binary/
│   │   └── *.py (Handles offsets and binary layout)
├── rpc/                            # RPC infrastructure
│   ├── ipdu_service_manager.py     # Base classes for RPC managers
│   ├── protocol_client.py          # High level RPC client helpers
│   ├── protocol_server.py          # High level RPC server helpers
│   ├── auto_wire.py                # Auto load protocol classes
│   ├── remote/                     # RPC over WebSocket
│   │   ├── remote_pdu_service_base_manager.py
│   │   ├── remote_pdu_service_client_manager.py
│   │   └── remote_pdu_service_server_manager.py
│   └── shm/                        # RPC over shared memory
│       ├── shm_pdu_service_base_manager.py
│       ├── shm_pdu_service_client_manager.py
│       └── shm_pdu_service_server_manager.py
├── resources/
│   └── offset/                     # Offset definition files
```

## 🏗️ Class Overview

### PduManager
- `PduManager` orchestrates PDU buffers and delegates transport to an `ICommunicationService`.
- Direct PDU I/O: declare channels with `declare_pdu_for_read/write` then use `flush_pdu_raw_data()` or `read_pdu_raw_data()`.
- RPC usage: extended via `rpc.IPduServiceManager` to handle `register_client`, `start_rpc_service`, and other RPC-specific APIs.

### Communication Implementations (`impl/`)
- `ICommunicationService` defines the transport API.
- `WebSocketCommunicationService` / `WebSocketServerCommunicationService` implement WebSocket transport.
- `ShmCommunicationService` enables high-speed shared-memory transport.
- Choose the backend by passing the desired implementation to `PduManager.initialize()`.

### RPC Layer (`rpc/`)
- `IPduServiceManager` family provides RPC APIs on top of `PduManager` with client/server variants and status codes.
- `protocol_client.py` and `protocol_server.py` wrap these managers into user-friendly protocol classes.
- `auto_wire.py` loads generated PDU converters and constructs protocol clients/servers automatically.
- `remote/` contains WebSocket-based managers; `shm/` provides shared-memory managers.
- `service_config.py` merges service definitions with base PDU definitions.

## 🧭 Class Diagram

```mermaid
classDiagram
    class PduManager
    PduManager --> ICommunicationService : uses
    PduManager --> CommunicationBuffer
    PduManager --> PduConvertor
    PduManager --> PduChannelConfig

    class ICommunicationService {
        <<interface>>
    }
    class WebSocketCommunicationService
    class WebSocketServerCommunicationService
    class ShmCommunicationService
    ICommunicationService <|.. WebSocketCommunicationService
    ICommunicationService <|.. WebSocketServerCommunicationService
    ICommunicationService <|.. ShmCommunicationService

    class IPduServiceManager {
        <<abstract>>
    }
    PduManager <|-- IPduServiceManager
    class IPduServiceClientManager
    class IPduServiceServerManager
    IPduServiceManager <|-- IPduServiceClientManager
    IPduServiceManager <|-- IPduServiceServerManager

    class RemotePduServiceBaseManager
    RemotePduServiceBaseManager <|-- RemotePduServiceClientManager
    RemotePduServiceBaseManager <|-- RemotePduServiceServerManager
    IPduServiceManager <|-- RemotePduServiceBaseManager

    class ShmPduServiceBaseManager
    ShmPduServiceBaseManager <|-- ShmPduServiceClientManager
    ShmPduServiceBaseManager <|-- ShmPduServiceServerManager
    IPduServiceManager <|-- ShmPduServiceBaseManager
```

---

## 🔗 Links

* 📘 GitHub: [https://github.com/hakoniwalab/hakoniwa-pdu-python](https://github.com/hakoniwalab/hakoniwa-pdu-python)
* 🌐 Hakoniwa Lab: [https://hakoniwa-lab.net](https://hakoniwa-lab.net)

---

## 📚 Documentation

For detailed API usage, refer to the full API reference:

➡️ [API Reference (api-doc.md)](./api-doc.md)

---

## 📜 License

MIT License - see [LICENSE](./LICENSE) for details.

