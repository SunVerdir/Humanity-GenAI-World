"""
core/allocation.py
World層：Meta Marcheで買い上げた食材を、子ども食堂へ配分するロジック。

sanpoyoshi-guardian の compute_distribution_ratio の考え方を簡略移植したもの。
配分比率は「登録利用予定人数」に応じた単純な按分とし、
最終判断は常に人間（職員）の承認を前提とする（Human-in-the-loop）。
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class MarcheItem:
    vendor: str
    name: str
    quantity_kg: float
    price_yen: int


@dataclass
class Cafeteria:
    name: str
    registered_users: int  # 登録利用予定人数（按分の重み）


@dataclass
class AllocationResult:
    cafeteria: str
    ratio: float
    quantity_kg: float


def compute_distribution_ratio(cafeterias: list[Cafeteria]) -> dict[str, float]:
    """登録利用予定人数に応じた按分比率を返す（合計はおおむね1.0）。"""
    total_users = sum(c.registered_users for c in cafeterias) or 1
    return {c.name: round(c.registered_users / total_users, 4) for c in cafeterias}


def allocate_item(item: MarcheItem, cafeterias: list[Cafeteria]) -> list[AllocationResult]:
    """1品目のMetaマルシェ出品を、登録利用予定人数の比率で子ども食堂へ配分案として計算する。

    ※ ここで返すのは「配分案」であり、実際の配分確定は職員の承認を経る（本関数は決定しない）。
    """
    ratios = compute_distribution_ratio(cafeterias)
    return [
        AllocationResult(
            cafeteria=name,
            ratio=ratio,
            quantity_kg=round(item.quantity_kg * ratio, 2),
        )
        for name, ratio in ratios.items()
    ]


@dataclass
class LedgerEntry:
    action_type: str
    actor: str
    details: dict
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


def create_log_entry(action_type: str, actor: str, details: dict) -> LedgerEntry:
    """監査ログの1件分を作る（sanpoyoshi-guardianのhash_chain.pyと同じ発想の
    簡易版。本実装ではハッシュチェーン化は行わず、記帳の型のみを揃えている）。
    """
    return LedgerEntry(action_type=action_type, actor=actor, details=details)
