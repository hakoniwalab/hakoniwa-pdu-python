"""Utility helpers to construct ProtocolClient/Server with minimal imports."""
from importlib import import_module
from typing import Any, Tuple, Type, Callable, Optional


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
        from .protocol_client import ProtocolClient as ProtocolClientClass  # type: ignore

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
        from .protocol_server import ProtocolServer as ProtocolServerClass  # type: ignore

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
