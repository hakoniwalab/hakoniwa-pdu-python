from typing import Optional
import os
import asyncio
from hakoniwa_pdu.impl.communication_buffer import CommunicationBuffer
from hakoniwa_pdu.impl.icommunication_service import ICommunicationService
from hakoniwa_pdu.impl.data_packet import (
    DataPacket,
    DECLARE_PDU_FOR_READ,
    DECLARE_PDU_FOR_WRITE,
    REQUEST_PDU_READ,
    PDU_DATA
)
from hakoniwa_pdu.impl.pdu_channel_config import PduChannelConfig
from hakoniwa_pdu.impl.pdu_convertor import PduConvertor
import importlib.resources

class PduManager:
    """
    PduManager is the core interface for PDU communication in the Hakoniwa simulation framework.

    Main Responsibilities:
    - Manage PDU channel declaration (for read, write, or both)
    - Start/stop the communication service (e.g., WebSocket)
    - Handle binary data transfer via buffer

    PDU data format:
    - Binary data is exchanged via shared buffer.
    - To convert between JSON and binary formats, use `self.pdu_convertor`, which is an instance of `PduConvertor`.

    Usage example:
        # Convert binary to JSON
        json_data = manager.pdu_convertor.convert_binary_to_json(robot_name, pdu_name, binary_data)

        # Convert JSON to binary
        binary_data = manager.pdu_convertor.convert_json_to_binary(robot_name, pdu_name, json_data)

    Related Components:
    - PduConvertor: Handles binary <-> JSON conversion.
    - PduChannelConfig: Parses and stores PDU channel configuration.
    - CommunicationBuffer: Shared buffer to hold binary PDU data.
    - ICommunicationService: Interface for the actual transport mechanism.

    Note:
    - Make sure to call `initialize()` before using any other methods.
    - The environment variable `HAKO_BINARY_PATH` can be used to override the default offset file location.
    """

    def __init__(self, *, wire_version: str = "v1"):
        """
        Initialize internal states of PduManager.

        Attributes:
            comm_buffer (Optional[CommunicationBuffer]): Internal buffer for PDU data.
            comm_service (Optional[ICommunicationService]): Interface for actual communication.
            b_is_initialized (bool): Flag indicating whether the manager has been initialized.
        """        
        self.comm_buffer: Optional[CommunicationBuffer] = None
        self.comm_service: Optional[ICommunicationService] = None
        self.b_is_initialized = False
        self.b_last_known_service_state = False
        self.wire_version = wire_version  # "v1" or "v2"
        print(f"[INFO] PduManager created with wire version: {self.wire_version}")

    def get_default_offset_path(self) -> str:
        # インストール済パッケージ内の offset ディレクトリパスを取得
        return str(importlib.resources.files("hakoniwa_pdu.resources.offset"))

    def initialize(self, config_path: str, comm_service: ICommunicationService):
        """
        Initialize the PDU manager with a configuration file and communication service.

        Args:
            config_path (str): Path to the JSON file defining the PDU channel configuration.
            comm_service (ICommunicationService): An instance of a communication service (e.g., WebSocket).

        Raises:
            ValueError: If the provided communication service is None.

        Notes:
            - Initializes the internal communication buffer using the configuration.
            - Initializes the PDU convertor using environment variable HAKO_BINARY_PATH,
              or falls back to the default path /usr/local/lib/hakoniwa/hako_binary/offset.
        """        
        if comm_service is None:
            raise ValueError("CommService is None")

        # JSONファイルからPduChannelConfigを生成
        self.pdu_config = PduChannelConfig(config_path)
        comm_service.set_channel_config(self.pdu_config)

        # CommunicationBufferにPduChannelConfigを渡して初期化
        self.comm_buffer = CommunicationBuffer(self.pdu_config)
        self.comm_service = comm_service
        self.b_is_initialized = True
        hako_binary_path = os.getenv('HAKO_BINARY_PATH', '/usr/local/lib/hakoniwa/hako_binary/offset')
        self.pdu_convertor = PduConvertor(hako_binary_path, self.pdu_config)
        print("[INFO] PduManager initialized")

    def is_service_enabled(self) -> bool:
        """
        Check if the communication service is currently running.

        Returns:
            bool: True if the service is active, False otherwise.

        Notes:
            - Returns False if the PduManager is not initialized or if no communication service is set.
            - Updates the internal state `b_last_known_service_state`.
        """        
        if not self.b_is_initialized or self.comm_service is None:
            print("[ERROR] PduManager is not initialized or CommService is None")
            return False
        current_state = self.comm_service.is_service_enabled()
        self.b_last_known_service_state = current_state
        return current_state

    async def start_service(self, uri: str = "") -> bool:
        """
        Start the communication service using the provided URI.

        Args:
            uri (str, optional): URI of the server to connect to (e.g., WebSocket URI). Defaults to "".

        Returns:
            bool: True if the service was successfully started, False otherwise.

        Notes:
            - This method is asynchronous and must be awaited.
            - Will not attempt to start if already running.
        """
        if not self.b_is_initialized or self.comm_service is None:
            print("[ERROR] PduManager is not initialized or CommService is None")
            return False
        if self.comm_service.is_service_enabled():
            print("[INFO] Service is already running")
            return False
        result = await self.comm_service.start_service(self.comm_buffer, uri)
        self.b_last_known_service_state = result
        if result:
            print(f"[INFO] Service started successfully at {uri}")
        else:
            print("[ERROR] Failed to start service")
        return result

    async def stop_service(self) -> bool:
        """
        Stop the currently running communication service.

        Returns:
            bool: True if the service was successfully stopped, False otherwise.

        Notes:
            - This method is asynchronous and must be awaited.
        """        
        if not self.b_is_initialized or self.comm_service is None:
            return False
        result = await self.comm_service.stop_service()
        self.b_last_known_service_state = not result
        return result

    def start_service_nowait(self, uri: str = "") -> bool:
        """
        Start the communication service without waiting for it to complete.

        Args:
            uri (str, optional): URI of the server to connect to (e.g., WebSocket URI). Defaults to "".

        Returns:
            bool: True if the service was successfully started, False otherwise.
        """        
        if not self.b_is_initialized or self.comm_service is None:
            print("[ERROR] PduManager is not initialized or CommService is None")
            return False
        result = self.comm_service.start_service_nowait(self.comm_buffer, uri)
        self.b_last_known_service_state = result
        return result

    def stop_service_nowait(self) -> bool:
        """
        Stop the currently running communication service without waiting for it to complete.

        Returns:
            bool: True if the service was successfully stopped, False otherwise.
        """        
        if not self.b_is_initialized or self.comm_service is None:
            return False
        result = self.comm_service.stop_service_nowait()
        self.b_last_known_service_state = not result
        return result
    
    def run_nowait(self) -> bool:
        """
        Run the communication service without waiting for it to complete.

        Returns:
            bool: True if the service was successfully started, False otherwise.
        """        
        if not self.b_is_initialized or self.comm_service is None:
            print("[ERROR] PduManager is not initialized or CommService is None")
            return False
        result = self.comm_service.run_nowait()
        self.b_last_known_service_state = result
        return result

    def get_pdu_channel_id(self, robot_name: str, pdu_name: str) -> int:
        """
        Get the internal channel ID for a specific robot and PDU name.

        Args:
            robot_name (str): The name of the robot.
            pdu_name (str): The name of the PDU.

        Returns:
            int: The channel ID assigned to the specified PDU, or -1 if not found.
        """        
        return self.comm_buffer.get_pdu_channel_id(robot_name, pdu_name)

    def get_pdu_size(self, robot_name: str, pdu_name: str) -> int:
        """
        Get the byte size of the specified PDU.

        Args:
            robot_name (str): The name of the robot.
            pdu_name (str): The name of the PDU.

        Returns:
            int: Size in bytes of the PDU, or -1 if undefined.
        """
        return self.comm_buffer.get_pdu_size(robot_name, pdu_name)

    async def flush_pdu_raw_data(self, robot_name: str, pdu_name: str, pdu_raw_data: bytearray) -> bool:
        """
        Send raw binary PDU data to the communication service.

        Args:
            robot_name (str): The name of the robot.
            pdu_name (str): The name of the PDU.
            pdu_raw_data (bytearray): Raw binary data to send.

        Returns:
            bool: True if the data was successfully sent, False otherwise.

        Notes:
            - This method is asynchronous and must be awaited.
            - PDU must have been declared before sending.
        """
        if not self.is_service_enabled() or self.comm_service is None:
            return False
        channel_id = self.comm_buffer.get_pdu_channel_id(robot_name, pdu_name)
        if channel_id < 0:
            return False
        
        if self.wire_version == "v1":
            return await self.comm_service.send_data(robot_name, channel_id, pdu_raw_data)
        else:
            raw_data = self._build_binary(PDU_DATA, robot_name, channel_id, pdu_raw_data)
            return await self.comm_service.send_binary(raw_data)

    def flush_pdu_raw_data_nowait(self, robot_name: str, pdu_name: str, pdu_raw_data: bytearray) -> bool:
        """
        Send raw binary PDU data to the communication service without waiting.

        Args:
            robot_name (str): The name of the robot.
            pdu_name (str): The name of the PDU.
            pdu_raw_data (bytearray): Raw binary data to send.

        Returns:
            bool: True if the data was successfully sent, False otherwise.

        Notes:
            - PDU must have been declared before sending.
        """        
        if not self.is_service_enabled() or self.comm_service is None:
            return False
        channel_id = self.comm_buffer.get_pdu_channel_id(robot_name, pdu_name)
        if channel_id < 0:
            return False
        
        if self.wire_version == "v1":
            return self.comm_service.send_data_nowait(robot_name, channel_id, pdu_raw_data)
        else:
            raise NotImplementedError("Wire version not supported")

    def read_pdu_raw_data(self, robot_name: str, pdu_name: str) -> Optional[bytearray]:
        """
        Read the latest raw binary data for the specified PDU.

        Args:
            robot_name (str): The name of the robot.
            pdu_name (str): The name of the PDU.

        Returns:
            Optional[bytearray]: Raw binary data, or None if not available.
        """        
        if not self.is_service_enabled():
            return None
        return self.comm_buffer.get_buffer(robot_name, pdu_name)

    async def request_pdu_read(self, robot_name: str, pdu_name: str, timeout: float = 1.0) -> Optional[bytearray]:
        """Request the latest PDU data from the server and wait for the response.

        Args:
            robot_name (str): Target robot name.
            pdu_name (str): PDU name to request.
            timeout (float, optional): Seconds to wait for the response. Defaults to 1.0.

        Returns:
            Optional[bytearray]: Received PDU data or ``None`` if no data was received within the timeout.
        """
        if not self.is_service_enabled() or self.comm_service is None:
            return None

        channel_id = self.comm_buffer.get_pdu_channel_id(robot_name, pdu_name)
        if channel_id < 0:
            return None

        if self.wire_version == "v1":
            # send request magic number
            req_data = bytearray(REQUEST_PDU_READ.to_bytes(4, byteorder="little"))
            if not await self.comm_service.send_data(robot_name, channel_id, req_data):
                return None
        else:
            raw_data = self._build_binary(REQUEST_PDU_READ, robot_name, channel_id, None)
            if not await self.comm_service.send_binary(raw_data):
                return None

        # wait for buffer to be filled
        loop = asyncio.get_event_loop()
        end_time = loop.time() + timeout
        while loop.time() < end_time:
            if self.comm_buffer.contains_buffer(robot_name, pdu_name):
                return self.comm_buffer.get_buffer(robot_name, pdu_name)
            await asyncio.sleep(0.05)
        return None

    async def declare_pdu_for_read(self, robot_name: str, pdu_name: str) -> bool:
        """
        Declare that you want to read data from a specified PDU.

        Args:
            robot_name (str): The name of the robot.
            pdu_name (str): The name of the PDU to read from.

        Returns:
            bool: True if the declaration was successful, False otherwise.
        """        
        return await self._declare_pdu(robot_name, pdu_name, is_read=True)

    async def declare_pdu_for_write(self, robot_name: str, pdu_name: str) -> bool:
        """
        Declare that you want to write data to a specified PDU.

        Args:
            robot_name (str): The name of the robot.
            pdu_name (str): The name of the PDU to write to.

        Returns:
            bool: True if the declaration was successful, False otherwise.
        """
        return await self._declare_pdu(robot_name, pdu_name, is_read=False)

    async def declare_pdu_for_readwrite(self, robot_name: str, pdu_name: str) -> bool:
        """
        Declare that you want to both read and write to a specified PDU.

        Args:
            robot_name (str): The name of the robot.
            pdu_name (str): The name of the PDU.

        Returns:
            bool: True if both read and write declarations were successful.
        """        
        read_result = await self.declare_pdu_for_read(robot_name, pdu_name)
        write_result = await self.declare_pdu_for_write(robot_name, pdu_name)
        return read_result and write_result

    async def _declare_pdu(self, robot_name: str, pdu_name: str, is_read: bool) -> bool:
        """
        Internal method to declare a PDU for reading or writing by sending a magic number.

        Args:
            robot_name (str): The name of the robot.
            pdu_name (str): The name of the PDU.
            is_read (bool): If True, declare for reading; otherwise, for writing.

        Returns:
            bool: True if the declaration message was successfully sent.
        """        
        if not self.is_service_enabled():
            print("[WARN] Service is not enabled")
            return False

        channel_id = self.comm_buffer.get_pdu_channel_id(robot_name, pdu_name)
        if channel_id < 0:
            print(f"[WARN] Unknown PDU: {robot_name}/{pdu_name}")
            return False
        
        if self.wire_version == "v1":
            raise NotImplementedError("register rpc service for v1 is not implemented")
        else:
            meta_request_type = DECLARE_PDU_FOR_READ if is_read else DECLARE_PDU_FOR_WRITE
            raw_data = self._build_binary(meta_request_type, robot_name, channel_id, None)
            return await self.comm_service.send_binary(raw_data)

    def log_current_state(self):
        """
        Print the current internal state of the PduManager.

        This method is primarily for debugging and logging purposes.
        """        
        print("PduManager State:")
        print(f"  - Initialized: {self.b_is_initialized}")
        print(f"  - CommBuffer Valid: {self.comm_buffer is not None}")
        print(f"  - CommService Valid: {self.comm_service is not None}")
        print(f"  - Last Known Service State: {self.b_last_known_service_state}")


    def _build_binary(self, meta_request_type: int, robot_name: str, channel_id: int, pdu_data: bytearray) -> bytearray:
        packet = DataPacket(
            robot_name=robot_name,
            channel_id=channel_id,
            body_data=pdu_data
        )
        return packet.encode(version = "v2", meta_request_type=meta_request_type)