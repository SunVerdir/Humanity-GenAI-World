"""
core/resident.py
Resident Dashboard向けの読み取り・利用ロジック。

方針：
- 新しいモックデータは作らず、既存のidentityとledgerを参照する。
- Meta Marcheの配分結果はALLOCATION_PROPOSEDのledgerから読む。
- UBI利用はUBI_USEDとして同じledgerへ記帳する。
- 本モジュールは政策判断や制度確定を行わない。
"""
from typing import Any


def find_last_allocation(ledger: list[Any]) -> dict | None:
    """ledgerから直近のALLOCATION_PROPOSEDのdetailsを返す。"""
    if not isinstance(ledger, list):
        return None
    for entry in reversed(ledger):
        action_type = getattr(entry, "action_type", None)
        if action_type is None and isinstance(entry, dict):
            action_type = entry.get("action_type")
        if action_type != "ALLOCATION_PROPOSED":
            continue

        details = getattr(entry, "details", None)
        if details is None and isinstance(entry, dict):
            details = entry.get("details")
        return details if isinstance(details, dict) else None
    return None


def cafeteria_allocation(ledger: list[Any], cafeteria_name: str) -> list[dict]:
    """直近の配分案から、指定した子ども食堂の配分データを返す。"""
    allocation = find_last_allocation(ledger)
    if not allocation:
        return []

    results = allocation.get("results", [])
    if not isinstance(results, list):
        return []

    return [
        result
        for result in results
        if isinstance(result, dict) and result.get("cafeteria") == cafeteria_name
    ]


def append_ubi_used(ledger: list[Any], amount_yen: int, cafeteria_name: str) -> None:
    """住民のUBI利用を既存ledgerへ記帳する。"""
    from core.allocation import create_log_entry

    ledger.append(
        create_log_entry(
            action_type="UBI_USED",
            actor="Resident",
            details={
                "amount_yen": amount_yen,
                "cafeteria": cafeteria_name,
            },
        )
    )
