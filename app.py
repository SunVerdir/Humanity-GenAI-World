"""
Humanity-GenAI-World — MVP (Phase 1)

現時点では、4タブ構想を実装している。
- Identity & UBI（本人確認モック＋給付シミュレーション）
- Meta Marche循環（買上・子ども食堂への配分案）
- 源内 政策策定ルーム（AIとの政策壁打ちチャット）

「住民ダッシュボード」は実装済み（Phase 1のセッション内ウォレット）。
すべて概念実証段階のローカルモックであり、実測データではない。
"""
import streamlit as st

from core.allocation import Cafeteria, MarcheItem, allocate_item, create_log_entry
from core.identity import IdentityLevel, WorldIDMock
from core.policy_ai import GennaiCopilot
from core.resident import append_ubi_used, cafeteria_allocation

st.set_page_config(page_title="Humanity-GenAI-World", page_icon="🌏", layout="wide")

# ── セッションステートの初期化 ───────────────────────────────────
if "ledger" not in st.session_state:
    st.session_state.ledger = []
if "identity" not in st.session_state:
    st.session_state.identity = WorldIDMock()
if "gennai" not in st.session_state:
    st.session_state.gennai = GennaiCopilot()
if "base_ubi" not in st.session_state:
    st.session_state.base_ubi = 30_000
if "resident_wallet" not in st.session_state:
    st.session_state.resident_wallet = 0
if "population" not in st.session_state:
    st.session_state.population = 1_000
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": "こんにちは。ガバメントAI「源内」です。現在のシミュレーション条件をもとに、政策シナリオを一緒に検討しましょう。",
        }
    ]

st.title("🌏 Humanity-GenAI-World")
st.caption("Humanity First. GenAI at the Center. World as the Horizon.（概念実証段階のローカルプロトタイプ）")

tab1, tab2, tab3, tab4 = st.tabs(["👤 Identity & UBI", "🥕 Metaマルシェ循環", "🧠 源内 政策策定ルーム", "🏠 住民ダッシュボード"])

# ── Tab 1: Identity & UBI ────────────────────────────────────────
with tab1:
    st.subheader("本人確認（World ID モック・成人対象）")

    level = st.radio(
        "認証レベルを選択",
        options=list(IdentityLevel),
        format_func=lambda x: x.value,
        horizontal=True,
    )
    st.session_state.identity.verify(level)

    st.divider()
    st.subheader("UBI給付シミュレーション")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.base_ubi = st.slider(
            "UBI給付額（月額・円／人）", 10_000, 100_000, st.session_state.base_ubi, step=5_000
        )
    with col2:
        st.session_state.population = st.slider(
            "対象人口（人）", 100, 10_000, st.session_state.population, step=100
        )

    personal_ubi = st.session_state.identity.monthly_ubi(st.session_state.base_ubi)
    st.metric("あなたの今月のUBI給付額", f"¥{personal_ubi:,}")

    total_outlay = st.session_state.base_ubi * st.session_state.population
    st.metric("町全体（全員がOrb認証と仮定）の月間給付総額", f"¥{total_outlay:,}")
    st.caption("※ 概念実証段階の仮モデルです。実際の財源・制度条件は別途検討が必要です。")

# ── Tab 2: Meta Marche循環 ───────────────────────────────────────
with tab2:
    st.subheader("Metaマルシェ：出品（モックデータ）")

    marche_items = [
        MarcheItem(vendor="農家A", name="規格外キャベツ", quantity_kg=20.0, price_yen=4000),
        MarcheItem(vendor="農家B", name="規格外トマト", quantity_kg=15.0, price_yen=6000),
    ]
    cafeterias = [
        Cafeteria(name="子ども食堂A", registered_users=40),
        Cafeteria(name="子ども食堂B", registered_users=35),
        Cafeteria(name="子ども食堂C", registered_users=25),
    ]

    st.table(
        [{"出店者": i.vendor, "品目": i.name, "数量(kg)": i.quantity_kg, "価格(円)": i.price_yen} for i in marche_items]
    )

    selected = st.selectbox("買い上げる品目を選択", options=[f"{i.vendor} / {i.name}" for i in marche_items])
    item = marche_items[[f"{i.vendor} / {i.name}" for i in marche_items].index(selected)]

    if st.button("行政（DAO）が買い上げ、配分案を生成する"):
        results = allocate_item(item, cafeterias)
        st.success(f"『{item.name}』{item.quantity_kg}kg（¥{item.price_yen:,}）を買い上げ、配分案を生成しました。")
        st.table(
            [{"子ども食堂": r.cafeteria, "配分比率": f"{r.ratio:.0%}", "配分量(kg)": r.quantity_kg} for r in results]
        )

        entry = create_log_entry(
            action_type="ALLOCATION_PROPOSED",
            actor="System",
            details={"item": item.name, "vendor": item.vendor, "results": [r.__dict__ for r in results]},
        )
        st.session_state.ledger.append(entry)
        st.info("配分案を記帳しました。実際の配分確定には職員の承認が必要です（本MVPでは承認UIは未実装）。")

    st.divider()
    st.subheader("記帳ログ（簡易台帳）")
    if st.session_state.ledger:
        st.table(
            [{"時刻": e.timestamp, "種別": e.action_type, "実行者": e.actor, "品目": e.details.get("item")} for e in st.session_state.ledger]
        )
    else:
        st.caption("まだ記帳はありません。")

