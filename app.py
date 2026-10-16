import calendar
import datetime
import json
import zoneinfo
import pandas as pd
import plotly.express as px
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --------------------------------------------------
# 1. ページ基本設定 & タイムゾーン設定
# --------------------------------------------------
st.set_page_config(
    page_title="芳怜ちゃん育児記録",
    page_icon="🌸",
    layout="centered"
)

# 常に日本時間（Asia/Tokyo）の現在日付を取得
JST = zoneinfo.ZoneInfo("Asia/Tokyo")
now_jst = datetime.datetime.now(JST)
today_date = now_jst.date()

# --------------------------------------------------
# 日付またぎ・バックグラウンド復帰対策（自動リフレッシュ）
# --------------------------------------------------
if "last_loaded_date" not in st.session_state or st.session_state["last_loaded_date"] != today_date:
    st.session_state["last_loaded_date"] = today_date
    if "df_master" in st.session_state:
        del st.session_state["df_master"]
    st.cache_data.clear()

# --------------------------------------------------
# カスタムCSS
# --------------------------------------------------
st.markdown("""
<style>
    .main {
        background-color: #FFF8F9;
        font-family: -apple-system, BlinkMacSystemFont, "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Meiryo", sans-serif;
        color: #554848;
        padding-left: 0.3rem !important;
        padding-right: 0.3rem !important;
    }
    .luna-title-container {
        text-align: center;
        padding: 10px 0 15px 0;
        margin-bottom: 15px;
    }
    .luna-title {
        color: #FF5A79;
        font-size: 1.5rem;
        font-weight: bold;
        letter-spacing: 0.5px;
    }
    .luna-subtitle {
        color: #9E8B8B;
        font-size: 0.8rem;
        margin-top: 2px;
    }
    .luna-card {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 14px 10px;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(255, 138, 158, 0.08);
        border: 1px solid #FFEBEF;
    }
    .luna-card-highlight {
        background: linear-gradient(135deg, #FFF0F3 0%, #FFE1E8 100%);
        border-radius: 20px;
        padding: 14px 16px;
        margin-bottom: 16px;
        border: 1px solid #FFCCD5;
        box-shadow: 0 4px 14px rgba(255, 90, 121, 0.12);
    }
    .luna-card-mint {
        background-color: #F2FAF7;
        border-radius: 20px;
        padding: 14px 10px;
        margin-bottom: 16px;
        border: 1px solid #D5F0E6;
    }
    .luna-header {
        font-size: 1.0rem;
        font-weight: bold;
        color: #FF5A79;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .luna-metric-val {
        font-size: 1.8rem;
        font-weight: bold;
        color: #FF5A79;
    }
    .luna-metric-lbl {
        font-size: 0.75rem;
        color: #8C7B7B;
    }
    .timeline-card {
        background-color: #FFF5F7;
        border-left: 5px solid #FF5A79;
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 10px;
    }
    .timeline-time {
        font-size: 0.95rem;
        font-weight: bold;
        color: #FF5A79;
    }
    .timeline-badge {
        display: inline-block;
        background-color: #FFFFFF;
        border: 1px solid #FFD2DC;
        border-radius: 12px;
        padding: 2px 6px;
        font-size: 0.75rem;
        margin-right: 4px;
        color: #554848;
    }
    .cal-grid-container {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 3px;
        width: 100%;
        margin-top: 8px;
    }
    .cal-header-cell {
        text-align: center;
        font-weight: bold;
        font-size: 0.75rem;
        padding: 4px 0;
    }
    .cal-day-cell {
        background-color: #FFFFFF;
        border: 1px solid #FFE1E8;
        border-radius: 8px;
        padding: 3px 0px 0px 0px;
        text-align: center;
        min-height: 76px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        box-sizing: border-box;
        overflow: hidden;
    }
    .cal-day-cell-empty {
        background-color: #FAF8F8;
        border: 1px solid #F2EDED;
        border-radius: 8px;
        min-height: 76px;
    }
    .cal-day-num {
        font-size: 0.7rem;
        color: #8C7B7B;
        font-weight: bold;
        line-height: 1.0;
    }
    .cal-milk-val {
        font-size: 0.7rem;
        font-weight: bold;
        color: #FF5A79;
        margin-top: 1px;
        line-height: 1.1;
    }
    .cal-bar-container {
        background-color: #FFEBF0;
        border-radius: 0 0 6px 6px;
        height: 18px;
        width: 100%;
        margin: 2px 0 0 0;
        display: flex;
        align-items: flex-end;
        overflow: hidden;
    }
    .cal-bar-fill {
        background: linear-gradient(0deg, #FF8A9E 0%, #FF5A79 100%);
        width: 100%;
        border-radius: 0;
    }
    .stButton > button {
        border-radius: 25px !important;
        background: linear-gradient(135deg, #FF8A9E 0%, #FF5A79 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 0.9rem !important;
        padding: 6px 10px !important;
        box-shadow: 0 4px 12px rgba(255, 90, 121, 0.2) !important;
        width: 100%;
    }
    div[data-baseweb="input"], div[data-baseweb="select"] {
        border-radius: 14px !important;
        border-color: #FFD2DC !important;
    }
</style>
""", unsafe_allow_html=True)

# ヘッダー
st.markdown("""
<div class="luna-title-container">
    <div class="luna-title">🌸 芳怜ちゃん育児記録</div>
    <div class="luna-subtitle">毎日のすくすく成長記録</div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 2. Googleスプレッドシート接続＆データ操作処理
# --------------------------------------------------
@st.cache_resource
def get_gspread_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    info = json.loads(st.secrets["gcp_service_account"]["json_text"])
    credentials = Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(credentials)


def get_worksheet():
    gc = get_gspread_client()
    spreadsheet_name = st.secrets["spreadsheet"]["spreadsheet_name"]
    sh = gc.open(spreadsheet_name)
    return sh.sheet1


@st.cache_data(ttl=300)
def fetch_data_from_sheet():
    try:
        ws = get_worksheet()
        values = ws.get_all_values()
        
        if len(values) <= 1:
            return pd.DataFrame(columns=["date", "hour", "time_str", "milk_ml", "poop_size", "memo"])
        
        df = pd.DataFrame(values[1:], columns=values[0])
        df["hour"] = pd.to_numeric(df["hour"], errors="coerce").fillna(0).astype(int)
        df["milk_ml"] = pd.to_numeric(df["milk_ml"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        st.error(f"スプレッドシート読み込みエラー: {e}")
        return pd.DataFrame(columns=["date", "hour", "time_str", "milk_ml", "poop_size", "memo"])


def load_data():
    if "df_master" not in st.session_state:
        st.session_state["df_master"] = fetch_data_from_sheet()
    return st.session_state["df_master"]


def append_row(new_row):
    try:
        ws = get_worksheet()
        ws.append_row([
            new_row["date"],
            int(new_row["hour"]),
            new_row["time_str"],
            int(new_row["milk_ml"]),
            new_row["poop_size"],
            new_row["memo"]
        ])
        
        new_df = pd.DataFrame([new_row])
        st.session_state["df_master"] = pd.concat([st.session_state["df_master"], new_df], ignore_index=True)
        fetch_data_from_sheet.clear()
    except Exception as e:
        st.error(f"書き込みエラー: {e}")


def delete_single_row(target_row_dict):
    try:
        ws = get_worksheet()
        records = ws.get_all_records()
        
        for idx, row in enumerate
