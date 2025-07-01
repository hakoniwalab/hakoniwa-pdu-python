from typing import Optional
import os
from hakoniwa_pdu.impl.communication_buffer import CommunicationBuffer
from hakoniwa_pdu.impl.icommunication_service import ICommunicationService
from hakoniwa_pdu.impl.data_packet import DataPacket
from hakoniwa_pdu.impl.pdu_channel_config import PduChannelConfig  # ← 追加
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

    def __init__(self):
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
        pdu_config = PduChannelConfig(config_path)

        # CommunicationBufferにPduChannelConfigを渡して初期化
        self.comm_buffer = CommunicationBuffer(pdu_config)
        self.comm_service = comm_service
        self.b_is_initialized = True
        hako_binary_path = os.getenv('HAKO_BINARY_PATH', '/usr/local/lib/hakoniwa/hako_binary/offset')
        self.pdu_convertor = PduConvertor(hako_binary_path, pdu_config)
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
        return await self.comm_service.send_data(robot_name, channel_id, pdu_raw_data)

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
        return (self.declare_pdu_for_read(robot_name, pdu_name) and
                self.declare_pdu_for_write(robot_name, pdu_name))

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

        magic_number = 0x52455044 if is_read else 0x57505044
        pdu_raw_data = bytearray(magic_number.to_bytes(4, byteorder='little'))
        return await self.comm_service.send_data(robot_name, channel_id, pdu_raw_data)

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