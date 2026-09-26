import calendar
import datetime
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. ページ基本設定
st.set_page_config(
    page_title="芳怜ちゃん育児記録",
    page_icon="🌸",
    layout="centered"
)

# --------------------------------------------------
# カスタムCSS (iPhone・モバイル最適化)
# --------------------------------------------------
st.markdown("""
<style>
    /* 全体背景：ほんのり桜色のやさしい背景 */
    .main {
        background-color: #FFF8F9;
        font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif;
        color: #554848;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* ヘッダー */
    .luna-title-container {
        text-align: center;
        padding: 10px 0 15px 0;
        margin-bottom: 15px;
    }
    .luna-title {
        color: #FF5A79;
        font-size: 1.6rem;
        font-weight: bold;
        letter-spacing: 0.5px;
    }
    .luna-subtitle {
        color: #9E8B8B;
        font-size: 0.8rem;
        margin-top: 2px;
    }

    /* ぷっくりカード */
    .luna-card {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(255, 138, 158, 0.08);
        border: 1px solid #FFEBEF;
    }

    /* ミントグリーン枠のアクセントカード */
    .luna-card-mint {
        background-color: #F2FAF7;
        border-radius: 20px;
        padding: 16px;
        margin-bottom: 16px;
        border: 1px solid #D5F0E6;
    }

    /* サブヘッダー */
    .luna-header {
        font-size: 1.05rem;
        font-weight: bold;
        color: #FF5A79;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* メトリクス表示 */
    .luna-metric-val {
        font-size: 2.0rem;
        font-weight: bold;
        color: #FF5A79;
    }
    .luna-metric-lbl {
        font-size: 0.8rem;
        color: #8C7B7B;
    }

    /* タイムライン個別アイテム */
    .timeline-card {
        background-color: #FFF5F7;
        border-left: 5px solid #FF5A79;
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 10px;
    }
    .timeline-time {
        font-size: 1.0rem;
        font-weight: bold;
        color: #FF5A79;
    }
    .timeline-badge {
        display: inline-block;
        background-color: #FFFFFF;
        border: 1px solid #FFD2DC;
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 0.8rem;
        margin-right: 6px;
        color: #554848;
    }

    /* カレンダーセル用デザイン */
    .cal-day-box {
        background-color: #FFFFFF;
        border: 1px solid #FFE1E8;
        border-radius: 10px;
        padding: 4px 2px;
        text-align: center;
        height: 75px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
    }
    .cal-day-num {
        font-size: 0.75rem;
        color: #8C7B7B;
        font-weight: bold;
    }
    .cal-milk-val {
        font-size: 0.6rem;
        font-weight: bold;
        color: #FF5A79;
        margin-top: 1px;
    }
    
    /* 縦棒グラフ用コンテナとバー */
    .cal-bar-container {
        background-color: #FFEBF0;
        border-radius: 4px;
        height: 24px;
        width: 12px;
        margin: 2px auto 2px auto;
        display: flex;
        align-items: flex-end;
        overflow: hidden;
    }
    .cal-bar-fill {
        background: linear-gradient(0deg, #FF8A9E 0%, #FF5A79 100%);
        width: 100%;
        border-radius: 4px;
    }

    /* ボタン */
    .stButton > button {
        border-radius: 25px !important;
        background: linear-gradient(135deg, #FF8A9E 0%, #FF5A79 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 0.95rem !important;
        padding: 6px 14px !important;
        box-shadow: 0 4px 12px rgba(255, 90, 121, 0.2) !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }

    /* 入力フォーム */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border-radius: 14px !important;
        border-color: #FFD2DC !important;
    }
</style>
""", unsafe_allow_html=True)

# ヘッダー (「芳怜ちゃん育児記録」に変更)
st.markdown("""
<div class="luna-title-container">
    <div class="luna-title">🌸 芳怜ちゃん育児記録</div>
    <div class="luna-subtitle">毎日のすくすく成長記録</div>
</div>
""", unsafe_allow_html=True)

DATA_FILE = "baby_record.csv"


# 2. データ読み込み・保存関数
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
# 3. 入力エリア (起動・更新時は常に本日の日付に固定)
# --------------------------------------------------
st.markdown('<div class="luna-card">', unsafe_allow_html=True)
st.markdown('<div class="luna-header">📝 きょうの記録をつける</div>', unsafe_allow_html=True)

