# hakoniwa-pdu-python

箱庭シミュレータ用の Python PDU 通信ライブラリです。WebSocket 経由で箱庭と通信し、PDUバイナリの送受信やJSON変換を簡単に扱えます。

---

## 📦 インストール

```bash
pip install hakoniwa-pdu
````

バージョン確認：

```bash
pip show hakoniwa-pdu
```

---

## 🔧 環境変数

PDU変換に使用する `.offset` ファイルのディレクトリを指定できます。

```bash
export HAKO_BINARY_PATH=/your/path/to/offset
```

省略時は以下が使用されます：

```
/usr/local/lib/hakoniwa/hako_binary/offset
```

---

## 🚀 使用例（Sample）

### テスト用スクリプトで PDU 読み取り確認

以下のサンプルは、ドローンから `pos` PDU を受信し、JSON形式に変換して出力するものです。

`tests/sample.py`:

```python
import argparse
import asyncio
import sys
from hakoniwa_pdu.pdu_manager import PduManager
from hakoniwa_pdu.impl.websocket_communication_service import WebSocketCommunicationService

async def main():
    parser = argparse.ArgumentParser(description="Sample PDU Manager usage")
    parser.add_argument("--config", required=True, help="Path to PDU channel config JSON")
    parser.add_argument("--uri", required=True, help="WebSocket server URI")
    parser.add_argument("--read-time", type=int, default=5, help="Seconds to wait for PDU read")
    args = parser.parse_args()

    service = WebSocketCommunicationService()
    manager = PduManager()
    manager.initialize(config_path=args.config, comm_service=service)

    if not await manager.start_service(args.uri):
        print("[ERROR] Failed to start communication service.")
        sys.exit(1)

    robot_name = 'Drone'
    pdu_name = 'pos'

    if not await manager.declare_pdu_for_read(robot_name, pdu_name):
        print(f"[FAIL] Could not declare PDU for READ: {robot_name}/{pdu_name}")
        await manager.stop_service()
        sys.exit(1)

    print(f"[OK] Declared PDU for READ: {robot_name}/{pdu_name}")
    await asyncio.sleep(args.read_time)

    pdu_data = manager.read_pdu_raw_data(robot_name, pdu_name)
    if pdu_data:
        print(f"[RECV] Raw PDU Data: {list(pdu_data)}")
        try:
            json_data = manager.pdu_convertor.convert_binary_to_json(robot_name, pdu_name, pdu_data)
            print(f"[DEBUG] JSON: {json_data}")
        except Exception as e:
            print(f"[ERROR] Conversion failed: {e}")
    else:
        print("[INFO] No data received.")

    await manager.stop_service()
    print("[INFO] Communication stopped.")

if __name__ == "__main__":
    asyncio.run(main())
```

### 実行コマンド例

```bash
python tests/sample.py \
  --config ./config/pdudef/webavatar.json \
  --uri ws://localhost:8765
```

---

## 📁 パッケージ構成（主要ファイル）

```
hakoniwa_pdu/
├── pdu_manager.py                  # PDUのライフサイクル管理
├── impl/
│   ├── websocket_communication_service.py  # WebSocket実装
│   ├── pdu_convertor.py            # バイナリ⇔JSON変換
│   ├── hako_binary/
│   │   └── *.py (offset読み取りやバイナリ構造)
├── resources/
│   └── offset/                    # 各種 .offset ファイル
```

---

## 🔗 リンク

* 📘 GitHub: [https://github.com/hakoniwalab/hakoniwa-pdu-python](https://github.com/hakoniwalab/hakoniwa-pdu-python)
* 🌐 箱庭ラボ: [https://hakoniwa-lab.net](https://hakoniwa-lab.net)

---

## 📜 ライセンス

MIT License - see [LICENSE](./LICENSE) ファイルをご覧ください。

```
