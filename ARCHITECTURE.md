# Architecture — Humanity-GenAI-World

## 目的

Humanity-GenAI-World は、住民・行政の「こうしたい」を起点に、ガバメントAI「源内」を Policy Copilot として介し、地域の社会システムをローカルで試作するためのMVPです。

Phase 1では、**Identity & UBI → Metaマルシェ → ledger → 源内 → 住民ダッシュボード**というデータの一本道を、外部サービスに依存しないローカルモックとして確認します。

## 現在のデータフロー

```text
┌─────────────────────┐
│ Identity & UBI      │
│ 本人確認モック       │
│ UBI / 対象人口       │
└─────────┬───────────┘
          │ session state
          ▼
┌─────────────────────┐
│ Metaマルシェ循環      │
│ 買上げ → 配分案生成   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ ledger              │
│ ALLOCATION_PROPOSED │
│ 配分案の単一情報源    │
└──────┬──────────┬───┘
       │          │
       │          └──────────────┐
       ▼                         ▼
┌─────────────────────┐   ┌─────────────────────┐
│ 源内 Policy Copilot │   │ 住民ダッシュボード    │
│ ledger + UBI条件を  │   │ UBI受取・利用         │
│ 読み取り整理・比較   │   │ ウォレット状態         │
└─────────┬───────────┘   └─────────┬───────────┘
          │                         │
          │                         ▼
          │                   UBI_USED
          │                         │
          └────────────┬────────────┘
                       ▼
              ┌──────────────────┐
              │ Human Decision   │
              │ 人間が条件・承認  │
              └──────────────────┘
```

## Source of Truth

### ledger

Metaマルシェの配分案と住民のUBI利用記録について、`ledger` を単一の情報源（Single Source of Truth）として扱います。

- `ALLOCATION_PROPOSED`：配分案
- `UBI_USED`：住民によるUBI利用のシミュレーション記録

UI用stateと記録済みデータを分離して二重管理しないことを基本方針とします。

なお、Phase 1のledgerは**簡易台帳**であり、改ざん耐性を備えたハッシュチェーンではありません。ハッシュチェーン監査は既存の Sanpoyoshi Guardian 側の実装資産を参照します。

## Humanity / GenAI / World

| 層 | 現在の実装 |
|---|---|
| Humanity | `core/identity.py` の本人確認モック、UBI条件、住民利用体験 |
| GenAI | `core/policy_ai.py` のルールベース Policy Copilot |
| World | `core/allocation.py` のMetaマルシェ→子ども食堂配分案、`core/resident.py` の住民利用ロジック |

外部のWorld ID、World Money、LLM APIなどはPhase 1の必須依存にしていません。将来の接続口は `adapters/` として段階的に切り出す想定です。

## 人間による判断境界

源内は以下を行いません。

- 政策の最終決定
- 配分の最終承認
- 予算措置
- 制度化
- 実際の給付・決済

住民ダッシュボードも、実際の給付・決済を行うものではありません。UBI受取・利用はStreamlitのセッション状態と簡易ledgerによるシミュレーションです。

源内が返すのは、現在のシミュレーション条件やledgerに記録された配分案を整理した材料です。

Metaマルシェの配分関数も「配分案」を生成するだけで、確定処理は行いません。

## 数値の扱い

現在の数値には2種類あります。

1. **アプリ内で実際に計算・更新される値**
   - UBI月額
   - 対象人口
   - 月間給付総額
   - 本人の受給試算額
   - 住民ウォレットのセッション内残高
   - ledger内の配分案・利用記録

2. **モック／仮モデル**
   - 出品者・食材・価格
   - 子ども食堂の登録利用予定人数
   - 認証レベルごとのUBI給付率

これらは現実の自治体財政、給付実績、決済実績、政策効果を示す実測データではありません。

## テスト

`tests/test_flow.py` はStreamlit UIを介さず、次の一本道をcoreロジックレベルで確認します。

```text
Identity
  ↓
UBI condition
  ↓
Meta Marche allocation
  ↓
ALLOCATION_PROPOSED
  ↓
ledger
  ↓
Gennai response
  ↓
UBI condition change
  ↓
Gennai response change
  ↓
Resident wallet
  ↓
UBI_USED
  ↓
ledger
```

実行：

```bash
python tests/test_flow.py
```

## 次の拡張

4タブMVPを基準として、以下を段階的に検証します。

- adapter layer
- 実LLM接続の比較検証
- 本番想定の認証・決済連携
- 監査・承認フローの拡張
- 住民・行政双方のUI/UX改善

実装範囲を越える機能については、READMEおよびVISION.mdで明示します。