today_date = datetime.date.today()
selected_date = st.date_input("日付を選択", value=today_date, format="YYYY/MM/DD")

# 日付表記（例：9/26(土) や 2026年9月26日）の作成
weekdays_jp = ["月", "火", "水", "木", "金", "土", "日"]
wd_str = weekdays_jp[selected_date.weekday()]
formatted_short_date = f"{selected_date.month}/{selected_date.day}({wd_str})"
date_display = f"{selected_date.year}年{selected_date.month}月{selected_date.day}日"
date_str = selected_date.strftime("%Y-%m-%d")

with st.form("record_form", clear_on_submit=False):
    col1, col2 = st.columns(2)

    with col1:
        # 「時台」→「時」に変更
        hour = st.selectbox("時間帯", options=list(range(24)), format_func=lambda x: f"{x}時")
        minute = st.selectbox("分", options=list(range(0, 60, 5)), format_func=lambda x: f"{x:02d}分")
        time_str = f"{hour:02d}:{minute:02d}"

    with col2:
        milk_ml = st.number_input("🍼 ミルクの量 (ml)", min_value=0, max_value=300, step=10, value=0)
        poop_size = st.radio("💩 うんちの量", options=["なし", "小", "中", "大"], horizontal=True)

    memo = st.text_input("💬 メモ・ごきげん", placeholder="例：機嫌よくたくさん飲んだ！")

    submitted = st.form_submit_button("🌸 記録を保存する")

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
        st.toast(f"{time_str} の記録を保存しました 💕")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# 4. 当日のサマリー・グラフ・タイムライン
# --------------------------------------------------
day_data = df[df["date"] == date_str]

