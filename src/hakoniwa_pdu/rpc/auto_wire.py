"""Utility helpers to construct ProtocolClient/Server with minimal imports."""
from importlib import import_module
from typing import Any, Tuple, Type, Callable, Optional, Sequence, Dict
import asyncio


def _load_protocol_components(srv: str, pkg: str) -> Tuple[type, type, Callable, Callable, Callable, Callable]:
    """Dynamically load packet classes and converters for a service.

    Parameters
    ----------
    srv: str
        Service name such as ``"AddTwoInts"``.
    pkg: str
        Base package where PDU modules reside.

    Returns
    -------
    tuple
        ``(ReqPacket, ResPacket, req_encoder, req_decoder, res_encoder, res_decoder)``
    """
    req_packet_mod = f"{pkg}.pdu_pytype_{srv}RequestPacket"
    res_packet_mod = f"{pkg}.pdu_pytype_{srv}ResponsePacket"
    req_conv_mod = f"{pkg}.pdu_conv_{srv}RequestPacket"
    res_conv_mod = f"{pkg}.pdu_conv_{srv}ResponsePacket"

    try:
        ReqPacket = getattr(import_module(req_packet_mod), f"{srv}RequestPacket")
        ResPacket = getattr(import_module(res_packet_mod), f"{srv}ResponsePacket")
        req_conv = import_module(req_conv_mod)
        res_conv = import_module(res_conv_mod)
    except (ImportError, AttributeError) as e:
        raise RuntimeError(f"Failed to load protocol components for service '{srv}'") from e

    try:
        req_encoder = getattr(req_conv, f"py_to_pdu_{srv}RequestPacket")
        req_decoder = getattr(req_conv, f"pdu_to_py_{srv}RequestPacket")
        res_encoder = getattr(res_conv, f"py_to_pdu_{srv}ResponsePacket")
        res_decoder = getattr(res_conv, f"pdu_to_py_{srv}ResponsePacket")
    except AttributeError as e:
        raise RuntimeError(f"Missing converter functions for service '{srv}'") from e

    return ReqPacket, ResPacket, req_encoder, req_decoder, res_encoder, res_decoder


def make_protocol_client(*, pdu_manager: Any, service_name: str, client_name: str,
                         srv: str,
                         pkg: str = "hakoniwa_pdu.pdu_msgs.hako_srv_msgs",
                         ProtocolClientClass: Optional[Type[Any]] = None):
    """Create :class:`ProtocolClient` from a service name.

    Parameters
    ----------
    pdu_manager: Any
        Manager instance controlling PDU communication.
    service_name: str
        Name of the remote service (e.g. ``"Service/Add"``).
    client_name: str
        Name of this client instance.
    srv: str
        Simple service type name such as ``"AddTwoInts"``.
    pkg: str, optional
        Package prefix where generated PDU modules exist.
    ProtocolClientClass: Type, optional
        Custom ``ProtocolClient`` class to instantiate.
    """
    if ProtocolClientClass is None:
        from .protocol_client import (
            ProtocolClientBlocking,
            ProtocolClientImmediate,
        )  # type: ignore
        register_client = getattr(pdu_manager, "register_client", None)
        if asyncio.iscoroutinefunction(register_client):
            ProtocolClientClass = ProtocolClientBlocking
        else:
            ProtocolClientClass = ProtocolClientImmediate

    ReqPacket, ResPacket, req_encoder, req_decoder, res_encoder, res_decoder = _load_protocol_components(srv, pkg)

    return ProtocolClientClass(
        pdu_manager=pdu_manager,
        service_name=service_name,
        client_name=client_name,
        cls_req_packet=ReqPacket,
        req_encoder=req_encoder,
        req_decoder=req_decoder,
        cls_res_packet=ResPacket,
        res_encoder=res_encoder,
        res_decoder=res_decoder,
    )


