#!/usr/bin/python
# -*- coding: utf-8 -*-
import asyncio
import sys
import hakopy
from typing import Any

# 新しいRPCコンポーネントをインポート
from hakoniwa_pdu.rpc.shm.shm_pdu_service_server_manager import ShmPduServiceServerManager
from hakoniwa_pdu.rpc.protocol_server import ProtocolServer

# PDUの型定義とエンコーダ/デコーダをインポート
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_AddTwoIntsRequest import AddTwoIntsRequest
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_AddTwoIntsResponse import AddTwoIntsResponse
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_AddTwoIntsRequestPacket import AddTwoIntsRequestPacket
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_pytype_AddTwoIntsResponsePacket import AddTwoIntsResponsePacket
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_AddTwoIntsRequestPacket import py_to_pdu_AddTwoIntsRequestPacket, pdu_to_py_AddTwoIntsRequestPacket
from hakoniwa_pdu.pdu_msgs.hako_srv_msgs.pdu_conv_AddTwoIntsResponsePacket import py_to_pdu_AddTwoIntsResponsePacket, pdu_to_py_AddTwoIntsResponsePacket

# --- サーバー設定 ---
ASSET_NAME = 'NewServer'
SERVICE_NAME = 'Service/Add'
SERVICE_CONFIG_PATH = './examples/service.json'
# HAKO_BINARY_PATH環境変数から取得するか、デフォルト値を設定
OFFSET_PATH = '/usr/local/hakoniwa/share/hakoniwa/offset'
DELTA_TIME_USEC = 1000 * 1000

# グローバル変数としてマネージャとプロトコルを保持
pdu_manager: ShmPduServiceServerManager = None
protocol_server: ProtocolServer = None

async def add_two_ints_handler(request: AddTwoIntsRequest) -> AddTwoIntsResponse:
    """
    リクエストを処理するビジネスロジック。
    受け取った2つの整数を足し算して返す。
    """
    print(f"Request data received: a={request.a}, b={request.b}")
    response = AddTwoIntsResponse()
    response.sum = request.a + request.b
    print(f"Calculated sum: {response.sum}")
    return response

def my_on_initialize(context):
    """
    Hakoniwaアセットの初期化コールバック
    """
    global pdu_manager, protocol_server
    print(f"Starting service: {SERVICE_NAME}")
    # サーバープロトコルを初期化
    protocol_server = ProtocolServer(
        service_name=SERVICE_NAME,
        max_clients=1,
        pdu_manager=pdu_manager,
        cls_req_packet=AddTwoIntsRequestPacket,  # リクエストPDUの型
        req_encoder=py_to_pdu_AddTwoIntsRequestPacket,  # リクエストのエンコーダ
        req_decoder=pdu_to_py_AddTwoIntsRequestPacket,  # リクエストのデコーダ
        cls_res_packet=AddTwoIntsResponsePacket,  # レスポンスPDUの型
        res_encoder=py_to_pdu_AddTwoIntsResponsePacket,  # レスポンスのエンコーダ
        res_decoder=pdu_to_py_AddTwoIntsResponsePacket  # レスポンスのデコーダ
    )
    # サービスを開始
    if not protocol_server.start_service_nowait():
        print("Failed to start service.")
        return 1

    print("Initialization complete.")
    return 0

def my_on_manual_timing_control(context):
    """
    Hakoniwaアセットのメインループコールバック
    """
    global protocol_server
    print("Server is running. Waiting for requests...")
    try:
        # サーバーのイベントループを開始
        protocol_server.serve_nowait(add_two_ints_handler)
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    finally:
        protocol_server.stop()
    return 0

def my_on_reset(context):
    return 0

# Hakoniwaへのコールバック関数を辞書として登録
my_callback = {
    'on_initialize': my_on_initialize,
    'on_simulation_step': None,
    'on_manual_timing_control': my_on_manual_timing_control,
    'on_reset': my_on_reset
}

def main():
    """
    メインの実行関数
    """
    global pdu_manager
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <pdu_config_path>")
        return 1
    
    pdu_config_path = sys.argv[1]

    # PDUサービスマネージャを初期化
    print("Initializing PDU Service Manager for SHM...")
    pdu_manager = ShmPduServiceServerManager(
        asset_name=ASSET_NAME,
        pdu_config_path=pdu_config_path,
        offset_path=OFFSET_PATH
    )

    # Conductorを開始
    hakopy.conductor_start(DELTA_TIME_USEC, DELTA_TIME_USEC)

    print(f"Registering asset: {ASSET_NAME}")
    # Hakoniwaにアセットを登録
    ret = hakopy.asset_register(ASSET_NAME, pdu_config_path, my_callback, DELTA_TIME_USEC, hakopy.HAKO_ASSET_MODEL_PLANT)
    if not ret:
        print(f"ERROR: hako_asset_register() failed.")
        hakopy.conductor_stop()
        return 1
    
    # サービスを初期化
    if pdu_manager.initialize_services(SERVICE_CONFIG_PATH, DELTA_TIME_USEC) < 0:
        print(f"ERROR: hako_asset_service_initialize() failed.")
        hakopy.conductor_stop()
        return 1


    # シミュレーションを開始
    hakopy.start()
    print("Simulation finished.")

    # Conductorを停止
    hakopy.conductor_stop()
    return 0

if __name__ == "__main__":
    sys.exit(main())
