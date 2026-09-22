"""
core/identity.py
Humanity層：本人性・参加のモック実装。

方針：
- Meta Marche出店者、および大人食堂UBI受給者は World ID Adapter（成人対象）で扱う。
- 子ども食堂の受益者（子どもと保護者）は World ID を使わず、
  Public Credential Adapter（保護者確認・制度上の資格確認）で扱う。
  ※ World ID の Orb 認証は成人が対象であるため、子ども本人をWorld IDで
     認証する設計にはしない、というVISION.md/README.mdの方針をコードに反映している。
"""
from dataclasses import dataclass
from enum import Enum


class IdentityLevel(str, Enum):
    UNVERIFIED = "未認証"
    DEVICE_VERIFIED = "デバイス認証"
    ORB_VERIFIED = "Orb認証済み"


# 各認証レベルでのUBI給付率（未認証は給付対象外、デバイス認証は暫定半額、Orb認証済みで満額）
UBI_PAYOUT_RATIO = {
    IdentityLevel.UNVERIFIED: 0.0,
    IdentityLevel.DEVICE_VERIFIED: 0.5,
    IdentityLevel.ORB_VERIFIED: 1.0,
}


@dataclass
class WorldIDMock:
    """Meta Marche出店者・大人食堂UBI受給者向けの本人確認モック（成人対象）。"""

    level: IdentityLevel = IdentityLevel.UNVERIFIED

    def verify(self, level: IdentityLevel) -> IdentityLevel:
        self.level = level
        return self.level

    def monthly_ubi(self, base_amount_yen: int) -> int:
        """認証レベルに応じたUBI給付額（円）を返す。"""
        ratio = UBI_PAYOUT_RATIO[self.level]
        return int(base_amount_yen * ratio)


@dataclass
class PublicCredentialMock:
    """子ども食堂の受益者（子ども・保護者）向けの資格確認モック。

    World IDとは別経路。保護者確認・制度上の資格確認（例：就学援助対象等）を
    想定したプレースホルダーで、実際の制度連携は未実装。
    """

    guardian_confirmed: bool = False
    eligibility_note: str = ""

    def confirm_guardian(self, note: str = "") -> bool:
        self.guardian_confirmed = True
        self.eligibility_note = note or "保護者確認済み（制度上の資格確認は別途）"
        return self.guardian_confirmed