# ── Tab 4: 住民ダッシュボード ─────────────────────────────────
with tab4:
    st.subheader("🏠 住民ダッシュボード")
    st.caption("Tab 1の本人確認・UBI計算と、Tab 2の配分記帳をそのまま参照します。新しいモックデータは作りません。")

    identity = st.session_state.identity
    personal_ubi = identity.monthly_ubi(st.session_state.base_ubi)

    st.subheader("本人確認")
    st.write(f"現在の認証レベル：**{identity.level.value}**")

    st.subheader("UBIウォレット")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("今月の受給試算額", f"¥{personal_ubi:,}")
    with col2:
        st.metric("現在のウォレット残高", f"¥{st.session_state.resident_wallet:,}")

    if st.button("今月分を受け取る", key="resident_receive_ubi"):
        st.session_state.resident_wallet += personal_ubi
        st.success(f"¥{personal_ubi:,}をウォレット残高に加算しました。")

    st.divider()
    st.subheader("近隣の子ども食堂メニュー（配分記帳から表示）")
    cafeteria_names = ["子ども食堂A", "子ども食堂B", "子ども食堂C"]
    selected_cafeteria = st.selectbox(
        "利用する子ども食堂",
        options=cafeteria_names,
        key="resident_cafeteria",
    )
    menu_rows = cafeteria_allocation(st.session_state.ledger, selected_cafeteria)
    if menu_rows:
        allocation = menu_rows[0]
        allocation_item = next(
            (
                entry.details.get("item")
                for entry in reversed(st.session_state.ledger)
                if getattr(entry, "action_type", None) == "ALLOCATION_PROPOSED"
            ),
            "配分品目",
        )
        st.write(f"**{allocation_item}**：{allocation.get('quantity_kg', 0)}kg（配分比率 {allocation.get('ratio', 0):.0%}）")
        st.caption("※ ここに表示しているのは、Tab 2で記録された配分案です。")
    else:
        st.info("まだ本日の配分データはありません。")

    st.divider()
    st.subheader("食堂を利用する（UBIを使う）")
    use_amount = st.number_input(
        "利用額（円）",
        min_value=0,
        max_value=max(st.session_state.resident_wallet, 0),
        value=0,
        step=500,
        key="resident_use_amount",
    )
    if st.button("食堂で使う", key="resident_use_ubi"):
        if use_amount <= 0:
            st.warning("利用額を入力してください。")
        elif use_amount > st.session_state.resident_wallet:
            st.warning("ウォレット残高を超える利用はできません。")
        else:
            st.session_state.resident_wallet -= int(use_amount)
            append_ubi_used(
                st.session_state.ledger,
                amount_yen=int(use_amount),
                cafeteria_name=selected_cafeteria,
            )
            st.success(f"¥{int(use_amount):,}を{selected_cafeteria}で利用し、ledgerに記帳しました。")

    st.divider()
    st.subheader("住民利用の記帳")
    used_entries = [
        e for e in st.session_state.ledger
        if getattr(e, "action_type", None) == "UBI_USED"
    ]
    if used_entries:
        st.table([
            {
                "時刻": e.timestamp,
                "種別": e.action_type,
                "利用額(円)": e.details.get("amount_yen"),
                "子ども食堂": e.details.get("cafeteria"),
            }
            for e in used_entries
        ])
    else:
        st.caption("まだUBI利用の記帳はありません。")

# ── Tab 3: 源内 政策策定ルーム ────────────────────────────────
with tab3:
    st.subheader("🧠 源内 政策策定ルーム")
    st.caption(
        "現在はルールベースのPolicy Copilotです（Local First・LLM API未接続）。"
        "源内は政策判断を自律的に行わず、他タブの実際のシミュレーション値をもとに"
        "整理・比較材料を返すのみで、最終判断は常に人間が行います。"
    )

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="🧠" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    if prompt := st.chat_input("源内にシナリオを相談する（例：UBIを増やしたらどうなる？）"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🧠"):
            personal_ubi = st.session_state.identity.monthly_ubi(st.session_state.base_ubi)
            response = st.session_state.gennai.generate_response(
                user_input=prompt,
                base_ubi=st.session_state.base_ubi,
                population=st.session_state.population,
                personal_ubi=personal_ubi,
                ledger=st.session_state.ledger,
            )
            st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
