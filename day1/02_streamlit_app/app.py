# app.py
import streamlit as st
import ui                   # UIモジュール
import llm                  # LLMモジュール
import database             # データベースモジュール
import metrics              # 評価指標モジュール
import data                 # データモジュール
import torch
from transformers import pipeline
from config import MODELS, DEFAULT_MODEL
from huggingface_hub import HfFolder

# --- アプリケーション設定 ---
st.set_page_config(page_title="Gemma Chatbot", layout="wide")

# --- 初期化処理 ---
# NLTKデータのダウンロード（初回起動時など）
metrics.initialize_nltk()

# データベースの初期化（テーブルが存在しない場合、作成）
database.init_db()

# データベースが空ならサンプルデータを投入
data.ensure_initial_data()

# モデル選択
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = DEFAULT_MODEL

# サイドバーにモデル選択UIを追加
st.sidebar.title("モデル設定")
model_options = list(MODELS.keys())
model_descriptions = [MODELS[m]["description"] for m in model_options]
selected_model = st.sidebar.selectbox(
    "使用するモデルを選択",
    options=model_options,
    format_func=lambda x: f"{x} - {MODELS[x]['description']}",
    key="model_selector"
)

# モデルが変更された場合、キャッシュをクリアして再ロード
if selected_model != st.session_state.selected_model:
    st.session_state.selected_model = selected_model
    st.cache_resource.clear()

pipe = llm.load_model(st.session_state.selected_model)

# --- Streamlit アプリケーション ---
st.title("🤖 Gemma Chatbot with Feedback")
st.write("Gemmaモデルを使用したチャットボットです。回答に対してフィードバックを行えます。")
st.markdown("---")

# --- サイドバー ---
st.sidebar.title("ナビゲーション")
# セッション状態を使用して選択ページを保持
if 'page' not in st.session_state:
    st.session_state.page = "チャット" # デフォルトページ

page = st.sidebar.radio(
    "ページ選択",
    ["チャット", "履歴閲覧", "サンプルデータ管理"],
    key="page_selector",
    index=["チャット", "履歴閲覧", "サンプルデータ管理"].index(st.session_state.page), # 現在のページを選択状態にする
    on_change=lambda: setattr(st.session_state, 'page', st.session_state.page_selector) # 選択変更時に状態を更新
)


# --- メインコンテンツ ---
if st.session_state.page == "チャット":
    if pipe:
        ui.display_chat_page(pipe)
    else:
        st.error("チャット機能を利用できません。モデルの読み込みに失敗しました。")
elif st.session_state.page == "履歴閲覧":
    ui.display_history_page()
elif st.session_state.page == "サンプルデータ管理":
    ui.display_data_page()

# --- フッターなど（任意） ---
st.sidebar.markdown("---")
st.sidebar.info("開発者: [Your Name]")