# 非同期共有 RPC ランタイム設計

## 1. 目的

この文書は、`hakoniwa-pdu-python` に対して追加する新しい非同期 RPC クライアント設計を定義する。

目的は、`100-512+` 機体のような大規模 SHM RPC fan-out を、1つの Python プロセスから効率よく扱えるようにすることにある。

加えて、将来的な Hakoniwa asset 化および分散シミュレーション連携を見据え、
時刻進行を runtime 内部の `sleep` に依存させない構造を目指す。

今回の設計は追加実装を前提とする。

- 既存クラスは残す
- 既存の同期動作は残す
- 新実装は別クラスとして追加する
- 評価中はローカルの `PYTHONPATH` で `work/hakoniwa-pdu-python` を優先利用する

Hakoniwa の初期化 (`hakopy.init_for_external()` など) は runtime の責務に含めない。
この初期化は呼び出し元が実行モードに応じて選択する。

- external 利用: 呼び出し元が `hakopy.init_for_external()` を実行する
- asset 利用: 呼び出し元が asset 向け初期化を実行する

新設計の runtime は、初期化済みの Hakoniwa 実行環境の上で動作する transport/runtime 層として扱う。

## 2. 対象範囲

対象:

- SHM RPC クライアント経路
- クライアント側の非同期 request 実行
- Python プロセス内共有ランタイム
- 既存 `ProtocolClientImmediate` との共存方針
- Hakoniwa asset 化を見据えた manual polling モード

対象外:

- サーバー側の全面再設計
- remote/WebSocket RPC の再設計
- 第1段階での既存クラス置換
- 既存 public API の削除

## 3. 現状構造

現在のクライアント側レイヤは以下である。

1. `HakoniwaRpcDroneClient`
2. `ProtocolClientImmediate`
3. `ShmPduServiceClientManager`
4. `hakopy`

現状の呼び出し経路:

1. `HakoniwaRpcDroneClient._call()` が protocol client を生成または再利用する
2. `ProtocolClientImmediate.call()` が request packet を生成して送信する
3. `ProtocolClientImmediate._wait_response()` が response/timeout/cancel を待つ
4. `ShmPduServiceClientManager` が `hakopy.asset_service_client_*` を呼ぶ

関連ファイル:

- `src/hakoniwa_pdu/rpc/protocol_client.py`
- `src/hakoniwa_pdu/rpc/shm/shm_pdu_service_client_manager.py`
- `src/hakoniwa_pdu/rpc/ipdu_service_manager.py`
- ドローン側利用例: `drone_api/external_rpc/hakosim_rpc.py`

## 4. 現状動作と問題

現在の external RPC 利用では、機体ごとに `HakoniwaRpcDroneClient` が1つ作られる。
さらに、その各 client が初回利用時に独自の `ShmPduServiceClientManager` を生成している。

その結果:

- 1つの Python プロセス内で `ShmPduServiceClientManager` が機体数分作られる
- 同一プロセス内で `initialize_services()` が何度も実行される
- Hakoniwa core への service registration 負荷が不要に高くなる
- オブジェクト数、初期化時間、SHM 準備コストが機体数に比例して増大する

これは transport の要件ではない。
現在の同期 RPC クライアント構造に起因する実装上の制約である。

追加で、shared runtime 化の初期段階では `register_client()` ごとに以下を毎回実行していた。

- `offset_map.create_offmap(...)`
- `ServiceConfig(...)`
- `load_shared_memory_for_safe(...)`
- `service_config.append_pdu_def(...)`
- `pdu_config.update_pdudef(...)`

前半 3 つは runtime 初期化時に 1 回でよい固定処理であり、後半 2 つも service 定義が固定である以上は毎回不要である。
実測では、この「PDU 定義の毎回再生成」が Python 側 registration コストの主因だった。

## 5. なぜ現状では共有しにくかったか

問題は単に `ShmPduServiceClientManager` が「同期型」であることだけではない。
より本質的には、クライアントスタック全体が以下を前提にしていることである。

- request を1つ送る
- その呼び出し元がその場で待つ
- response polling もその呼び出し元が担当する
- request/response の所有権が protocol client インスタンスに閉じている

現在、以下の状態が protocol client 側に局所化されている。

- `service_name`
- `client_name`
- `client_id`
- serializer / deserializer
- last request tracking

そのため、1つの shared manager の上で多数の outstanding request を安全に multiplex するための中央 dispatcher が存在しない。