if not day_data.empty:
    total_milk = day_data["milk_ml"].sum()
    poop_count = len(day_data[day_data["poop_size"] != "なし"])

    # サマリーカード
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown(f"""
        <div class="luna-card">
            <div class="luna-header">🍼 ミルク合計</div>
            <div class="luna-metric-val">{total_milk} <span style="font-size:0.9rem; color:#8C7B7B;">ml</span></div>
            <div class="luna-metric-lbl">{date_display}</div>
        </div>
        """, unsafe_allow_html=True)

    with m_col2:
        st.markdown(f"""
        <div class="luna-card-mint">
            <div class="luna-header" style="color: #2E8B75;">💩 うんち回数</div>
            <div class="luna-metric-val" style="color: #2E8B75;">{poop_count} <span style="font-size:0.9rem; color:#5C9E8E;">回</span></div>
            <div class="luna-metric-lbl" style="color: #5C9E8E;">{date_display}</div>
        </div>
        """, unsafe_allow_html=True)

    # 1日の時間別グラフ (例：きょうの時間別授乳グラフ (9/26(土)))
    st.markdown('<div class="luna-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="luna-header">📊 きょうの時間別授乳グラフ ({formatted_short_date})</div>', unsafe_allow_html=True)

    full_hours = pd.DataFrame({"hour": list(range(24))})
    hourly_summary = day_data.groupby("hour")["milk_ml"].sum().reset_index()
    chart_data = pd.merge(full_hours, hourly_summary, on="hour", how="left").fillna(0)

    chart_data["hour_label"] = chart_data["hour"].apply(lambda x: f"{x:02d}:00")
    chart_data["text_label"] = chart_data["milk_ml"].apply(lambda x: f"{int(x)}ml" if x > 0 else "")

    fig = px.bar(
        chart_data,
        x="milk_ml",
        y="hour_label",
        orientation="h",
        labels={"milk_ml": "ミルク (ml)", "hour_label": "時間"},
        text="text_label",
        color="milk_ml",
        color_continuous_scale=["#FFEBF0", "#FF8A9E", "#FF5A79"]
    )

    fig.update_layout(
        yaxis=dict(autorange="reversed", tickfont=dict(color="#665555", size=10)),
        xaxis=dict(tickfont=dict(color="#665555", size=10)),
        height=450,
        margin=dict(l=0, r=15, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
    )

    fig.update_traces(
        textposition="outside",
        textfont=dict(color="#FF5A79", size=11),
        cliponaxis=False,
        marker=dict(line=dict(color="#FF8A9E", width=1))
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # タイムラインカード
    st.markdown('<div class="luna-card">', unsafe_allow_html=True)
    st.markdown('<div class="luna-header">🕒 本日のタイムライン</div>', unsafe_allow_html=True)

    sorted_day_data = day_data.sort_values("time_str")

    for idx, row in sorted_day_data.iterrows():
        milk_txt = f"{row['milk_ml']}ml" if row["milk_ml"] > 0 else "なし"
        poop_txt = f"{row['poop_size']}" if row["poop_size"] != "なし" else "なし"
        memo_txt = row["memo"] if pd.notna(row["memo"]) and str(row["memo"]).strip() != "" else "メモなし"

        col_text, col_btn = st.columns([8.5, 1.5])

        with col_text:
            st.markdown(f"""
            <div class="timeline-card">
                <div class="timeline-time">⏰ {row['time_str']}</div>
                <div style="margin-top: 6px;">
                    <span class="timeline-badge">🍼 ミルク: <b>{milk_txt}</b></span>
                    <span class="timeline-badge">💩 うんち: <b>{poop_txt}</b></span>
                </div>
                <div style="font-size: 0.8rem; color: #776666; margin-top: 6px; padding-left: 2px;">
                    💬 {memo_txt}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_btn:
            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️", key=f"del_{idx}"):
                df = df.drop(idx)
                save_data(df)
                st.toast(f"{row['time_str']} の記録を削除しました")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div class="luna-card" style="text-align: center; padding: 25px 15px;">
        <div style="font-size: 2.0rem; margin-bottom: 6px;">🌸</div>
        <div style="font-weight: bold; font-size: 1.0rem; color: #FF5A79;">{date_display} の記録はまだありません</div>
        <div style="color: #9E8B8B; font-size: 0.8rem; margin-top: 4px;">上のフォームから記録をつけると、ここにサマリーとタイムラインが表示されます</div>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# 5. カレンダー表示 (例：📅 9月ミルクカレンダー)
# --------------------------------------------------
st.markdown('<div class="luna-card">', unsafe_allow_html=True)

year = selected_date.year
month = selected_date.month

# 具体的な月（例：9月）を入れたタイトルに変更
st.markdown(f'<div class="luna-header">📅 {month}月ミルクカレンダー</div>', unsafe_allow_html=True)

if not df.empty:
    df["date_dt"] = pd.to_datetime(df["date"])
    monthly_df = df[(df["date_dt"].dt.year == year) & (df["date_dt"].dt.month == month)]
    daily_milk = monthly_df.groupby("date")["milk_ml"].sum().to_dict()
else:
    daily_milk = {}

max_monthly_milk = max(daily_milk.values()) if daily_milk and max(daily_milk.values()) > 0 else 800

cal = calendar.monthcalendar(year, month)
weekdays = ["月", "火", "水", "木", "金", "土", "日"]

# 曜日ヘッダー
cols = st.columns(7)
for i, wd in enumerate(weekdays):
    color = "#FF5A79" if wd in ["土", "日"] else "#554848"
    cols[i].markdown(f"<div style='text-align:center; font-weight:bold; font-size:0.8rem; color:{color};'>{wd}</div>", unsafe_allow_html=True)

# カレンダーマス出力
for week in cal:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].markdown("<div class='cal-day-box' style='background-color:#FAF8F8; border:1px solid #F0EAEA;'></div>", unsafe_allow_html=True)
        else:
            d_str = f"{year}-{month:02d}-{day:02d}"
            milk_val = daily_milk.get(d_str, 0)

            bar_percent = min(100, int((milk_val / max_monthly_milk) * 100)) if milk_val > 0 else 0
            is_today = (d_str == today_date.strftime("%Y-%m-%d"))

            bg_style = "background-color: #FFF0F3; border: 1.5px solid #FF5A79;" if is_today else ""

            if milk_val > 0:
                inner_html = f"<div class='cal-day-num'>{day}</div><div class='cal-milk-val'>{milk_val}ml</div><div class='cal-bar-container'><div class='cal-bar-fill' style='height: {bar_percent}%;'></div></div>"
            else:
                inner_html = f"<div class='cal-day-num'>{day}</div><div style='font-size:0.6rem; color:#DDD;'>-</div><div class='cal-bar-container' style='background-color:transparent;'></div>"

            cols[i].markdown(f"<div class='cal-day-box' style='{bg_style}'>{inner_html}</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
