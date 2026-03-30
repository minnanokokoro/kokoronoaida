import streamlit as st
from groq import Groq
import json
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="こころのあいだ", page_icon="🧡", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #FDFBF7; }
    .stButton>button { border-radius: 20px; background-color: #4A4A4A; color: white; }
    .post-card { background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #E0E0E0; margin-bottom: 15px; }
    .chat-user { background-color: #F0F0F0; padding: 12px 16px; border-radius: 15px 15px 4px 15px; margin: 8px 0; text-align: right; }
    .chat-ai { background-color: #FFF3E8; padding: 12px 16px; border-radius: 15px 15px 15px 4px; margin: 8px 0; border-left: 3px solid #FFA07A; }
    </style>
    """, unsafe_allow_html=True)

# --- API設定 ---
if "GROQ_API_KEY" not in st.secrets:
    st.warning("APIキーが設定されていません。SecretsにGROQ_API_KEYを設定してください。")

# --- データ管理 ---
if "posts" not in st.session_state:
    st.session_state.posts = [
        {
            "id": "1",
            "title": "進路について言い合ってしまった",
            "position": "子ども",
            "theme": "受験・進路",
            "whatHappened": "美大に行きたいと伝えたら否定された。就職はどうするの？と聞かれて悲しかった。",
            "howFelt": "自分の夢を否定されたように感じて、とても悲しかったです。",
            "tags": ["理解されない", "期待"],
            "createdAt": "2026-03-27"
        }
    ]

# --- 関数: AI分析 ---
def analyze_post(post):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    prompt = f"""
    以下の親子関係の悩みを分析し、日本語のJSON形式のみで出力してください。
    前置きや説明文は一切不要です。JSONだけを返してください。

    立場: {post['position']}
    テーマ: {post['theme']}
    内容: {post['whatHappened']}
    感情: {post['howFelt']}

    以下のキーを持つJSONを返してください（日本語で回答）:
    {{
      "overview": "この投稿の整理",
      "hidden_feelings": "表面には見えない奥にある気持ち",
      "parent_perspective": "親の立場から見た視点とアドバイス",
      "child_perspective": "子の立場から見た視点とアドバイス",
      "actionable_hints": ["ヒント1", "ヒント2", "ヒント3"]
    }}
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "あなたは親子関係の悩みに寄り添うカウンセラーです。必ずJSON形式のみで回答してください。"},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# --- 関数: AIチャット返答 ---
def chat_with_ai(post, analysis, chat_history, user_message):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    system_prompt = f"""
あなたは親子関係の悩みに深く寄り添う、温かいカウンセラーです。
以下の3つの役割を大切にしてください：

1. 【具体的なアドバイス】 抽象的な言葉ではなく、実際に使える言葉や行動を提案する
2. 【次のアクションを一緒に考える】 「次に何ができそうか」を相手と一緒に考える姿勢を持つ
3. 【相手の気持ちを代弁する】 親/子どもの立場から見た気持ちを丁寧に言語化して伝える

【この投稿の背景情報】
- 立場: {post['position']}
- テーマ: {post['theme']}
- 何があったか: {post['whatHappened']}
- どう感じたか: {post['howFelt']}

【すでに行ったAI分析の結果】
- 整理: {analysis.get('overview', '')}
- 隠れた気持ち: {analysis.get('hidden_feelings', '')}
- 親の視点: {analysis.get('parent_perspective', '')}
- 子の視点: {analysis.get('child_perspective', '')}

この背景をふまえて、ユーザーの言葉に丁寧に応答してください。
返答は200〜300文字程度の自然な日本語で、押しつけがましくなく、温かいトーンで。
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# --- 画面遷移制御 ---
if "view" not in st.session_state:
    st.session_state.view = "home"

# --- 画面: ホーム ---
if st.session_state.view == "home":
    st.title("🧡 こころのあいだ")
    st.caption("こころのあいだを、ことばにする。")

    if st.button("＋ こころを書き出す"):
        st.session_state.view = "create"
        st.rerun()

    st.write("---")
    for post in st.session_state.posts:
        with st.container():
            st.markdown(f"""
            <div class="post-card">
                <h3 style="margin-top:0;">{post['title']}</h3>
                <p style="color:gray; font-size:0.9em;">{post['position']} | {post['theme']}</p>
                <p>{post['whatHappened'][:50]}...</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("詳細・AI分析を見る", key=post['id']):
                st.session_state.selected_post = post
                st.session_state.analysis_result = None
                st.session_state.chat_history = []
                st.session_state.view = "detail"
                st.rerun()

# --- 画面: 新規投稿 ---
elif st.session_state.view == "create":
    st.header("こころを書き出す")
    with st.form("post_form"):
        title = st.text_input("タイトル（任意）")
        position = st.selectbox("あなたの立場", ["親", "子ども"])
        theme = st.selectbox("テーマ", ["親子関係", "子育て", "受験・進路"])
        happened = st.text_area("何がありましたか？（事実）")
        felt = st.text_area("どう感じましたか？（感情）")

        submitted = st.form_submit_button("静かに投稿する")
        if submitted:
            new_post = {
                "id": str(datetime.now().timestamp()),
                "title": title if title else "名もなき感情",
                "position": position,
                "theme": theme,
                "whatHappened": happened,
                "howFelt": felt,
                "createdAt": str(datetime.now().date())
            }
            st.session_state.posts.insert(0, new_post)
            st.session_state.view = "home"
            st.rerun()

    if st.button("キャンセルして戻る"):
        st.session_state.view = "home"
        st.rerun()

# --- 画面: 詳細・分析・チャット ---
elif st.session_state.view == "detail":
    post = st.session_state.selected_post

    if st.button("← 一覧へ戻る"):
        st.session_state.view = "home"
        st.rerun()

    st.markdown(f"## {post['title']}")
    st.info(f"**立場:** {post['position']} / **テーマ:** {post['theme']}")
    st.write(f"**【何があったか】**\n{post['whatHappened']}")
    st.write(f"**【どう感じたか】**\n{post['howFelt']}")

    st.write("---")

    # --- AI分析セクション ---
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.session_state.analysis_result is None:
        if st.button("✨ AIと見つめ直す"):
            if "GROQ_API_KEY" not in st.secrets:
                st.error("APIキーが設定されていないため、AI機能を使えません。")
            else:
                with st.spinner("言葉を紡いでいます..."):
                    result = analyze_post(post)
                    if "error" in result:
                        st.error(f"分析に失敗しました: {result['error']}")
                    else:
                        st.session_state.analysis_result = result
                        # 最初のAIメッセージをチャット履歴に追加
                        st.session_state.chat_history = [{
                            "role": "assistant",
                            "content": "分析が終わりました。気になること、もっと深めたいこと、何でも話しかけてみてください。一緒に考えます🧡"
                        }]
                        st.rerun()

    # --- 分析結果の表示 ---
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result

        st.success("分析が完了しました")
        st.markdown(f"### 🔍 投稿の整理\n{result.get('overview', '')}")
        st.markdown(f"### 🧡 見えてくる気持ち\n{result.get('hidden_feelings', '')}")

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**親の視点から**\n\n{result.get('parent_perspective', '')}")
        with col2:
            st.success(f"**子の視点から**\n\n{result.get('child_perspective', '')}")

        st.warning("### 💡 関係をよくするヒント")
        for hint in result.get('actionable_hints', []):
            st.write(f"- {hint}")

        # --- チャットセクション ---
        st.write("---")
        st.markdown("### 💬 AIとさらに話してみる")
        st.caption("気持ちを深堀りしたり、具体的なアドバイスを聞いたり、自由に話しかけてください。")

        # チャット履歴の表示
        for msg in st.session_state.chat_history:
            if msg["role"] == "assistant":
                st.markdown(f'<div class="chat-ai">🧡 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)

        # 入力フォーム
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input("メッセージを入力...", placeholder="例：相手にどう伝えればいいですか？")
            send = st.form_submit_button("送る")

            if send and user_input.strip():
                with st.spinner("考えています..."):
                    ai_response = chat_with_ai(
                        post,
                        result,
                        st.session_state.chat_history,
                        user_input
                    )
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    st.rerun()
