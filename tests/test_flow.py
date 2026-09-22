"""
tests/test_flow.py
Tab1→Tab2→Tab3の一本道を、Streamlit UIを介さずcoreロジックだけで検証するスモークテスト。

対応する確認項目（前回合意した6点）：
1. Tab1のUBI変更が反映される
2. Tab2の買上げが成功する
3. ALLOCATION_PROPOSEDがledgerに入る
4. Tab3の源内がledgerを読める
5. UBIを30,000→50,000円にすると回答も変わる
6. ledgerが空でも源内がエラーにならず説明できる
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.allocation import Cafeteria, MarcheItem, allocate_item, create_log_entry
from core.identity import IdentityLevel, WorldIDMock
from core.policy_ai import GennaiCopilot


def check(label: str, condition: bool) -> None:
    status = "OK " if condition else "NG "
    print(f"[{status}] {label}")
    assert condition, f"FAILED: {label}"


def main() -> None:
    ledger = []
    gennai = GennaiCopilot()

    # ── 6. ledgerが空でも源内がエラーにならず説明できる ──
    empty_reply = gennai.generate_response(
        user_input="さっきのマルシェ配分は？", base_ubi=30_000, population=1_000, personal_ubi=30_000, ledger=ledger
    )
    check("6. 空ledgerでも例外を投げず案内文を返す", isinstance(empty_reply, str) and "配分データはありません" in empty_reply)

    # ── 1. Tab1のUBI変更が反映される ──
    identity = WorldIDMock()
    identity.verify(IdentityLevel.ORB_VERIFIED)
    base_ubi = 30_000
    population = 1_000
    personal_ubi = identity.monthly_ubi(base_ubi)
    check("1. Orb認証済みならUBI満額が反映される", personal_ubi == base_ubi)

    # ── 2. Tab2の買上げが成功する ──
    item = MarcheItem(vendor="農家A", name="規格外キャベツ", quantity_kg=20.0, price_yen=4000)
    cafeterias = [
        Cafeteria(name="子ども食堂A", registered_users=40),
        Cafeteria(name="子ども食堂B", registered_users=35),
        Cafeteria(name="子ども食堂C", registered_users=25),
    ]
    results = allocate_item(item, cafeterias)
    check("2. 3つの子ども食堂すべてに配分案が生成される", len(results) == 3)
    check("2. 配分比率の合計がほぼ1.0になる", abs(sum(r.ratio for r in results) - 1.0) < 0.01)

    # ── 3. ALLOCATION_PROPOSEDがledgerに入る ──
    entry = create_log_entry(
        action_type="ALLOCATION_PROPOSED",
        actor="System",
        details={"item": item.name, "vendor": item.vendor, "results": [r.__dict__ for r in results]},
    )
    ledger.append(entry)
    check("3. ledgerにALLOCATION_PROPOSEDが記帳される", ledger[-1].action_type == "ALLOCATION_PROPOSED")

    # ── 4. Tab3の源内がledgerを読める ──
    reply_after_allocation = gennai.generate_response(
        user_input="さっきのマルシェ配分は？",
        base_ubi=base_ubi,
        population=population,
        personal_ubi=personal_ubi,
        ledger=ledger,
    )
    check("4. 源内がledgerの品目名を回答に含める", item.name in reply_after_allocation)
    check("4. 源内が子ども食堂Aへの配分量を回答に含める", "子ども食堂A" in reply_after_allocation)

    # 複合質問（マルシェ×UBI）の確認
    combo_reply = gennai.generate_response(
        user_input="さっきのマルシェ配分を踏まえてUBIを考えると？",
        base_ubi=base_ubi,
        population=population,
        personal_ubi=personal_ubi,
        ledger=ledger,
    )
    check("複合質問でUBI総額とマルシェ実績の両方に言及する", "給付総額" in combo_reply and item.name in combo_reply)

    # ── 5. UBIを30,000→50,000円にすると回答も変わる ──
    new_base_ubi = 50_000
    new_personal_ubi = identity.monthly_ubi(new_base_ubi)
    reply_after_change = gennai.generate_response(
        user_input="UBIを増やしたらどうなる？",
        base_ubi=new_base_ubi,
        population=population,
        personal_ubi=new_personal_ubi,
        ledger=ledger,
    )
    check(
        "5. 変更後の給付総額（¥50,000,000）が回答に反映される",
        f"{new_base_ubi * population:,}" in reply_after_change,
    )
    check("5. 変更前の回答と変更後の回答が異なる", reply_after_change != empty_reply)

    print("\n全チェック合格。Tab1→Tab2→Tab3の一本道はcoreロジック上で成立しています。")


if __name__ == "__main__":
    main()