def make_protocol_server(*, pdu_manager: Any, service_name: str, srv: str, max_clients: int,
                         pkg: str = "hakoniwa_pdu.pdu_msgs.hako_srv_msgs",
                         ProtocolServerClass: Optional[Type[Any]] = None):
    """Create :class:`ProtocolServer` from a service name."""
    if ProtocolServerClass is None:
        from .protocol_server import (
            ProtocolServerBlocking,
            ProtocolServerImmediate,
        )  # type: ignore
        start_rpc_service = getattr(pdu_manager, "start_rpc_service", None)
        if asyncio.iscoroutinefunction(start_rpc_service):
            ProtocolServerClass = ProtocolServerBlocking
        else:
            ProtocolServerClass = ProtocolServerImmediate

    ReqPacket, ResPacket, req_encoder, req_decoder, res_encoder, res_decoder = _load_protocol_components(srv, pkg)

    return ProtocolServerClass(
        pdu_manager=pdu_manager,
        service_name=service_name,
        max_clients=max_clients,
        cls_req_packet=ReqPacket,
        req_encoder=req_encoder,
        req_decoder=req_decoder,
        cls_res_packet=ResPacket,
        res_encoder=res_encoder,
        res_decoder=res_decoder,
    )


def make_protocol_clients(
    *,
    pdu_manager: Any,
    services: Sequence[Dict[str, Any]],
    pkg: str = "hakoniwa_pdu.pdu_msgs.hako_srv_msgs",
    ProtocolClientClass: Optional[Type[Any]] = None,
) -> Dict[str, Any]:
    """Create multiple :class:`ProtocolClient` instances.

    Parameters
    ----------
    pdu_manager: Any
        Manager instance controlling PDU communication.
    services: Sequence[Dict[str, Any]]
        Iterable of service specifications.  Each specification must contain
        ``service_name``, ``client_name`` and ``srv``.
    pkg: str, optional
        Package prefix where generated PDU modules exist.
    ProtocolClientClass: Type, optional
        Custom ``ProtocolClient`` class to instantiate.

    Returns
    -------
    Dict[str, Any]
        Mapping of service names to their corresponding ``ProtocolClient``
        instances.
    """
    clients: Dict[str, Any] = {}
    for spec in services:
        service_name = spec["service_name"]
        manager = spec.get("pdu_manager", pdu_manager)
        service_pkg = spec.get("pkg", pkg)
        clients[service_name] = make_protocol_client(
            pdu_manager=manager,
            service_name=service_name,
            client_name=spec["client_name"],
            srv=spec["srv"],
            pkg=service_pkg,
            ProtocolClientClass=ProtocolClientClass,
        )
    return clients


def make_protocol_servers(
    *,
    pdu_manager: Any,
    services: Sequence[Dict[str, Any]],
    pkg: str = "hakoniwa_pdu.pdu_msgs.hako_srv_msgs",
    ProtocolServerClass: Optional[Type[Any]] = None,
) -> Any:
    """Create a multi-service :class:`ProtocolServer` instance.

    Parameters
    ----------
    pdu_manager: Any
        Manager instance controlling PDU communication.
    services: Sequence[Dict[str, Any]]
        Iterable of service specifications.  Each specification must contain
        ``service_name``, ``srv`` and ``max_clients``.
    pkg: str, optional
        Package prefix where generated PDU modules exist.
    ProtocolServerClass: Type, optional
        Custom ``ProtocolServer`` class to instantiate.

    Returns
    -------
    Any
        A ``ProtocolServer`` instance capable of handling all specified
        services.
    """
    if not services:
        raise ValueError("No services specified")

    first = services[0]
    first_pkg = first.get("pkg", pkg)
    server = make_protocol_server(
        pdu_manager=pdu_manager,
        service_name=first["service_name"],
        srv=first["srv"],
        max_clients=first["max_clients"],
        pkg=first_pkg,
        ProtocolServerClass=ProtocolServerClass,
    )

    for spec in services[1:]:
        service_pkg = spec.get("pkg", pkg)
        ReqPacket, ResPacket, req_encoder, req_decoder, res_encoder, res_decoder = _load_protocol_components(
            spec["srv"], service_pkg
        )
        server.add_service(
            spec["service_name"],
            spec["max_clients"],
            ReqPacket,
            req_encoder,
            req_decoder,
            ResPacket,
            res_encoder,
            res_decoder,
        )
    return server
