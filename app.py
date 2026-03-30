import streamlit as st
from groq import Groq
import json
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="こころのあいだ", page_icon="🧡", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;500&display=swap');

    .main { background-color: #FAF7F2; }
    section[data-testid="stSidebar"] { background-color: #FAF7F2; }

    .stButton>button {
        border-radius: 20px;
        background-color: #E8A87C;
        color: #4A2C1A;
        border: none;
        font-weight: 500;
        padding: 6px 20px;
    }
    .stButton>button:hover {
        background-color: #D9956A;
        color: #4A2C1A;
        border: none;
    }

    .app-title {
        font-family: 'Noto Serif JP', Georgia, serif;
        font-size: 28px;
        font-weight: 500;
        color: #3D2B1F;
    }
    .app-caption {
        font-size: 13px;
        color: #9C7B6A;
        margin-top: -8px;
        margin-bottom: 16px;
    }
    .divider {
        border: none;
        border-top: 1px dashed #D9C4B0;
        margin: 16px 0;
    }

    .post-card {
        background-color: #FFFDF8;
        border: 1.5px solid #E8D8C4;
        border-left: 4px solid #E8A87C;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
    }
    .post-card-title {
        font-family: 'Noto Serif JP', Georgia, serif;
        font-size: 15px;
        font-weight: 500;
        color: #3D2B1F;
        margin-bottom: 6px;
    }
    .post-card-meta {
        font-size: 12px;
        color: #B07050;
        margin-bottom: 8px;
    }
    .post-card-body {
        font-size: 13px;
        color: #6B5043;
        line-height: 1.7;
        margin-bottom: 10px;
    }
    .badge-position {
        display: inline-block;
        font-size: 11px;
        background: #FAF0E8;
        color: #B07050;
        padding: 3px 10px;
        border-radius: 20px;
        margin-left: 6px;
        vertical-align: middle;
    }
    .badge-anon {
        display: inline-block;
        font-size: 11px;
        background: #F0F0F0;
        color: #888;
        padding: 3px 10px;
        border-radius: 20px;
        margin-left: 6px;
        vertical-align: middle;
    }
    .tag-pill {
        display: inline-block;
        font-size: 11px;
        background: #FDE8D8;
        color: #993C1D;
        padding: 3px 10px;
        border-radius: 20px;
        margin-right: 4px;
        margin-bottom: 4px;
    }
    .section-header {
        font-family: 'Noto Serif JP', Georgia, serif;
        font-size: 18px;
        font-weight: 500;
        color: #3D2B1F;
        margin-bottom: 12px;
    }
    .chat-user {
        background-color: #F5EDE4;
        padding: 12px 16px;
        border-radius: 15px 15px 4px 15px;
        margin: 8px 0;
        text-align: right;
        color: #4A2C1A;
        font-size: 14px;
    }
    .chat-ai {
        background-color: #FFFDF8;
        padding: 12px 16px;
        border-radius: 15px 15px 15px 4px;
        margin: 8px 0;
        border-left: 3px solid #E8A87C;
        color: #4A2C1A;
        font-size: 14px;
    }
    .theme-icon { margin-right: 4px; }
    </style>
    """, unsafe_allow_html=True)

# --- テーマアイコン ---
THEME_ICONS = {
    "親子関係": "💬",
    "子育て": "🌱",
    "受験・進路": "📖"
}

# --- API設定 ---
if "GROQ_API_KEY" not in st.secrets:
    st.warning("APIキーが設定されていません。SecretsにGROQ_API_KEYを設定してください。")

# --- データ管理 ---
if "posts" not in st.session_state:
    st.session_state.posts = [
        {
            "id": "1",
            "title": "進路について言い合ってしまった",
            "author": "",
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

# --- カードのHTML生成 ---
def render_post_card(post):
    icon = THEME_ICONS.get(post['theme'], '📝')
    tags_html = ''.join([f'<span class="tag-pill">#{t}</span>' for t in post.get('tags', [])])
    anon_badge = '<span class="badge-anon">匿名</span>' if post.get('isAnonymous') else ''
    author_text = f'<span style="font-size:12px;color:#9C7B6A;margin-left:4px;">{post.get("author","")}</span>' if post.get("author") and not post.get("isAnonymous") else ''
    position_badge = f'<span class="badge-position">{post["position"]}</span>'
    preview = post['whatHappened'][:45] + '...' if len(post['whatHappened']) > 45 else post['whatHappened']

    return f"""
    <div class="post-card">
        <div class="post-card-title">
            {post['title']}{anon_badge}{author_text}{position_badge}
        </div>
        <div class="post-card-meta">
            <span>{icon} {post['theme']}</span>
            &nbsp;·&nbsp;
            <span>{post['createdAt']}</span>
        </div>
        <div class="post-card-body">{preview}</div>
        {f'<div style="margin-bottom:10px;">{tags_html}</div>' if tags_html else ''}
    </div>
    """

# --- 画面遷移制御 ---
if "view" not in st.session_state:
    st.session_state.view = "home"

# =============================
# 画面: ホーム
# =============================
if st.session_state.view == "home":
    st.markdown('<div class="app-title">🧡 こころのあいだ</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-caption">こころのあいだを、ことばにする。</div>', unsafe_allow_html=True)

    if st.button("＋ こころを書き出す"):
        st.session_state.view = "create"
        st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    for post in st.session_state.posts:
        st.markdown(render_post_card(post), unsafe_allow_html=True)
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            if st.button("✨ AI分析を見る", key=f"detail_{post['id']}"):
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
        st.markdown('<div style="margin-bottom:8px;"></div>', unsafe_allow_html=True)

# =============================
# 画面: 新規投稿
# =============================
elif st.session_state.view == "create":
    st.markdown('<div class="section-header">🖊️ こころを書き出す</div>', unsafe_allow_html=True)
    st.caption("思いつくままに、ゆっくり書いてみてください。")

    with st.form("post_form"):
        title = st.text_input("タイトル（任意）")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        col_name, col_anon = st.columns([3, 1])
        with col_name:
            author = st.text_input("お名前（任意）", placeholder="例：Sachi")
        with col_anon:
            st.write("")
            st.write("")
            is_anonymous = st.checkbox("匿名にする")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        position = st.selectbox("あなたの立場", ["親", "子ども"])
        theme = st.selectbox("テーマ", ["親子関係", "子育て", "受験・進路"])

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        happened = st.text_area("何がありましたか？（事実）", placeholder="どんなことが起きたか、できるだけ具体的に。")
        felt = st.text_area("どう感じましたか？（感情）", placeholder="そのとき、どんな気持ちになりましたか？")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.caption("もう少し深く教えてください（任意）")
        really_wanted = st.text_area("本当はどうしてほしかったですか？", placeholder="例：ただ話を聞いてほしかった、認めてほしかった…")
        hardest_moment = st.text_area("一番つらかった瞬間はどこですか？", placeholder="例：○○と言われたとき、無視されたとき…")

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
                "tags": [],
                "createdAt": str(datetime.now().date())
            }
            st.session_state.posts.insert(0, new_post)
            st.session_state.view = "home"
            st.rerun()

    if st.button("← キャンセルして戻る"):
        st.session_state.view = "home"
        st.rerun()

# =============================
# 画面: 編集
# =============================
elif st.session_state.view == "edit":
    post = st.session_state.selected_post
    st.markdown('<div class="section-header">✏️ 投稿を編集する</div>', unsafe_allow_html=True)

    with st.form("edit_form"):
        title = st.text_input("タイトル", value=post['title'])

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        col_name, col_anon = st.columns([3, 1])
        with col_name:
            author = st.text_input("お名前（任意）", value=post.get('author', ''))
        with col_anon:
            st.write("")
            st.write("")
            is_anonymous = st.checkbox("匿名にする", value=post.get('isAnonymous', False))

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        position = st.selectbox("あなたの立場", ["親", "子ども"],
            index=["親", "子ども"].index(post['position']))
        theme = st.selectbox("テーマ", ["親子関係", "子育て", "受験・進路"],
            index=["親子関係", "子育て", "受験・進路"].index(post['theme']))

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        happened = st.text_area("何がありましたか？（事実）", value=post['whatHappened'])
        felt = st.text_area("どう感じましたか？（感情）", value=post['howFelt'])

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
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

    if st.button("← キャンセルして戻る"):
        st.session_state.view = "home"
        st.rerun()

# =============================
# 画面: 削除確認
# =============================
elif st.session_state.view == "confirm_delete":
    target_id = st.session_state.get("delete_target_id")
    target_post = next((p for p in st.session_state.posts if p['id'] == target_id), None)

    st.markdown('<div class="section-header">🗑️ 投稿を削除しますか？</div>', unsafe_allow_html=True)
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

    icon = THEME_ICONS.get(post['theme'], '📝')
    anon_badge = '<span class="badge-anon">匿名</span>' if post.get('isAnonymous') else ''
    author_text = f'<span style="font-size:12px;color:#9C7B6A;margin-left:4px;">{post.get("author","")}</span>' if post.get("author") and not post.get("isAnonymous") else ''

    st.markdown(f'<div class="section-header">{post["title"]}{anon_badge}{author_text}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:13px;color:#B07050;margin-bottom:12px;">{icon} {post["theme"]} &nbsp;·&nbsp; {post["position"]} &nbsp;·&nbsp; {post["createdAt"]}</div>', unsafe_allow_html=True)

    st.markdown(f'<div style="background:#FFFDF8;border:1.5px solid #E8D8C4;border-left:4px solid #E8A87C;border-radius:12px;padding:16px;margin-bottom:10px;"><div style="font-size:12px;color:#9C7B6A;margin-bottom:4px;">何があったか</div><div style="font-size:14px;color:#3D2B1F;line-height:1.7;">{post["whatHappened"]}</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:#FFFDF8;border:1.5px solid #E8D8C4;border-left:4px solid #C4A882;border-radius:12px;padding:16px;margin-bottom:10px;"><div style="font-size:12px;color:#9C7B6A;margin-bottom:4px;">どう感じたか</div><div style="font-size:14px;color:#3D2B1F;line-height:1.7;">{post["howFelt"]}</div></div>', unsafe_allow_html=True)

    if post.get('reallyWanted'):
        st.markdown(f'<div style="background:#FFFDF8;border:1.5px solid #E8D8C4;border-left:4px solid #D9B8A0;border-radius:12px;padding:16px;margin-bottom:10px;"><div style="font-size:12px;color:#9C7B6A;margin-bottom:4px;">本当はどうしてほしかったか</div><div style="font-size:14px;color:#3D2B1F;line-height:1.7;">{post["reallyWanted"]}</div></div>', unsafe_allow_html=True)
    if post.get('hardestMoment'):
        st.markdown(f'<div style="background:#FFFDF8;border:1.5px solid #E8D8C4;border-left:4px solid #D9B8A0;border-radius:12px;padding:16px;margin-bottom:10px;"><div style="font-size:12px;color:#9C7B6A;margin-bottom:4px;">一番つらかった瞬間</div><div style="font-size:14px;color:#3D2B1F;line-height:1.7;">{post["hardestMoment"]}</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

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

        st.markdown(f'<div style="background:#FFFDF8;border:1.5px solid #E8D8C4;border-radius:12px;padding:16px;margin-bottom:10px;"><div style="font-size:13px;font-weight:500;color:#3D2B1F;margin-bottom:6px;">🔍 投稿の整理</div><div style="font-size:14px;color:#4A2C1A;line-height:1.7;">{result.get("overview","")}</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="background:#FFF5EE;border:1.5px solid #F0CDB0;border-radius:12px;padding:16px;margin-bottom:10px;"><div style="font-size:13px;font-weight:500;color:#3D2B1F;margin-bottom:6px;">🧡 見えてくる気持ち</div><div style="font-size:14px;color:#4A2C1A;line-height:1.7;">{result.get("hidden_feelings","")}</div></div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div style="background:#F5F0FF;border:1.5px solid #D8C8F0;border-radius:12px;padding:16px;"><div style="font-size:12px;font-weight:500;color:#5A3E8A;margin-bottom:6px;">親の視点から</div><div style="font-size:13px;color:#3D2B5A;line-height:1.7;">{result.get("parent_perspective","")}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div style="background:#F0FFF5;border:1.5px solid #B8E8CC;border-radius:12px;padding:16px;"><div style="font-size:12px;font-weight:500;color:#2A6B4A;margin-bottom:6px;">子の視点から</div><div style="font-size:13px;color:#1A4A30;line-height:1.7;">{result.get("child_perspective","")}</div></div>', unsafe_allow_html=True)

        hints = result.get('actionable_hints', [])
        if hints:
            hints_html = ''.join([f'<div style="display:flex;gap:8px;margin-bottom:8px;"><span style="color:#E8A87C;font-weight:500;">·</span><span style="font-size:14px;color:#4A2C1A;line-height:1.7;">{h}</span></div>' for h in hints])
            st.markdown(f'<div style="background:#FFFDF8;border:1.5px solid #E8D8C4;border-radius:12px;padding:16px;margin-top:10px;"><div style="font-size:13px;font-weight:500;color:#3D2B1F;margin-bottom:10px;">💡 関係をよくするヒント</div>{hints_html}</div>', unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div style="font-size:15px;font-weight:500;color:#3D2B1F;margin-bottom:4px;">💬 AIとさらに話してみる</div>', unsafe_allow_html=True)
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
                    ai_response = chat_with_ai(post, result, st.session_state.chat_history, user_input)
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    st.rerun()
