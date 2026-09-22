"""
Humanity-GenAI-World — MVP (Phase 1)

現時点では、4タブ構想のうち以下3タブを実装している。
- Identity & UBI（本人確認モック＋給付シミュレーション）
- Meta Marche循環（買上・子ども食堂への配分案）
- 源内 政策策定ルーム（AIとの政策壁打ちチャット）

「住民ダッシュボード」は未実装（README.mdのロードマップ参照）。
すべて概念実証段階のローカルモックであり、実測データではない。
"""
import streamlit as st

from core.allocation import Cafeteria, MarcheItem, allocate_item, create_log_entry
from core.identity import IdentityLevel, WorldIDMock
from core.policy_ai import GennaiCopilot

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

tab1, tab2, tab3 = st.tabs(["👤 Identity & UBI", "🥕 Metaマルシェ循環", "🧠 源内 政策策定ルーム"])

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