さらに現状の waiting は call path の中で完結しており、呼び出し元がシミュレーション時刻に合わせて
進行制御することが難しい。
この点は、分散シミュレーション時に別ノードの Python プログラムを時刻同期させたい要件と相性が悪い。

加えて、現行 `ShmPduServiceClientManager.poll_response()` は内部で `sleep(delta_time)` を行う。
この挙動は external の同期呼び出しには都合がよいが、manual polling を正規形とする今回の設計とは整合しない。
そのため既存 manager に `poll_response_nowait()` を追加し、`async_shared` はそれを使う。

## 6. 設計目標

新設計で満たしたい条件は以下である。

- 1つの Python プロセスに対して 1つの SHM RPC ランタイム
- プロセス内で 1本の shared response polling loop
- その上に複数の論理 RPC client handle
- 非同期 request submission に対して lightweight な future 風オブジェクトを返す
- 既存同期 API は、新しい非同期経路の上に互換層として残せる
- request 発行は immediate-return を基本とする
- 時刻進行は呼び出し元が制御できる
- runtime 内部の `sleep` は必須要件にしない
- Hakoniwa 初期化方式は runtime に埋め込まない

## 7. 提案設計

### 7.1 レイヤ分離

新構造では、物理ランタイムと論理クライアントを分離する。

1. `SharedRpcRuntime`
   - `ShmPduServiceClientManager` を1つ保持する
   - polling loop を1つ保持する
   - pending request table を保持する
   - registration cache を保持する

2. `AsyncRpcClientHandle`
   - 1つの `(service_name, client_name, serializer set)` に束縛される
   - 軽量な論理 endpoint
   - shared runtime 上で1回だけ register する
   - `call_async()` を提供する

3. `RpcCallFuture`
   - `call_async()` が返す完了待ちオブジェクト
   - `done()`, `wait()`, `result()`, `exception()` を提供する

4. optional background poller
   - convenience 用の補助機能
   - ただし runtime の本質責務とは分離する

### 7.2 所有ルール

所有ルールは以下とする。

- 1 Python process
- 1 `SharedRpcRuntime`
- 多数の `AsyncRpcClientHandle`
- 多数の in-flight `RpcCallFuture`

ここが最重要の設計変更である。
共有すべきなのは runtime であり、現行の `ProtocolClientImmediate` オブジェクトそのものではない。

## 8. 提案 API

最小の新規 API 形は以下である。

```python
runtime = SharedRpcRuntime(
    asset_name="DroneExternalClient",
    pdu_config_path="...",
    service_config_path="...",
    offset_path="...",
)

runtime.initialize()

client = AsyncRpcClientHandle(
    runtime=runtime,
    service_name="DroneService/DroneGoTo/Drone-1",
    client_name="DroneGoToClient_Drone_1",
    cls_req_packet=...,
    req_encoder=...,
    req_decoder=...,
    cls_res_packet=...,
    res_encoder=...,
    res_decoder=...,
)

client.register()
future = client.call_async(request_data, timeout_msec=30000, poll_interval=0.01)
response = future.result(timeout=60.0)
```

同期互換ラッパは任意で以下のように提供できる。

```python
response = client.call(request_data, timeout_msec=30000, poll_interval=0.01)
```

この `call()` は内部的に

- `future = call_async(...)`
- `return future.result(...)`

として実装する。

## 8.1 実行モード

runtime は以下の2モードを想定する。

### manual mode

- `call_async()` は request を送って即 return する
- response/event の進行は呼び出し元が `poll_once()` などで明示的に駆動する
- runtime は内部で `sleep` しない
- `async_shared` は manager の `poll_response_nowait()` を使う
- Hakoniwa asset 化、時刻同期、分散シミュレーション向けの正規形

### background mode

- runtime が内部 thread で poll を回す
- external 実験や簡易利用の便宜のための補助機能
- ただし本質設計は manual mode を優先する

この設計により、

- external 利用では background mode
- asset 利用では manual mode

という使い分けができる。

## 9. request ライフサイクル

### 9.1 送信

`AsyncRpcClientHandle.call_async()` は以下を行う。

1. request packet を生成する
2. request packet に入る実 request_id を確定する
3. shared manager 経由で request を送信する
4. `RpcCallFuture` を生成する
5. runtime の pending table に登録する
6. 即時 return する

