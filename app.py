import datetime
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. ページ基本設定
st.set_page_config(
    page_title="赤ちゃんすくすく記録",
    page_icon="👶",
    layout="centered"
)

# --------------------------------------------------
# ポップなデザイン用カスタムCSS（パステル調・丸みのあるデザイン）
# --------------------------------------------------
st.markdown("""
<style>
    /* 全体の背景色をほのかに優しいウォームカラーに */
    .main {
        background-color: #FFF9F5;
    }
    
    /* タイトルのデザイン */
    .pop-title {
        color: #FF6B81;
        text-align: center;
        font-weight: bold;
        font-size: 2.2rem;
        padding: 10px;
        background: #FFEAA7;
        border-radius: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 25px;
    }

    /* サブタイトルのデザイン */
    .pop-header {
        color: #FF7675;
        font-weight: bold;
        border-bottom: 3px dashed #FFB8B8;
        padding-bottom: 5px;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    /* ボタンのデザインを丸くポップに */
    .stButton > button {
        border-radius: 20px !important;
        background-color: #FFABE1 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #FF80BF !important;
        transform: scale(1.03);
    }
</style>
""", unsafe_allow_html=True)

# ポップなタイトルの表示
st.markdown('<div class="pop-title">👶 赤ちゃんすくすく記録 🍼</div>', unsafe_allow_html=True)

DATA_FILE = "baby_record.csv"


# 2. データ読み込み・保存用関数
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(
            columns=["date", "hour", "time_str", "milk_ml", "poop_size", "memo"]
        )


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


df = load_data()

# --------------------------------------------------
# 3. 入力エリア
# --------------------------------------------------
st.markdown('<h3 class="pop-header">📝 きょうの記録</h3>', unsafe_allow_html=True)

selected_date = st.date_input(
    "日付選択", datetime.date.today(), format="YYYY/MM/DD"
)
date_display = f"{selected_date.year}年{selected_date.month}月{selected_date.day}日"
date_str = selected_date.strftime("%Y-%m-%d")

with st.form("record_form", clear_on_submit=False):
    col1, col2 = st.columns(2)

    with col1:
        # 時間帯（0時台 〜 23時台）
        hour = st.selectbox(
            "⏰ 時間帯",
            options=list(range(24)),
            format_func=lambda x: f"{x}時",
        )

        # 分（0分〜55分、5分刻み）
        minute = st.selectbox(
            f"⏱️ {hour}時台の「分」",
            options=list(range(0, 60, 5)),
            format_func=lambda x: f"{x:02d}分",
        )

        time_str = f"{hour:02d}:{minute:02d}"
        st.caption(f"選択された時刻： **{time_str}**")

    with col2:
        milk_ml = st.number_input(
            "🍼 ミルクの量 (ml)", min_value=0, max_value=300, step=10, value=0
        )
        poop_size = st.radio(
            "💩 うんちの量", options=["なし", "小", "中", "大"], horizontal=True
        )

    memo = st.text_input("✏️ メモ", placeholder="例：ごきげん、ちょっと吐き戻し")

    submitted = st.form_submit_button("✨ 記録を保存する")

    if submitted:
        new_data = {
            "date": date_str,
            "hour": hour,
            "time_str": time_str,
            "milk_ml": milk_ml,
            "poop_size": poop_size,
            "memo": memo,
        }

        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        save_data(df)

        st.success(f"{date_display} {time_str} の記録を保存しました！")
        st.rerun()

# --------------------------------------------------
# 4. 可視化・管理エリア（ポップなデザイングラフ）
# --------------------------------------------------
st.write("---")
st.markdown(f'<h3 class="pop-header">📊 {date_display} のサマリー</h3>', unsafe_allow_html=True)

day_data = df[df["date"] == date_str]

if not day_data.empty:
    # --- 指標のカード表示 ---
    total_milk = day_data["milk_ml"].sum()
    poop_count = len(day_data[day_data["poop_size"] != "なし"])

    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric("🍼 合計ミルク量", f"{total_milk} ml")
    metric_col2.metric("💩 うんち回数", f"{poop_count} 回")

    # --- 24時間 描画用データの準備 ---
    full_hours = pd.DataFrame({"hour": list(range(24))})
    hourly_summary = (
        day_data.groupby("hour")["milk_ml"].sum().reset_index()
    )
    chart_data = pd.merge(full_hours, hourly_summary, on="hour", how="left").fillna(0)

    chart_data["hour_label"] = chart_data["hour"].apply(lambda x: f"{x:02d}:00")

    # --- Plotlyによるポップな横棒グラフ ---
    st.markdown("##### 🍼 時間帯ごとのミルク量")

    fig = px.bar(
        chart_data,
        x="milk_ml",
        y="hour_label",
        orientation="h",
        labels={"milk_ml": "ミルク (ml)", "hour_label": "時間"},
        text="milk_ml",
        color="milk_ml",
        # ポップで明るいカラーグラデーション (パステルサンセット調)
        color_continuous_scale=["#FFEAA7", "#FF7675"]
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        height=580,
        margin=dict(l=10, r=20, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",   # 背景を透明にしてスッキリ
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,     # カラーバーを非表示にしてシンプル化
    )

    fig.update_traces(
        texttemplate="%{text} ml",
        textposition="outside",
        cliponaxis=False,
        marker=dict(line=dict(color="#FF6B81", width=1.5)) # バーのフチどり
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- タイムライン（テーブル） ---
    st.markdown("##### 📝 タイムライン（記録の削除・確認）")
    
    sorted_day_data = day_data.sort_values("time_str")

    h_col1, h_col2, h_col3, h_col4, h_col5 = st.columns([1.5, 2, 1.5, 3, 1])
    h_col1.markdown("**時刻**")
    h_col2.markdown("**ミルク**")
    h_col3.markdown("**うんち**")
    h_col4.markdown("**メモ**")
    h_col5.markdown("**削除**")
    st.divider()

    for idx, row in sorted_day_data.iterrows():
        c1, c2, c3, c4, c5 = st.columns([1.5, 2, 1.5, 3, 1])
        c1.write(row["time_str"])
        c2.write(f"{row['milk_ml']} ml" if row["milk_ml"] > 0 else "-")
        c3.write(row["poop_size"])
        c4.write(row["memo"] if pd.notna(row["memo"]) and row["memo"] != "" else "-")
        
        if c5.button("🗑️", key=f"del_{idx}"):
            df = df.drop(idx)
            save_data(df)
            st.toast(f"{row['time_str']} の記録を削除しました")
            st.rerun()

else:
    st.info("本日の記録はまだありません。")