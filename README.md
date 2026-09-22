# Humanity-GenAI-World

**Humanity First. GenAI at the Center. World as the Horizon.**

Humanity-GenAI-Worldは、住民の本人性・参加（Humanity）を起点に、ガバメントAI「源内（Gennai）」（GenAI）を介して、地域の食・支援・社会保障に関するプロトタイプ（World）をローカル環境で実験するオープンな開発プロジェクトです。

プロジェクトの背景にある思想については [VISION.md](./VISION.md) を参照してください。本ドキュメントでは、現在何を実装し、何を検証しようとしているかを示します。

---

## 概要

現在、以下の既存プロトタイプを接続し、地域資源の循環・配分・監査・政策シミュレーションを一連の流れとして検証することを目的としています。

| 区分 | 内容 |
|---|---|
| **Humanity** | 本人性・参加（出店者確認、住民参加） |
| **GenAI** | ガバメントAI「源内」による政策案の検討・情報整理・シミュレーション支援 |
| **World** | Meta Marche・子ども食堂DAO・Sanpoyoshi Guardian・Otona Shokudo × UBI |

「World」は特定の3プロジェクトに限定した概念ではなく、地域社会のプロトタイプ領域全般を指す、拡張可能な区分です。

体験の流れとしては、次の一本道を想定しています。

```
Humanity（住民参加）
   ↓
Meta Marche（出品・調達）
   ↓
子ども食堂DAO（資金・食材循環）
   ↓
Sanpoyoshi Guardian（AI配分案 → 人間承認 → 監査記帳）
   ↓
Otona Shokudo × UBI（政策シミュレーション）
   ↓
源内（政策案の整理・シナリオ比較）
```

## 構成コンポーネント

このリポジトリは、以下の既存プロトタイプの技術資産を土台に、統合レイヤーを構築します。

- **[kodomo-shokudo-dao-gennai](https://github.com/SunVerdir/kodomo-shokudo-dao-gennai)** — 子ども食堂DAO × Metaマルシェ。段階的本人確認と資金循環のプロトタイプ（Zenodo DOI: [10.5281/zenodo.22040861](https://doi.org/10.5281/zenodo.22040861)）
- **[sanpoyoshi-guardian](https://github.com/SunVerdir/sanpoyoshi-guardian)** — Metaマルシェの出品を子ども食堂へ分配するAIエージェント（ADK + Firestore + Cloud Run、Human-in-the-loopの承認フロー実装済み）
- **[OtonaShokudo-UBI-GenAI](https://github.com/SunVerdir/OtonaShokudo-UBI-GenAI)** — 大人食堂UBI政策シミュレーター（Streamlit / stlite、[ライブデモ](https://sunverdir.github.io/OtonaShokudo-UBI-GenAI/)）

## 源内（Gennai）の位置づけ

源内は、政策判断を自律的に行うシステムではありません。政策案の検討、情報整理、シナリオ比較、シミュレーションなどを通じて、人間の意思決定を支援するAIインターフェース（Government AI / Policy Copilot）です。最終的な判断・承認は、常に人間（職員・住民・意思決定者）が行います。

## 現在の実装状況

本リポジトリは、統合レイヤーの設計・構築段階にあります。MVPとして3タブが実装済みです。

- [x] 3プロジェクトの技術資産（Firestore構造、ハッシュチェーン台帳、Streamlit/stlite資産）の棚卸し
- [x] VISION.md（思想）の策定
- [x] `core/identity.py`（World ID／Public Credentialモック）の実装
- [x] `core/allocation.py`（Metaマルシェ→子ども食堂の配分案生成、簡易記帳）の実装
- [x] `core/policy_ai.py`（源内のルールベースPolicy Copilot。UBI条件・直近の配分結果を踏まえて応答）の実装
- [x] Streamlit 3タブ（Identity & UBI／Metaマルシェ循環／源内 政策策定ルーム＝チャットUI）のMVP実装。3タブ間でUBI条件・配分結果をsession_stateで連携
- [x] `tests/test_flow.py`（Tab1→Tab2→Tab3のデータ連携をcoreロジックレベルで検証するスモークテスト、6項目すべて合格）
- [ ] `core/`の残り（payment・marketplace・dao・ubi・audit）の実装
- [ ] `adapters/`（本番想定のWorld ID／World Money／本物の生成AI等への差し替え口）の実装
- [ ] 残り1タブ（住民ダッシュボード）の実装
- [ ] デモ動画の作成

現時点のMVPは、Identity & UBI／Metaマルシェ循環／源内 政策策定ルームの3タブです。子ども食堂DAO・Sanpoyoshi Guardian・大人食堂UBIそのものの動作は、各コンポーネントの個別リポジトリをご参照ください。

## ローカルでの動かし方

```bash
git clone https://github.com/SunVerdir/Humanity-GenAI-World.git
cd Humanity-GenAI-World
pip install -r requirements.txt
streamlit run app.py
```

現時点で起動すると「Identity & UBI」「Metaマルシェ循環」「源内 政策策定ルーム」の3タブが表示されます。残り1タブ（住民ダッシュボード）は未実装です。

## 想定デモシナリオ

最終的なデモでは、機能を個別に説明するのではなく、一つの政策シナリオを最初から最後まで動かして見せます。

住民が参加 → Meta Marcheに食材が出品 → 子ども食堂DAOへ資源が集まる → Sanpoyoshi Guardianが配分案を作成 → 人間が承認 → 監査記録に残る → 大人食堂UBIのシミュレーションに反映 → 源内が政策シナリオを整理 → 人間が条件を変えて再シミュレーション

**「AIが政策を決める」のではなく、「AIを使って人間が政策を試してみる」**ことをデモの軸に置きます。この流れが、3分間の紹介動画の骨格にもなる想定です。

## ロードマップ

- **Phase 1（〜2026年11月9日）**：[ヒーローズ・オンラインリーグ2026](https://heroes-league.net/2026/)応募に向けたローカルプロトタイプ（Python/Streamlit）の実装、既存3プロトタイプの接続、ProtoPedia登録、3分紹介動画の作成
- **Phase 2（2026年11月）**：GENIAC-PRIZE 2026提案書・デモ動画への統合。大人食堂UBI政策提言の実現に向けたプロトタイプとしての位置づけを整理
- **Phase 3（2027年〜）**：自治体実証データをもとにした政策提言（大人食堂UBI）への展開

## このプロジェクトが示さないもの

本リポジトリは、政策の実施・制度化・予算措置を示すものではなく、社会システムの設計仮説をローカル環境で検証するための実験的実装です。シミュレーターの数値は概念実証段階の仮モデルであり、実測データではありません。

## ライセンス

コード：MIT License（予定）

---

*Humanity-GenAI-World は、菅野敦也（経営DXラボ CIO）による、AI駆動開発（Vibe Coding）を通じた地方創生AXの実験プロジェクトです。*
