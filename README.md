# hakoniwa-pdu-python

[![tests](https://github.com/hakoniwalab/hakoniwa-pdu-python/actions/workflows/tests.yml/badge.svg)](https://github.com/hakoniwalab/hakoniwa-pdu-python/actions/workflows/tests.yml)

**Python PDU communication library for the Hakoniwa simulator.**
Provides a unified transport layer where **RPC** and **Pub/Sub (topics)** run seamlessly over WebSocket.
For high-speed use cases, a **Shared Memory (SHM)** backend is also available.
The architecture is extensible to **Zenoh**, enabling scalable and distributed systems.
Binary ⇔ JSON ⇔ Python type conversion is built-in, reducing boilerplate to a minimum.

---

## ✨ Features

* **Unified layer**: RPC and Pub/Sub integrated on top of WebSocket
* **Automatic type conversion**: safely convert between binary, JSON, and Python types with offset definitions
* **Transport flexibility**: choose between **WebSocket**, **Shared Memory (SHM)**, and extensible backends such as **Zenoh**
* **Explicit & secure connections**: WebSocket URIs (`ws://...`) clearly define communication scope
* **Event-driven & polling support**: register handlers or poll buffers as needed
* **Ready-to-run samples**: minimal examples for `Twist` (topic) and `AddTwoInts` (RPC) included

---

## 📦 Installation

```bash
pip install hakoniwa-pdu
pip show hakoniwa-pdu   # check version
```

### Foundation Core Python binding contract

When this package is installed through `tools/hako.py`, the Core Python
binding is resolved from the installed Core Component Receipt:

```text
<core-prefix>/share/hakoniwa/receipts/hakoniwa-core-pro.yaml
  -> python.artifact
```

The declared artifact may use the platform's ABI-tagged extension name, such
as `hakopy.cp312-win_amd64.pyd` on Windows. `doctor` and `install` use this
same Receipt declaration and reject a missing artifact, an incompatible
extension, or a path outside the Core install prefix. They do not create or
rename an undeclared `hakopy.pyd`/`hakopy.so` compatibility copy. For a legacy
Core Receipt that predates `python.artifact`, only one extension recognized by
the running Python interpreter may be selected; no candidate or multiple
candidates are rejected. The final `import hakopy` smoke check runs with the
Foundation virtual environment.

### Environment Variables

Specify the directory containing `.offset` files for PDU conversion:

```bash
export HAKO_BINARY_PATH=/your/path/to/offset
```

Default path if unset:

```
/usr/local/lib/hakoniwa/hako_binary/offset
```

### PDU Config Formats (`--pdu-config`)

`hakoniwa-pdu-python` accepts both:

* **Compact format** (recommended): `paths` + `robots[].pdutypes_id`
* **Legacy format**: `robots[].shm_pdu_readers/shm_pdu_writers/...`

Internally, the library normalizes both formats and keeps backward compatibility
for existing legacy-based APIs.

Compact example (`pdudef.json`):

```json
{
  "paths": [
    { "id": "default", "path": "pdutypes.json" }
  ],
  "robots": [
    { "name": "RobotA", "pdutypes_id": "default" }
  ]
}
```

Compact types file (`pdutypes.json`):

```json
[
  { "channel_id": 0, "pdu_size": 72, "name": "pos", "type": "geometry_msgs/Twist" }
]
```

---

## 🚀 Quick Start (3 commands)

> Example 1: **WebSocket Topic** (`geometry_msgs/Twist` publish → subscribe)

1. **Publisher (server)**

```bash
python examples/topic/websocket/remote_publisher.py \
  --uri ws://localhost:8080 \
  --pdu-config examples/pdu_config.json \
  --service-config examples/service.json
```

2. **Subscriber (client)**

```bash
python examples/topic/websocket/remote_subscriber.py \
  --uri ws://localhost:8080 \
  --pdu-config examples/pdu_config.json \
  --service-config examples/service.json
```

3. **Output**

```
[INFO] Received Twist: linear.x=0 angular.z=0
[INFO] Received Twist: linear.x=1 angular.z=1
```

---

> Example 2: **WebSocket RPC** (`AddTwoInts` service)

1. **RPC Server**

```bash
python examples/rpc/websocket/remote_rpc_server.py \
  --uri ws://localhost:8080 \
  --pdu-config examples/pdu_config.json \
  --service-config examples/service.json
```

2. **RPC Client**

```bash
python examples/rpc/websocket/remote_rpc_client.py \
  --uri ws://localhost:8080 \
  --pdu-config examples/pdu_config.json \
  --service-config examples/service.json
```

3. **Output**

```
Response: 3
```

---

## 📡 Event-Driven PDU Handling

Server:

```python
server_manager.register_handler_pdu_data(on_pdu)

def on_pdu(client_id, packet):
    ...
```

Client:

```python
client_manager.register_handler_pdu_data(on_pdu)

def on_pdu(packet):
    ...
```

Polling via `contains_buffer()` / `get_buffer()` is also available.

---

## 📁 Project Structure

```
hakoniwa_pdu/
├── pdu_manager.py
├── impl/
│   ├── icommunication_service.py
│   ├── websocket_communication_service.py
│   ├── websocket_server_communication_service.py
│   ├── shm_communication_service.py
│   ├── pdu_convertor.py
│   └── hako_binary/
├── rpc/
│   ├── ipdu_service_manager.py
│   ├── profile.py
│   ├── protocol_client.py
│   ├── protocol_server.py
│   ├── auto_wire.py
│   ├── async_shared/
│   ├── remote/
│   └── shm/
├── resources/
│   └── offset/
└── examples/
```

---

## 📝 Design Notes

RPC client redesign notes for large-scale SHM fan-out:

- `docs/rpc/async_shared_runtime.md`

---

## ⚡ Shared SHM RPC Runtime

For high fan-out SHM RPC workloads, `hakoniwa-pdu-python` also provides a
shared client runtime under `hakoniwa_pdu.rpc.async_shared`.

Core classes:

* `SharedRpcRuntime`: owns one shared `ShmPduServiceClientManager`, client registration cache, and pending request table.
* `AsyncRpcClientHandle`: lightweight logical RPC client bound to one service/client pair.
* `RpcCallFuture`: completion handle returned by `call_async()`.

Typical usage:

```python
from hakoniwa_pdu.rpc.async_shared import AsyncRpcClientHandle, SharedRpcRuntime

runtime = SharedRpcRuntime(
    asset_name="DroneExternalClient",
    pdu_config_path="pdu_config.json",
    service_config_path="service.json",
    offset_path="offset",
    delta_time_usec=10000,
)

client = AsyncRpcClientHandle(
    runtime=runtime,
    service_name="MyService",
    client_name="MyClient",
    cls_req_packet=ReqPacket,
    req_encoder=req_encoder,
    req_decoder=req_decoder,
    cls_res_packet=ResPacket,
    res_encoder=res_encoder,
    res_decoder=res_decoder,
)

client.register()
future = client.call_async(request_data, timeout_msec=30000, poll_interval=0.01)

while not future.done():
    runtime.poll_once()

response = future.result()
```

Use this path when one Python process needs to manage many concurrent SHM RPC
clients efficiently. For the detailed design and ownership model, see
`docs/rpc/async_shared_runtime.md`.

---

## 🧰 Hakoniwa Launcher

`hako_launcher.py` orchestrates multiple Hakoniwa assets described in a JSON file. The
launcher handles environment preparation, process supervision, and optional
notifications when an asset exits unexpectedly.

### How to run

```bash
# Basic usage (immediate mode)
python -m hakoniwa_pdu.apps.launcher.hako_launcher path/to/launch.json

# Immediate mode with background exit (skip monitoring loop)
python -m hakoniwa_pdu.apps.launcher.hako_launcher path/to/launch.json --no-watch

# Interactive control (serve mode)
python -m hakoniwa_pdu.apps.launcher.hako_launcher path/to/launch.json --mode serve

# OS-independent background lifecycle control
python -m hakoniwa_pdu.apps.launcher.hako_launcher path/to/launch.json \
  --background ./run/launcher-session.json
```

* **Immediate mode** (default) performs `activate → hako-cmd start → watch`.
  * Assets whose `activation_timing` is `"before_start"` are spawned first.
  * After `hako-cmd start` completes successfully, assets with
    `"after_start"` are started.
  * Unless `--no-watch` is specified, the launcher keeps monitoring child
    processes. If any asset stops, every remaining asset is terminated.
* **Serve mode** keeps the process alive and accepts commands via STDIN.
  Available commands: `activate`, `start`, `stop`, `reset`, `terminate`,
  `status`, `quit`/`exit`.

Set `HAKO_PDU_DEBUG=1` to enable debug logging from the launcher modules.

For background `status` / `terminate` commands, session ownership, startup
failure handling, and stale-session behavior, see
[`docs/launcher-background-lifecycle.md`](docs/launcher-background-lifecycle.md).

### Launcher JSON format

The schema is provided at
`src/hakoniwa_pdu/apps/launcher/schemas/launcher.schema.json`. A minimal
configuration consists of a version header, optional defaults, and at least one
asset definition.

```jsonc
{
  "version": "0.1",
  "runtime": {
    "cleanup_mmap_on_start": false
  },
  "defaults": {
    "cwd": ".",
    "stdout": "logs/${asset}.out",
    "stderr": "logs/${asset}.err",
    "start_grace_sec": 1,
    "delay_sec": 3,
    "env": {
      "prepend": {
        "PATH": ["/usr/bin"]
      }
    }
  },
  "assets": [
    {
      "name": "drone",
      "command": "linux-main_hako_aircraft_service_px4",
      "args": ["127.0.0.1", "4560"],
      "activation_timing": "before_start",
      "readiness": {
        "type": "hako_asset",
        "asset_name": "drone",
        "timeout_sec": 30
      }
    }
  ]
}
```

#### Top level keys

| Key        | Description |
| ---------- | ----------- |
| `version`  | Free-form version string for the specification.【F:src/hakoniwa_pdu/apps/launcher/model.py†L82-L90】 |
| `runtime`  | Optional Launcher-owned runtime preparation. `cleanup_mmap_on_start` is disabled by default and removes only Hakoniwa mmap/lock files before any asset starts. Enable it only when this Launcher exclusively owns the configured runtime directory. |
| `defaults` | Shared defaults applied to every asset when the field is omitted at the asset level. Paths are resolved relative to the launch file.【F:src/hakoniwa_pdu/apps/launcher/loader.py†L47-L91】 |
| `assets`   | Array of process definitions. Launch order is automatically sorted by `depends_on` while preserving the original order when there is no dependency.【F:src/hakoniwa_pdu/apps/launcher/model.py†L112-L167】 |
| `notify`   | Optional notification that fires when an asset exits or the launcher aborts. Supports `webhook` and `exec` variants.【F:src/hakoniwa_pdu/apps/launcher/model.py†L58-L80】【F:src/hakoniwa_pdu/apps/launcher/hako_monitor.py†L83-L121】 |

#### Defaults block

* `cwd`, `stdout`, `stderr`: default working directory and log sinks for assets.
  These support `${asset}`, `${timestamp}`, and `${base_dir}` placeholders. The
  loader resolves relative paths using the directory of the launch file.【F:src/hakoniwa_pdu/apps/launcher/loader.py†L30-L91】【F:src/hakoniwa_pdu/apps/launcher/hako_monitor.py†L19-L35】
* `start_grace_sec`: minimum time (seconds) an asset must stay alive after
  spawn to be considered healthy (default `5.0`).【F:src/hakoniwa_pdu/apps/launcher/model.py†L40-L54】
* `delay_sec`: delay inserted before launching the next asset (default `3.0`).【F:src/hakoniwa_pdu/apps/launcher/model.py†L40-L54】
* `env`: environment operations merged into the runtime environment in three
  stages: OS env → defaults.env → asset.env. Keys `set`, `prepend`, `append`,
  and `unset` are supported, and `lib_path` automatically maps to
  `LD_LIBRARY_PATH`/`DYLD_LIBRARY_PATH`/`PATH` depending on the platform.【F:src/hakoniwa_pdu/apps/launcher/model.py†L12-L37】【F:src/hakoniwa_pdu/apps/launcher/envmerge.py†L1-L103】

Environment variables written as `${VAR}` or `${VAR:-default}` inside the JSON
are resolved when the file is loaded. Placeholders `${asset}` and `${timestamp}`
are preserved for runtime expansion inside log paths and environment settings.【F:src/hakoniwa_pdu/apps/launcher/loader.py†L18-L67】

#### Asset entries

| Field                | Description |
| -------------------- | ----------- |
| `name`               | Asset identifier. Used for dependency checks and placeholders.【F:src/hakoniwa_pdu/apps/launcher/model.py†L56-L115】 |
| `command` / `args`   | Executable and argument vector passed to the process.【F:src/hakoniwa_pdu/apps/launcher/hako_monitor.py†L40-L77】 |
| `cwd`                | Working directory. Defaults to the launch file directory or `defaults.cwd`.【F:src/hakoniwa_pdu/apps/launcher/loader.py†L47-L91】 |
| `stdout` / `stderr`  | Optional log file destinations. Directories are created automatically and support placeholders. Leave `null` to inherit the parent stream.【F:src/hakoniwa_pdu/apps/launcher/hako_asset_runner.py†L60-L117】 |
| `delay_sec`          | Wait time before the next asset starts (overrides `defaults.delay_sec`).【F:src/hakoniwa_pdu/apps/launcher/model.py†L94-L107】 |
| `activation_timing`  | `before_start` launches prior to `hako-cmd start`; `after_start` launches only after a successful `hako-cmd start`.【F:src/hakoniwa_pdu/apps/launcher/model.py†L94-L107】【F:src/hakoniwa_pdu/apps/launcher/hako_launcher.py†L28-L70】 |
| `depends_on`         | List of other asset names that must start before this one. Cycles are rejected during load.【F:src/hakoniwa_pdu/apps/launcher/model.py†L112-L167】 |
| `start_grace_sec`    | Asset-specific stability grace period overriding `defaults.start_grace_sec`.【F:src/hakoniwa_pdu/apps/launcher/model.py†L94-L107】【F:src/hakoniwa_pdu/apps/launcher/hako_monitor.py†L40-L77】 |
| `readiness`          | Optional readiness gate. `type: "hako_asset"` polls bounded `hako-cmd ls` calls until `asset_name` is registered, before launching the next process. Omit this field for HTTP servers, external clients, and other processes that do not register as Hakoniwa assets. |
| `env`                | Environment overrides merged on top of `defaults.env`. Supports `${asset}`, `${timestamp}`, and `${ENV:VAR}` substitutions at runtime.【F:src/hakoniwa_pdu/apps/launcher/envmerge.py†L14-L103】 |

The `hako_asset` readiness gate accepts `timeout_sec` (default `30`),
`poll_interval_sec` (default `0.2`), and `command_timeout_sec` (default `1`).
The command timeout prevents a stalled `hako-cmd ls` probe from blocking the
Launcher indefinitely. A readiness timeout aborts startup before
`hako-cmd start` is issued.

At Launcher activation, `hako-cmd --version` is checked once. With hako-cmd
1.0.1 or newer, each command receives a bounded native file-lock wait; readiness
keeps its slightly longer Python subprocess timeout as an outer watchdog. Older
or unrecognized hako-cmd versions remain on the legacy command line, so existing
installations continue to work without the new option.

When `runtime.cleanup_mmap_on_start` is `true`, the Launcher resolves
`HAKO_CONFIG_PATH`, reads `core_mmap_path`, and removes only `mmap-0x*.bin`,
`flock.bin`, `pdu_init.lock`, and `pro_init.lock` before starting any asset. It
does not delete runtime files on shutdown. This option is an explicit ownership
declaration: do not enable it when another Launcher or Hakoniwa process may use
the same mmap directory.

#### Notify section

* `type: "exec"` executes a local command when the launcher aborts (placeholders
  `${asset}` and `${timestamp}` are available).【F:src/hakoniwa_pdu/apps/launcher/model.py†L58-L80】【F:src/hakoniwa_pdu/apps/launcher/hako_monitor.py†L83-L121】
* `type: "webhook"` issues an HTTP POST with the event name, asset, and
  timestamp. Use for integrations such as Slack or monitoring dashboards.【F:src/hakoniwa_pdu/apps/launcher/model.py†L58-L80】【F:src/hakoniwa_pdu/apps/launcher/hako_monitor.py†L83-L121】

Refer to the sample JSON provided above for a real-world configuration that
launches a drone asset together with supporting services.

---

## 🧭 Class Overview

### PduManager

* Orchestrates PDU buffers and delegates to a transport (`ICommunicationService`).
* Direct I/O: `declare_pdu_for_read/write` → `flush_pdu_raw_data()` / `read_pdu_raw_data()`.
* For RPC: extended via `rpc.IPduServiceManager` (handles `register_client`, `start_rpc_service`, etc.).

### Transport Implementations (`impl/`)

* `ICommunicationService` defines the transport API.
* `WebSocketCommunicationService` / `WebSocketServerCommunicationService`: WebSocket backend (explicit URI-based connection, simple & secure).
* `ShmCommunicationService`: high-speed shared memory backend.
* **Pluggable design**: additional transports (e.g., **Zenoh**) can be integrated without changing application code.

### RPC Layer (`rpc/`)

* `IPduServiceManager` family provides RPC APIs (client/server).
* `protocol_client.py` / `protocol_server.py`: user-friendly helpers.
* `auto_wire.py`: auto-loads generated converters.
* `async_shared/`: shared SHM RPC runtime for manual/background polling and many logical clients per process.
* `remote/`: WebSocket managers.
* `shm/`: SHM managers.
* `profile.py`: lightweight profiling helpers shared by RPC components.

---

## 🧩 Class Diagram (Mermaid)

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

For detailed API usage:
➡️ [API Reference (api-doc.md)](./api-doc.md)

---

## 📜 License

MIT License — see [LICENSE](./LICENSE)


## Separate generated build state

`tools/hako.py` accepts `--state-dir <directory>` on each operation. Without
this option, generated state stays in `<repository>/.hako` for compatibility.
An explicit path may be outside the repository; relative paths use the calling
shell's current directory, and `~` and symlinks are resolved.

Use the same state directory for every operation in a build/install sequence.
Resolved configuration and the configuration copied into the Component Receipt
come from that directory. Existing repository-local state is not moved or deleted.
Build and install directories remain separate options/manifest settings and must
also be distinct when sharing sources between environments.

Business Pack supplies `<HAKONIWA_WORK_DIR>/foundation/state/<component>` explicitly;
standalone invocations should supply their own `--state-dir`.