第1段階では、1つの registered client に対する in-flight request は 1件に制限する。
これは現行 SHM RPC API が client 単位の同期呼び出しを前提としているためである。
大規模 fan-out は、多数の client を同時に持つことで実現する。

### 9.2 完了

runtime の polling loop は以下を行う。

1. 登録済み client を poll する
2. response / timeout / cancel event を検出する
3. 必要に応じて response packet を取得する
4. response を decode する
5. 対応する `RpcCallFuture` を resolve する
6. pending entry を削除する

manual mode では、この処理は呼び出し元による `poll_once()` 呼び出しで進行する。
background mode では、内部 thread が同等処理を繰り返す。

## 10. 実装メモ: registration の固定処理キャッシュ

`async_shared` 実装では、registration 時の固定処理を以下のように整理する。

### 10.1 runtime 初期化時に 1 回だけ行うもの

- `offset_map.create_offmap(...)`
- `ServiceConfig(...)`
- `load_shared_memory_for_safe(...)`
- `hakopy.service_initialize(...)`
- `prepare_service_pdudef_once()`

### 10.2 client registration ごとに行うもの

- `hakopy.asset_service_client_create(...)`
- `hakopy.asset_service_get_channel_id(...)`
- client context の生成

### 10.3 `prepare_service_pdudef_once()` の考え方

service 定義ファイルは runtime 中に変化しない。
そのため、

- `service_config.append_pdu_def(...)`
- `pdu_config.update_pdudef(...)`

は runtime あたり 1 回で十分である。

これを `register_client()` ごとに毎回実行すると、100 機体以上では `prepare_basic_services` が支配的になる。
実測では、100 機体・4 service の準備時間が以下のように改善した。

- 変更前: `prepare_basic_services ≈ 3.57 sec`
- 変更後: `prepare_basic_services ≈ 0.06 sec`

したがって、`async_shared` では「service 定義は固定」「client registration は service handle 作成のみ」という役割分離を採用する。

## 11. profiling 方針

切り分けのため、以下の profiling を env で有効化できるようにしている。

- `HAKO_RPC_PROFILE_PREPARE=1`
  - Python 側 `async_shared` registration path の usec 計測
- `HAKO_PROFILE_SERVICE_CLIENT=1`
  - core 側 service client registration の usec 計測

通常運用では無効のままとする。

timeout / cancel の場合は response body を持たないため、
runtime は client 単位で保持している pending request の状態を遷移させながら処理する。

### 9.3 timeout / cancel の状態遷移

第1段階では、pending request ごとに runtime 内部状態を持つ。

- `DOING`
- `CANCELING`
- `DONE`
- `ERROR`

timeout 時のポリシーは以下とする。

1. `DOING` 中に timeout event を検知する
2. runtime が `cancel_request(client_id)` を発行する
3. pending state を `CANCELING` に遷移させる
4. その場では future を完了させない
5. 以後の `poll_once()` で `CANCEL_DONE` を待つ
6. `CANCEL_DONE` を受けた時点で、future を `TimeoutError` で失敗完了する

このポリシーにより、呼び出し元は future 完了を待つだけで
「request が完全に片付いた後」に retry を開始できる。

`CANCELING` 中は同一 client に対する新しい request を reject する。
これにより、未片付けの request と次の retry が混在することを防ぐ。

## 10. 相関キー

pending request を識別するキーは安定している必要がある。

採用方針:

- `(service_id, client_id, request_id)`

理由:

- `client_id` は global ではなく、service 配下の client slot として扱われる
- 既存 SHM API でも channel 解決は `asset_service_get_channel_id(service_id, client_id)` で行われる
- `hakopy.asset_service_client_create(...)` の戻り handle から `service_id` と `client_id` の両方を取得できる
- `request_id` は同一 client 上の複数 request を識別するために必要である
- 相関に使う `request_id` は、runtime 内部の仮採番ではなく、実際に送信した request packet header の値を使う

したがって、新設計では `(client_id, request_id)` のみを相関キーにしてはならない。
少なくとも `service_id` を含める。

実装上は、register 済み client ごとに以下の情報を保持する `RegisteredClientContext` を持つ。

- `service_name`
- `client_name`
- `service_id`
- `client_id`
- `handle`

runtime の pending table は、この `RegisteredClientContext` を基点にして
`(service_id, client_id, request_id)` をキーとして管理する。

加えて、runtime 内部では `PendingRequest` を保持する。
`PendingRequest` は少なくとも以下を持つ。

