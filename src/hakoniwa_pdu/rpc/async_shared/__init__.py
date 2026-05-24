__all__ = [
    "AsyncRpcClientHandle",
    "RpcCallFuture",
    "SharedRpcRuntime",
    "SharedRpcRuntimeConfig",
]


def __getattr__(name: str):
    if name == "AsyncRpcClientHandle":
        from .async_rpc_client import AsyncRpcClientHandle

        return AsyncRpcClientHandle
    if name == "RpcCallFuture":
        from .rpc_call_future import RpcCallFuture

        return RpcCallFuture
    if name == "SharedRpcRuntime":
        from .shared_rpc_runtime import SharedRpcRuntime

        return SharedRpcRuntime
    if name == "SharedRpcRuntimeConfig":
        from .shared_rpc_runtime import SharedRpcRuntimeConfig

        return SharedRpcRuntimeConfig
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
