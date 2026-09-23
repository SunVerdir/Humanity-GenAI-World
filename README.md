# Humanity-GenAI-World

**Humanity First. GenAI at the Center. World as the Horizon.**

Humanity-GenAI-Worldは、住民の本人性・参加（Humanity）を起点に、ガバメントAI「源内（Gennai）」（GenAI）を介して、地域の食・支援・社会保障に関するプロトタイプ（World）をローカル環境で実験するオープンな開発プロジェクトです。

プロジェクトの背景にある思想については [VISION.md](./VISION.md) を参照してください。本ドキュメントでは、現在何を実装し、何を検証しようとしているかを示します。

---

## 概要

現在、以下の既存プロトタイプを接続し、地域資源の循環・配分・住民利用・台帳記録・政策シミュレーションを一連の流れとして検証することを目的としています。

| 区分 | 内容 |
|---|---|
| **Humanity** | 本人性・参加（認証モック、住民参加、住民側の利用体験） |
| **GenAI** | ガバメントAI「源内」による政策案の検討・情報整理・シミュレーション支援 |
| **World** | Meta Marche・子ども食堂DAO・Sanpoyoshi Guardian・Otona Shokudo × UBI |

「World」は特定のプロジェクトに限定した概念ではなく、地域社会のプロトタイプ領域全般を指す、拡張可能な区分です。

現在のローカルMVPでは、次の4タブを一つの画面で接続しています。

1. **Identity & UBI** — 認証レベルとUBI条件のシミュレーション
2. **Metaマルシェ循環** — 食材の買上げと子ども食堂への配分案生成
3. **源内 政策策定ルーム** — 現在のUBI条件・ledgerを参照するPolicy Copilot
4. **住民ダッシュボード** — UBI受取、ウォレット残高、食堂利用、利用記録の確認

## 現在のデータフロー

```text
Identity & UBI
   ↓
Metaマルシェ循環
   ↓
ALLOCATION_PROPOSED（配分案）
   ↓
ledger
   ├─→ 源内 Policy Copilot
   └─→ 住民ダッシュボード
          ↓
       UBI_USED（利用記録）
          ↓
       ledger
          ↓
     Human Decision
```

## 構成コンポーネント

このリポジトリは、以下の既存プロトタイプの技術資産を土台に、統合レイヤーを構築します。

- **[kodomo-shokudo-dao-gennai](https://github.com/SunVerdir/kodomo-shokudo-dao-gennai)** — 子ども食堂DAO × Metaマルシェ。段階的本人確認と資金循環のプロトタイプ（Zenodo DOI: [10.5281/zenodo.22040861](https://doi.org/10.5281/zenodo.22040861)）
- **[sanpoyoshi-guardian](https://github.com/SunVerdir/sanpoyoshi-guardian)** — Metaマルシェの出品を子ども食堂へ分配するAIエージェント（ADK + Firestore + Cloud Run、Human-in-the-loopの承認フロー実装済み）
- **[OtonaShokudo-UBI-GenAI](https://github.com/SunVerdir/OtonaShokudo-UBI-GenAI)** — 大人食堂UBI政策シミュレーター（Streamlit / stlite、[ライブデモ](https://sunverdir.github.io/OtonaShokudo-UBI-GenAI/)）

## 源内（Gennai）の位置づけ

源内は、政策判断を自律的に行うシステムではありません。政策案の検討、情報整理、シナリオ比較、シミュレーションなどを通じて、人間の意思決定を支援するAIインターフェース（Government AI / Policy Copilot）です。最終的な判断・承認は、常に人間（職員・住民・意思決定者）が行います。

## 現在の実装状況

本リポジトリでは、統合レイヤーの4タブMVPを実装しています。

- [x] `core/identity.py`（World ID／Public Credentialモック）の実装
- [x] `core/allocation.py`（Metaマルシェ→子ども食堂の配分案生成、簡易記帳）の実装
- [x] `core/policy_ai.py`（源内のルールベースPolicy Copilot。UBI条件・直近の配分結果を踏まえて応答）の実装
- [x] `core/resident.py`（住民ダッシュボード向けの配分読込・UBI利用記録）の実装
- [x] Streamlit 4タブ（Identity & UBI／Metaマルシェ循環／源内 政策策定ルーム／住民ダッシュボード）のMVP実装
- [x] `session_state`によるタブ間のUBI条件・配分案・ウォレット状態の連携
- [x] `ALLOCATION_PROPOSED` と `UBI_USED` を同一ledgerへ記録する流れ
- [x] `tests/test_flow.py` によるIdentity→UBI→配分→源内→住民利用のcoreロジック検証
- [x] GitHub Actionsによるスモークテスト自動実行
- [ ] `core/`の残り（payment・marketplace・dao・ubi・audit）の実装
- [ ] `adapters/`（本番想定のWorld ID／World Money／本物の生成AI等への差し替え口）の実装
- [ ] 実LLM・本番認証・実決済との接続検証
- [ ] デモ動画の作成

## ローカルでの動かし方

```bash
git clone https://github.com/SunVerdir/Humanity-GenAI-World.git
cd Humanity-GenAI-World
pip install -r requirements.txt
streamlit run app.py
```

起動すると、次の4タブが表示されます。

- Identity & UBI
- Metaマルシェ循環
- 源内 政策策定ルーム
- 住民ダッシュボード

スモークテストは次のコマンドで実行できます。

```bash
python tests/test_flow.py
```

## 想定デモシナリオ

最終的なデモでは、機能を個別に説明するのではなく、一つの政策シナリオを最初から最後まで動かして見せます。

1. Identity & UBIで認証レベルとUBI条件を確認する
2. Metaマルシェで食材を選び、子ども食堂への配分案を生成する
3. `ALLOCATION_PROPOSED` がledgerに記録されたことを確認する
4. 源内に直近の配分案やUBI条件について質問する
5. 住民ダッシュボードでUBIを受け取り、食堂で一部を利用する
6. `UBI_USED` が同じledgerに記録され、ウォレット残高が減ることを確認する
7. 人間が条件を変更し、次のシナリオを考える

**「AIが政策を決める」のではなく、「AIを使って人間が政策を試してみる」**ことをデモの軸に置きます。

## ロードマップ

- **Phase 1（〜2026年11月9日）**：[ヒーローズ・オンラインリーグ2026](https://heroes-league.net/2026/)応募に向けたローカルプロトタイプ（Python/Streamlit）の実装、4タブMVPの整理、ProtoPedia登録、3分紹介動画の作成
- **Phase 2（2026年11月）**：GENIAC-PRIZE 2026提案書・デモ動画への統合。大人食堂UBI政策提言の実現に向けたプロトタイプとしての位置づけを整理
- **Phase 3（2027年〜）**：自治体実証データをもとにした政策提言（大人食堂UBI）への展開

## このプロジェクトが示さないもの

本リポジトリは、政策の実施・制度化・予算措置を示すものではなく、社会システムの設計仮説をローカル環境で検証するための実験的実装です。

現在の住民ダッシュボードにおけるウォレット・UBI受取・食堂利用は、Streamlitのセッション状態と簡易ledgerを用いたシミュレーションです。実際の給付、決済、本人確認、自治体制度、政策効果を実証するものではありません。数値・人口・配分値は概念実証用のモック／仮モデルとして扱います。

## ライセンス

コード：MIT License（予定）

---

*Humanity-GenAI-World は、菅野敦也（経営DXラボ CIO）による、AI駆動開発（Vibe Coding）を通じた地方創生AXの実験プロジェクトです。*