- `future`
- `service_id`
- `client_id`
- `request_id`
- `state`
- `cancel_reason`

## 11. polling モデル

第1段階の polling モデル:

- runtime thread は1本
- polling loop も1本
- response dispatch は中央集約

これにより挙動が決定的になり、デバッグしやすくなる。

その上位では、必要に応じて

- batched submission
- thread pool による request 発行

を追加できるが、response dispatch は中央集約のままとする。

重要:

- polling loop の本質は `poll_once()` の繰り返しである
- `sleep` は polling の本質ではなく、background mode の補助実装に過ぎない
- 分散シミュレーションや asset 化では `poll_once()` を simulation step に同期して呼ぶ

## 12. 並行実行モデル

runtime がサポートすべきもの:

- 多数の outstanding request
- 複数の logical client
- 1本の shared polling thread

ただし phase 1 では thread は optional とし、manual mode を第一級に扱う。

必要な thread safety:

- registration cache の保護
- pending request table の保護
- future resolve の冪等性保証

上位層は以下を自由に選択できる。

- 単一スレッド orchestration
- batched fan-out
- thread pool based submission

ただし runtime 自体は「機体数分の thread」を要求しない。

さらに将来の拡張として、runtime 構成に以下を持てるようにしてよい。

- `poller_count`
- `dispatch_workers`
- `poll_interval_sec`

ただし第1段階では `poller_count=1` を前提にする。

## 13. 互換性方針

第1段階では既存利用者を壊さないことを優先する。

ルール:

- `ProtocolClientImmediate` は変更しない
- 既存経路の `ShmPduServiceClientManager` も変更しない
- 新しいクラスを追加する
- 非同期経路が安定するまで既存 API の自動移行はしない

また、background polling を既定にせず、manual polling を正規形として設計する。

第1段階で追加する想定クラス:

- `rpc/async_shared/shared_rpc_runtime.py`
- `rpc/async_shared/async_rpc_client.py`
- `rpc/async_shared/rpc_call_future.py`

想定補助 API:

- `poll_once()`
- `poll_until_idle()`
- `start_background_polling()`
- `stop_background_polling()`

## 14. ローカル評価方針

評価時は installed package ではなく、ローカル worktree を使う。

方針:

- 改造対象は `work/hakoniwa-pdu-python`
- `PYTHONPATH` を `work/hakoniwa-pdu-python/src` に向ける
- installed `hakoniwa-pdu` は評価対象に使わない

これにより、安定版環境と試験実装を分離できる。

## 15. 移行ステップ

### Phase 1

- 現状構造を文書化する
- 新 runtime / future / client class を追加する
- 既存同期クライアント経路は変更しない

### Phase 2

- `hakoniwa-drone-pro` 側に試験用 integration path を追加する
- `HakoniwaRpcDroneClient` 相当ラッパへ shared runtime 注入を試す
- 初期化コストと大規模 fleet 時の挙動を比較する

### Phase 3

- 非同期経路上に同期ラッパを載せる
- external RPC 側の移行対象を判断する

## 16. 期待効果

- `initialize_services()` を「機体ごと」ではなく「プロセスごと1回」にできる
- 起動時の Hakoniwa core 負荷を下げられる
- SHM manager オブジェクト数を削減できる
- service registration のオーバーヘッドを削減できる
- batching と timeout 制御を上位で明確に扱える
- より大きい fleet への拡張余地ができる

## 17. 第1段階の非目標

- 既存同期 public API の置換
- 全サンプルの自動移行
- サーバー側の全面再設計
- WebSocket transport の統一設計

## 18. 未決事項

- runtime registration は eager に行うか lazy に行うか
- polling loop は常時稼働か、in-flight request 発生時のみ起動か
- serializer state を runtime 側と client handle 側のどちらにどこまで持たせるか
- `hakopy.asset_service_client_poll()` の thread safety をどの段階で検証するか

## 19. 設計判断の要約

今回の最重要判断は以下である。

- 共有すべきなのは runtime
- 現行の巨大な同期 client object ではない

つまり:

- shared manager は1つ
- shared poller も1つ
- lightweight な logical client handle は複数
- request 送信は非同期
- 完了待ちは explicit future object
- 時刻進行は runtime ではなく呼び出し元が制御する

この形であれば、既存互換を維持しながら、スケール時の問題を正しいレイヤで解消できる。
