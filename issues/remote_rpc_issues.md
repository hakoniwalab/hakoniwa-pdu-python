# Remote RPC Implementation Issues

The following concerns were identified during the review of the remote RPC implementation (`rpc/remote/remote_pdu_service_manager.py`). These should be investigated and addressed.

1. **Response channel mismatch**
   - Client registration uses `response_channel_id`, but normal responses are sent via `request_channel_id`.
   - According to the specification, server responses should use `response_channel_id`.

2. **`cancel_request` encoding and transmission**
   - `_client_instance_request_buffer` holds `DataPacket` objects, yet `req_decoder` attempts to decode raw bodies, losing header information.
   - `cancel_request` sends only the PDU body with `send_binary(pdu_data)` instead of using `_build_binary`, so metadata may be missing.
   - Sets a non-existent `poll_interval_msec` field; likely intended `status_poll_interval_msec`.

3. **Client service configuration path**
   - `register_client` references `self.service_config_path` which is never initialized, leading to `AttributeError`.

4. **Other notes**
   - `poll_response` increments `_client_instance_request_id` without clear linkage to other processes.
   - Several methods remain `NotImplemented` (`start_rpc_service_nowait`, etc.).

