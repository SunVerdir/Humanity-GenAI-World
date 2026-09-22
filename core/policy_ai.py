"""
core/policy_ai.py
GenAI層：ガバメントAI「源内」のPolicy Copilotロジック（Phase 1はルールベース）。

方針（VISION.md/README.mdと同じ線引き）：
- 政策判断を自律的に行わない。定型的な整理・比較の材料を返すだけ。
- 最終的な条件変更・判断は、常に人間（画面操作）が行う。
- あえてLLM API接続は行わず、Local Firstのままルールベースで動作を確認する
  （必要性が確認できた段階で adapters/gennai_* へ切り出す想定）。
- 応答に含む数値・配分結果は、記帳ログ（ledger）を単一の情報源として
  そこから読み取ったものだけを使う。架空の係数や根拠のない予測値
  （「◯倍になる」「活性化する」等）は返さない。
- ledgerの中身が想定外の形（空・型違い）でも例外を送出せず、防御的に扱う。
"""
from typing import Any


class GennaiCopilot:
    name = "源内"

    def _find_last_allocation(self, ledger: list[Any]) -> dict | None:
        """記帳ログ（ledger）から直近のMetaマルシェ配分案を防御的に探す。
        ledgerを単一の情報源とし、別途stateを複製しない。
        """
        if not isinstance(ledger, list):
            return None
        for entry in reversed(ledger):
            action_type = getattr(entry, "action_type", None)
            if action_type is None and isinstance(entry, dict):
                action_type = entry.get("action_type")
            if action_type == "ALLOCATION_PROPOSED":
                details = getattr(entry, "details", None)
                if details is None and isinstance(entry, dict):
                    details = entry.get("details")
                return details if isinstance(details, dict) else None
        return None

    def _format_allocation(self, last_allocation: dict) -> str:
        item_name = last_allocation.get("item", "不明な品目")
        vendor = last_allocation.get("vendor", "不明な出店者")
        results = last_allocation.get("results", [])
        lines = []
        if isinstance(results, list):
            for r in results:
                if not isinstance(r, dict):
                    continue
                cafeteria = r.get("cafeteria", "食堂")
                qty = r.get("quantity_kg", 0)
                ratio = r.get("ratio")
                ratio_str = f"{ratio:.0%}" if isinstance(ratio, (int, float)) else "—"
                lines.append(f"  - {cafeteria}：{qty}kg（{ratio_str}）")
        detail_text = "\n".join(lines) if lines else "  - 配分詳細の解析に失敗しました"
        return f"{vendor}の『{item_name}』\n{detail_text}"

    def generate_response(
        self,
        user_input: str,
        base_ubi: int,
        population: int,
        personal_ubi: int,
        ledger: list[Any],
    ) -> str:
        last_allocation = self._find_last_allocation(ledger)
        total_outlay = base_ubi * population

        has_ubi_kw = any(k in user_input for k in ["UBI", "給付", "増", "減", "額", "お金", "月額"])
        has_marche_kw = any(
            k in user_input for k in ["マルシェ", "食材", "配分", "子ども食堂", "直近", "キャベツ", "トマト"]
        )

        # 複合質問（マルシェ配分を踏まえたUBI）を最初に判定する
        if has_marche_kw and has_ubi_kw:
            if last_allocation:
                return (
                    f"直近のMetaマルシェの配分実績（{last_allocation.get('item', '品目')}）と、"
                    "現在のUBI給付設定をあわせて参照しています。\n\n"
                    f"- 現在の基本UBI：月額 ¥{base_ubi:,}（月間給付総額：¥{total_outlay:,}）\n"
                    f"- 直近の地域循環：{self._format_allocation(last_allocation)}\n\n"
                    "現物給付（マルシェ循環）と現金給付（UBI）のバランスは、"
                    "「Identity & UBI」タブで給付額を変更しながら比較できます。"
                )
            return (
                f"現在のUBI設定は月額 ¥{base_ubi:,}（町全体で月額 ¥{total_outlay:,}）です。\n\n"
                "なお、直近のマルシェ配分データはまだありません。「Metaマルシェ循環」タブで"
                "買い上げを実行すると、現物配分データとあわせて確認できます。"
            )

        if has_marche_kw:
            if last_allocation:
                return (
                    f"直近で記録されたMetaマルシェの配分案は次のとおりです。\n\n"
                    f"{self._format_allocation(last_allocation)}\n\n"
                    "この配分案は登録利用予定人数に基づく計算結果であり、実際の確定には"
                    "職員による承認が必要です。"
                )
            return (
                "現在、記録されている配分データはありません。「Metaマルシェ循環」タブで"
                "『行政（DAO）が買い上げ、配分案を生成する』を実行すると、ここで結果を参照できます。"
            )

        if has_ubi_kw:
            return (
                "現在の「Identity & UBI」タブの設定条件は次のとおりです。\n\n"
                f"- 基本UBI給付額：月額 ¥{base_ubi:,} / 人\n"
                f"- 対象人口：{population:,}人\n"
                f"- 町全体の月間給付総額（全員Orb認証と仮定）：¥{total_outlay:,}\n"
                f"- あなたの現在の受給試算額：月額 ¥{personal_ubi:,}\n\n"
                "条件を変えて総額がどう変わるかは、「Identity & UBI」タブのスライダーを"
                "動かして確認してみてください。"
            )

        if any(k in user_input for k in ["承認", "監査", "改ざん", "台帳"]):
            return (
                "「Metaマルシェ循環」タブで生成された配分案は、記帳ログに残ります。"
                "源内は配分案（たたき台）を示すだけで、最終判断は常に人間（職員）が行う"
                "Human-in-the-loopの原則を前提としています。"
            )

        return (
            "ガバメントAI「源内」です。各タブの現在のシミュレーション状態を踏まえて整理できます。\n\n"
            "例えば次のように聞いてみてください。\n"
            "- 「さっきのマルシェ配分を踏まえてUBIを考えると？」（配分と給付額の両方を参照）\n"
            "- 「さっきのマルシェ配分は？」（直近の地域循環を参照）\n"
            "- 「UBIを増やしたらどうなる？」（給付総額と条件を確認）"
        )
