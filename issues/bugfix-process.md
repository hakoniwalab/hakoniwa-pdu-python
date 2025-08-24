# 段階的移行プラン（破壊最小）

## フェーズ0：足場固め（現状維持）

* 現状の単一クライアント実装を**そのまま**動かす回帰テストを用意

  * 接続/切断、送受信、RPC往復、タイムアウト/キャンセル
* 目標：以降の変更は**このテストが緑**のまま進むこと

## フェーズ1：共通クラスに「役割フラグ」を導入（機能は不変）

* `WsEndpoint(role: SERVER|CLIENT)` を追加（内部的に今の実装を包む）
* 新API：`await send(data, *, to=None)`

  * `CLIENT`：`to`禁止。内部は従来の `self.websocket.send` を呼ぶ
  * `SERVER`：`to`必須。内部は**現在の self.websocket に送る**（まだ単一接続）
* 互換：既存の `send()`／`send_to()` があれば**デプリケート薄ラッパ**で新APIに委譲
* 受け入れ基準：既存テスト緑（挙動変化なし）

## フェーズ2：サーバ側だけ内部構造を多接続化（ただし既定は1接続）

* 内部を `clients: dict[client_id, websocket]` に変更

  * ただし**feature flag**（例：`multi_client_enabled=False`）でデフォルトは従来どおり「同時1接続相当」
* `send(data, to=client_id)` は `clients[to]` へ送る実装に差し替え

  * 同時送信衝突回避：client単位 `asyncio.Lock()` を導入
* `broadcast()` をサーバ専用メソッドとして追加（まだ使わない）
* 受け入れ基準：flag=OFF で既存テスト緑

## フェーズ3：client\_id の払い出し＆ハンドラ拡張（上位互換）

* 接続時に `client_id` 採番（`ws000001` 形式など）
* コールバックを二系統用意（**互換優先**）

  * 旧：`on_message(data)`（既存そのまま）
  * 新：`on_message_with_client(client_id, data)`（あればこちらを優先呼び出し）
* 切断通知も同様に `on_disconnect(client_id)` を**追加**（旧APIがあれば従来挙動も維持）
* 受け入れ基準：旧コールバックのみ登録時に挙動不変

## フェーズ4：Protocol/RPC層のマッピング導入（データ面は不変）

* **PDU配信**：`subscriptions[(robot, topic)] -> set[client_id]` を追加

  * `DECLARE_FOR_PDU_READ`／`UNDECLARE` を処理
  * **CommunicationBufferはこれまで通り**（robot×topicのみ、client\_idは載せない）
  * emit時に `multicast(subscribers)` で**宣言者にのみ**送信
* **RPC**：`route[(service_name, request_id)] -> client_id` を追加

  * リクエスト受信で登録、返信で `pop` して `send(to=client_id, ...)`
* 受け入れ基準：既存の単体RPC/単体PDUテスト緑（subscriptionsが空なら誰にも送らない仕様で）

## フェーズ5：健全性と掃除

* `serve(..., ping_interval=20, ping_timeout=20)` などで死活監視
* `on_disconnect(client_id)` を受けて

  * `subscriptions` から除去
  * `route` の値に残る client\_id を清掃（逆引きIndexがあると楽）
* 受け入れ基準：強制切断やネットワークエラーの再現テストが安定

## フェーズ6：LVC & バックプレッシャ（任意）

* **LVC**：`last_value[(robot, topic)]` を保持し、`DECLARE` 直後に最新値を即送信（UX向上）
* **背圧**：clientごと `asyncio.Queue(maxsize=N)`＋専用送信タスク

  * ポリシ：ドロップ / 最新優先 / ブロック の選択を設定で

## フェーズ7：機能切替を本番ON（段階展開）

* サービス設定（例：`max_clients>1` or `multi_client_enabled=true`）で多接続ON
* ログに `client_id` を必ず含める（障害解析・問合せ対応のため）
* 旧APIは当面残し、ログにデプリケーション警告のみ

---

## 小さな実装メモ（壊さない工夫）

* 旧単一接続互換：`self.websocket` 参照が残っても壊れないように

  * プロパティで提供し、`clients` の先頭要素（または最後に接続したもの）を返す**互換アクセサ**にする
* 例外の一元化：`send()` は `True/False` を返し、詳細はログ＋メトリクスに集約
* 設定フラグの優先順位：

  * `max_clients=1` → 実質従来
  * `max_clients>1` → 多接続
  * 明示 `multi_client_enabled` があればそれを優先

---

## 各フェーズの「Doneの定義」（抜粋）

* F1：`role=CLIENT`/`SERVER` で既存の全テスト緑、APIシグネチャ変更なし
* F2：`send(to=...)` が**存在しないclient\_id**で False を返す／存在すれば成功
* F3：旧`on_message`しか登録していない既存アプリが**無修正で動く**
* F4：`DECLARE` したクライアント**だけ**にPDUが届く（未宣言には届かない）
* F5：切断時に `subscriptions`／`route` がリークしない
* F7：`max_clients>1` で複数同時接続＆宛先指定送信の統合テストが緑

---

## リスクと手当

* **同時sendの競合** → per-client `asyncio.Lock()` or `Queue`
* **ゾンビ購読** → `on_disconnect`で必ず掃除＋宣言にTTL（任意）
* **誤配信** → 送信直前に `client_id ∈ subscriptions` 再チェック
* **性能退行** → F2時点でベンチ（1/2/10/50接続）をQuickに計測

