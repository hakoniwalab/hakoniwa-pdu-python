# Remote RPC Implementation Issues

The following concerns were previously identified in `rpc/remote/remote_pdu_service_manager.py`.

## Resolved
- Response channel mismatch: responses now use `response_channel_id`.
- `cancel_request` encoding: rebuilds the packet with `_build_binary` before resending.
- Client service configuration path: `service_config_path` is validated before client registration.

## Outstanding
1. `poll_response` increments `_client_instance_request_id` without clear linkage to other processes.
2. Several methods remain `NotImplemented` (`start_rpc_service_nowait`, etc.).

