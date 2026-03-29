import streamlit as st
import google.generativeai as genai

# --- ページ設定とデザイン ---
st.set_page_config(
    page_title="こころのあいだ",
    page_icon="🤍",
    layout="centered"
)

# カスタムCSSで「こころのあいだ」のやさしい雰囲気を再現
st.markdown("""
<style>
    .stApp {
        background-color: #FDFBF7;
        color: #57534e;
    }
    .stChatFloatingInputContainer {
        background-color: #FDFBF7;
    }
    h1, h2, h3 {
        color: #57534e !important;
    }
    /* AIのメッセージ背景を少しやさしい色に */
    .stChatMessage[data-testid="chatAvatarIcon-assistant"] {
        background-color: #fcf8f2;
        border: 1px solid #ffedd5;
        border-radius: 16px;
    }
</style>
""", unsafe_allow_html=True)

st.title("こころのあいだ")
st.caption("こころのあいだを、ことばにする。親子関係の悩みを、AIと一緒に見つめ直す場所です。")

# --- APIキーの設定 ---
# st.secrets から安全にAPIキーを取得します
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("【設定エラー】APIキーが見つかりません。Streamlit CloudのSecrets設定を確認してください。")
    st.stop()

genai.configure(api_key=api_key)

# --- AIモデルの初期化とシステムプロンプト設定 ---
system_instruction = """あなたは親子関係の悩みに寄り添う、関係の背景を読み解くAIアシスタント「こころのあいだ」です。
以下のルールとトーンを厳守してユーザーと対話してください。

【AIの基本トーン】
・やさしい、落ち着いている、否定しない、決めつけない
・どちらか一方を悪者にせず、可能性として整理する
・説教せず、カウンセラーのように穏やかに言語化する

【重要ルール】
・ユーザーの話を否定せず、まずは感情を受け止めること
・親の立場、子どもの立場の両方の視点を優しく提示すること
・今日からできる小さくて現実的な関わり方のヒントを提案すること
・長すぎる返答は避け、対話を通じて少しずつ整理していくこと
"""

# Geminiモデルの設定
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash-preview-09-2025",
    system_instruction=system_instruction
)

# --- チャット履歴の初期化 ---
if "chat_session" not in st.session_state:
    # 新しいチャットセッションを開始
    st.session_state.chat_session = model.start_chat(history=[])
    
    # AIからの最初の挨拶を履歴に追加
    initial_message = "こんにちは。ここは親と子のあいだにある、言葉にできない気持ちを整理する場所です。今日あったことや、心の中にあるモヤモヤを、そのまま教えていただけますか？"
    st.session_state.messages = [{"role": "assistant", "content": initial_message}]

# --- 過去のメッセージを表示 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- ユーザー入力とAIの応答処理 ---
if prompt := st.chat_input("いまの気持ちや、あったことを書いてみてください"):
    # ユーザーの入力を画面に表示して履歴に保存
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AIの応答を生成
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        # ローディング表示の代わり
        with st.spinner("言葉を紡いでいます..."):
            try:
                # APIにメッセージを送信し、応答を受け取る
                response = st.session_state.chat_session.send_message(prompt)
                full_response = response.text
                
                # 応答を表示して履歴に保存
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")