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
    .anon-badge { display: inline-block; background-color: #F0F0F0; color: #888; font-size: 0.75em; padding: 2px 10px; border-radius: 20px; margin-left: 6px; }
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
            "author": "Sachi",
            "isAnonymous": False,
            "position": "子ども",
            "theme": "受験・進路",
            "whatHappened": "美大に行きたいと伝えたら否定された。就職はどうするの？と聞かれて悲しかった。",
            "howFelt": "自分の夢を否定されたように感じて、とても悲しかったです。",
            "reallyWanted": "ただ、応援してほしかった。",
            "hardestMoment": "「そんな夢みたいなこと」と言われた瞬間。",
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
    本当はどうしてほしかったか: {post.get('reallyWanted', '未回答')}
    一番つらかった瞬間: {post.get('hardestMoment', '未回答')}

    以下のキーを持つJSONを返してください（日本語で回答）:
    {{
      "overview": "この投稿の整理",
      "hidden_feelings": "表面には見えない奥にある気持ち（「本当はどうしてほしかったか」「一番つらかった瞬間」もふまえて深く分析する）",
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
- 本当はどうしてほしかったか: {post.get('reallyWanted', '未回答')}
- 一番つらかった瞬間: {post.get('hardestMoment', '未回答')}

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

# --- 投稿者名の表示 ---
def display_author(post):
    if post.get('isAnonymous'):
        return '<span class="anon-badge">匿名</span>'
    author = post.get('author', '')
    return f'<span style="font-size:0.85em; color:#888;">{author}</span>' if author else ''

# --- 画面遷移制御 ---
if "view" not in st.session_state:
    st.session_state.view = "home"

# =============================
# 画面: ホーム
# =============================
if st.session_state.view == "home":
    st.title("🧡 こころのあいだ")
    st.caption("こころのあいだを、ことばにする。")

    if st.button("＋ こころを書き出す"):
        st.session_state.view = "create"
        st.rerun()

    st.write("---")
    for post in st.session_state.posts:
        with st.container():
            author_html = display_author(post)
            st.markdown(f"""
            <div class="post-card">
                <h3 style="margin-top:0;">{post['title']} {author_html}</h3>
                <p style="color:gray; font-size:0.9em;">{post['position']} | {post['theme']} | {post['createdAt']}</p>
                <p>{post['whatHappened'][:50]}...</p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                if st.button("詳細・AI分析を見る", key=f"detail_{post['id']}"):
                    st.session_state.selected_post = post
                    st.session_state.analysis_result = None
                    st.session_state.chat_history = []
                    st.session_state.view = "detail"
                    st.rerun()
            with col2:
                if st.button("✏️ 編集", key=f"edit_{post['id']}"):
                    st.session_state.selected_post = post
                    st.session_state.view = "edit"
                    st.rerun()
            with col3:
                if st.button("🗑️ 削除", key=f"delete_{post['id']}"):
                    st.session_state.delete_target_id = post['id']
                    st.session_state.view = "confirm_delete"
                    st.rerun()

# =============================
# 画面: 新規投稿
# =============================
elif st.session_state.view == "create":
    st.header("こころを書き出す")
    st.caption("思いつくままに、ゆっくり書いてみてください。")

    with st.form("post_form"):
        title = st.text_input("タイトル（任意）")

        # 匿名モード設定
        st.write("---")
        col_name, col_anon = st.columns([3, 1])
        with col_name:
            author = st.text_input("お名前（任意）", placeholder="例：Sachi")
        with col_anon:
            st.write("")
            st.write("")
            is_anonymous = st.checkbox("匿名にする")

        st.write("---")
        position = st.selectbox("あなたの立場", ["親", "子ども"])
        theme = st.selectbox("テーマ", ["親子関係", "子育て", "受験・進路"])

        st.write("---")
        happened = st.text_area("何がありましたか？（事実）", placeholder="どんなことが起きたか、できるだけ具体的に。")
        felt = st.text_area("どう感じましたか？（感情）", placeholder="そのとき、どんな気持ちになりましたか？")

        st.write("---")
        st.caption("もう少し深く教えてください（任意）")
        really_wanted = st.text_area(
            "本当はどうしてほしかったですか？",
            placeholder="例：ただ話を聞いてほしかった、認めてほしかった…"
        )
        hardest_moment = st.text_area(
            "一番つらかった瞬間はどこですか？",
            placeholder="例：○○と言われたとき、無視されたとき…"
        )

        submitted = st.form_submit_button("静かに投稿する")
        if submitted:
            new_post = {
                "id": str(datetime.now().timestamp()),
                "title": title if title else "名もなき感情",
                "author": author,
                "isAnonymous": is_anonymous,
                "position": position,
                "theme": theme,
                "whatHappened": happened,
                "howFelt": felt,
                "reallyWanted": really_wanted,
                "hardestMoment": hardest_moment,
                "createdAt": str(datetime.now().date())
            }
            st.session_state.posts.insert(0, new_post)
            st.session_state.view = "home"
            st.rerun()

    if st.button("キャンセルして戻る"):
        st.session_state.view = "home"
        st.rerun()

# =============================
# 画面: 編集
# =============================
elif st.session_state.view == "edit":
    post = st.session_state.selected_post
    st.header("✏️ 投稿を編集する")

    with st.form("edit_form"):
        title = st.text_input("タイトル", value=post['title'])

        st.write("---")
        col_name, col_anon = st.columns([3, 1])
        with col_name:
            author = st.text_input("お名前（任意）", value=post.get('author', ''))
        with col_anon:
            st.write("")
            st.write("")
            is_anonymous = st.checkbox("匿名にする", value=post.get('isAnonymous', False))

        st.write("---")
        position = st.selectbox(
            "あなたの立場", ["親", "子ども"],
            index=["親", "子ども"].index(post['position'])
        )
        theme = st.selectbox(
            "テーマ", ["親子関係", "子育て", "受験・進路"],
            index=["親子関係", "子育て", "受験・進路"].index(post['theme'])
        )

        st.write("---")
        happened = st.text_area("何がありましたか？（事実）", value=post['whatHappened'])
        felt = st.text_area("どう感じましたか？（感情）", value=post['howFelt'])

        st.write("---")
        st.caption("もう少し深く教えてください（任意）")
        really_wanted = st.text_area("本当はどうしてほしかったですか？", value=post.get('reallyWanted', ''))
        hardest_moment = st.text_area("一番つらかった瞬間はどこですか？", value=post.get('hardestMoment', ''))

        submitted = st.form_submit_button("保存する")
        if submitted:
            for i, p in enumerate(st.session_state.posts):
                if p['id'] == post['id']:
                    st.session_state.posts[i] = {
                        **p,
                        "title": title if title else "名もなき感情",
                        "author": author,
                        "isAnonymous": is_anonymous,
                        "position": position,
                        "theme": theme,
                        "whatHappened": happened,
                        "howFelt": felt,
                        "reallyWanted": really_wanted,
                        "hardestMoment": hardest_moment,
                    }
                    break
            st.success("保存しました！")
            st.session_state.view = "home"
            st.rerun()

    if st.button("キャンセルして戻る"):
        st.session_state.view = "home"
        st.rerun()

# =============================
# 画面: 削除確認
# =============================
elif st.session_state.view == "confirm_delete":
    target_id = st.session_state.get("delete_target_id")
    target_post = next((p for p in st.session_state.posts if p['id'] == target_id), None)

    st.header("🗑️ 投稿を削除しますか？")
    if target_post:
        st.warning(f"「{target_post['title']}」を削除します。この操作は元に戻せません。")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("削除する", type="primary"):
            st.session_state.posts = [p for p in st.session_state.posts if p['id'] != target_id]
            st.session_state.view = "home"
            st.rerun()
    with col2:
        if st.button("キャンセル"):
            st.session_state.view = "home"
            st.rerun()

# =============================
# 画面: 詳細・分析・チャット
# =============================
elif st.session_state.view == "detail":
    post = st.session_state.selected_post

    col_back, col_edit, col_delete = st.columns([3, 1, 1])
    with col_back:
        if st.button("← 一覧へ戻る"):
            st.session_state.view = "home"
            st.rerun()
    with col_edit:
        if st.button("✏️ 編集"):
            st.session_state.view = "edit"
            st.rerun()
    with col_delete:
        if st.button("🗑️ 削除"):
            st.session_state.delete_target_id = post['id']
            st.session_state.view = "confirm_delete"
            st.rerun()

    author_html = display_author(post)
    st.markdown(f"## {post['title']} {author_html}", unsafe_allow_html=True)
    st.info(f"**立場:** {post['position']} / **テーマ:** {post['theme']}")
    st.write(f"**【何があったか】**\n{post['whatHappened']}")
    st.write(f"**【どう感じたか】**\n{post['howFelt']}")
    if post.get('reallyWanted'):
        st.write(f"**【本当はどうしてほしかったか】**\n{post['reallyWanted']}")
    if post.get('hardestMoment'):
        st.write(f"**【一番つらかった瞬間】**\n{post['hardestMoment']}")

    st.write("---")

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
                        st.session_state.chat_history = [{
                            "role": "assistant",
                            "content": "分析が終わりました。気になること、もっと深めたいこと、何でも話しかけてみてください。一緒に考えます🧡"
                        }]
                        st.rerun()

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

        st.write("---")
        st.markdown("### 💬 AIとさらに話してみる")
        st.caption("気持ちを深堀りしたり、具体的なアドバイスを聞いたり、自由に話しかけてください。")

        for msg in st.session_state.chat_history:
            if msg["role"] == "assistant":
                st.markdown(f'<div class="chat-ai">🧡 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)

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
