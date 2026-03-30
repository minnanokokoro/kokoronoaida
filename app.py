import streamlit as st
from groq import Groq
from supabase import create_client
import json
import uuid
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
        font-size: 26px;
        font-weight: 500;
        color: #3D2B1F;
        margin-bottom: 2px;
    }
    .app-caption {
        font-size: 13px;
        color: #9C7B6A;
        margin-bottom: 0px;
    }
    .divider {
        border: none;
        border-top: 1px dashed #D9C4B0;
        margin: 16px 0;
    }
    .concept-card {
        background-color: #FFFDF8;
        border: 1.5px solid #E8D8C4;
        border-radius: 14px;
        padding: 18px 20px;
        margin: 12px 0 16px 0;
    }
    .concept-title {
        font-family: 'Noto Serif JP', Georgia, serif;
        font-size: 14px;
        font-weight: 500;
        color: #3D2B1F;
        margin-bottom: 10px;
    }
    .concept-body {
        font-size: 13px;
        color: #6B5043;
        line-height: 1.85;
        margin-bottom: 14px;
    }
    .step-row {
        display: flex;
        gap: 10px;
        align-items: flex-start;
        margin-bottom: 8px;
    }
    .step-num {
        min-width: 22px;
        height: 22px;
        background: #E8A87C;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        color: #4A2C1A;
        font-weight: 500;
    }
    .step-text {
        font-size: 13px;
        color: #6B5043;
        line-height: 1.6;
        padding-top: 2px;
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
    </style>
    """, unsafe_allow_html=True)

# --- テーマアイコン ---
THEME_ICONS = {"親子関係": "💬", "子育て": "🌱", "受験・進路": "📖"}

# --- Supabase設定 ---
@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# --- 端末ID生成（LocalStorageで永続化） ---
if "device_id" not in st.session_state:
    st.session_state.device_id = str(uuid.uuid4())

device_id_js = f"""
<script>
(function() {{
    let id = localStorage.getItem('kokoro_device_id');
    if (!id) {{
        id = '{st.session_state.device_id}';
        localStorage.setItem('kokoro_device_id', id);
    }}
    // Streamlitにデバイスカスタムイベントは送れないので、hiddenフィールドで渡す
    const el = window.parent.document.querySelector('input[data-device-id]');
    if (!el) {{
        const inp = window.parent.document.createElement('input');
        inp.setAttribute('data-device-id', id);
        inp.type = 'hidden';
        window.parent.document.body.appendChild(inp);
    }}
    // セッションストレージにも保存
    sessionStorage.setItem('kokoro_device_id', id);
}})();
</script>
"""

import streamlit.components.v1 as components

if "device_id_loaded" not in st.session_state:
    stored_id = st.query_params.get("did", None)
    if stored_id:
        st.session_state.device_id = stored_id
        st.session_state.device_id_loaded = True
    else:
        st.session_state.device_id_loaded = False

components.html(f"""
<script>
(function() {{
    let id = localStorage.getItem('kokoro_device_id');
    if (!id) {{
        id = '{st.session_state.device_id}';
        localStorage.setItem('kokoro_device_id', id);
    }}
    const current = new URLSearchParams(window.parent.location.search).get('did');
    if (current !== id) {{
        const url = new URL(window.parent.location.href);
        url.searchParams.set('did', id);
        window.parent.history.replaceState(null, '', url.toString());
        window.parent.location.reload();
    }}
}})();
</script>
""", height=0)

# --- 投稿の読み込み ---
def load_posts():
    try:
        supabase = get_supabase()
        res = supabase.table("posts").select("*").order("created_at", desc=True).execute()
        posts = []
        for p in res.data:
            posts.append({
                "id": p["id"],
                "title": p["title"] or "名もなき感情",
                "author": p["author"] or "",
                "isAnonymous": p["is_anonymous"],
                "position": p["position"],
                "theme": p["theme"],
                "whatHappened": p["what_happened"],
                "howFelt": p["how_felt"],
                "reallyWanted": p["really_wanted"] or "",
                "hardestMoment": p["hardest_moment"] or "",
                "tags": p["tags"] or [],
                "createdAt": str(p["created_at"]),
                "device_id": p["device_id"]
            })
        return posts
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {e}")
        return []

# --- 投稿の保存 ---
def save_post(post):
    try:
        supabase = get_supabase()
        supabase.table("posts").insert({
            "id": post["id"],
            "device_id": post["device_id"],
            "title": post["title"],
            "author": post["author"],
            "is_anonymous": post["isAnonymous"],
            "position": post["position"],
            "theme": post["theme"],
            "what_happened": post["whatHappened"],
            "how_felt": post["howFelt"],
            "really_wanted": post["reallyWanted"],
            "hardest_moment": post["hardestMoment"],
            "tags": post["tags"],
            "created_at": post["createdAt"]
        }).execute()
        return True
    except Exception as e:
        st.error(f"保存に失敗しました: {e}")
        return False

# --- 投稿の更新 ---
def update_post(post):
    try:
        supabase = get_supabase()
        supabase.table("posts").update({
            "title": post["title"],
            "author": post["author"],
            "is_anonymous": post["isAnonymous"],
            "position": post["position"],
            "theme": post["theme"],
            "what_happened": post["whatHappened"],
            "how_felt": post["howFelt"],
            "really_wanted": post["reallyWanted"],
            "hardest_moment": post["hardestMoment"],
        }).eq("id", post["id"]).execute()
        return True
    except Exception as e:
        st.error(f"更新に失敗しました: {e}")
        return False

# --- 投稿の削除 ---
def delete_post(post_id):
    try:
        supabase = get_supabase()
        supabase.table("posts").delete().eq("id", post_id).execute()
        return True
    except Exception as e:
        st.error(f"削除に失敗しました: {e}")
        return False

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

# --- 関数: AIチャット ---
def chat_with_ai(post, analysis, chat_history, user_message):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    system_prompt = f"""
あなたは親子関係の悩みに深く寄り添う、温かいカウンセラーです。
1. 【具体的なアドバイス】実際に使える言葉や行動を提案する
2. 【次のアクションを一緒に考える】「次に何ができそうか」を一緒に考える
3. 【相手の気持ちを代弁する】親/子どもの立場から気持ちを言語化する

立場: {post['position']} / テーマ: {post['theme']}
何があったか: {post['whatHappened']}
どう感じたか: {post['howFelt']}
本当はどうしてほしかったか: {post.get('reallyWanted', '')}
一番つらかった瞬間: {post.get('hardestMoment', '')}

分析結果:
- 整理: {analysis.get('overview', '')}
- 隠れた気持ち: {analysis.get('hidden_feelings', '')}

返答は200〜300文字程度の自然な日本語で、温かいトーンで。
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

# --- カードHTML生成 ---
def render_post_card(post):
    icon = THEME_ICONS.get(post['theme'], '📝')
    tags_html = ''.join([f'<span class="tag-pill">#{t}</span>' for t in post.get('tags', [])])
    anon_badge = '<span class="badge-anon">匿名</span>' if post.get('isAnonymous') else ''
    author_text = f'<span style="font-size:12px;color:#9C7B6A;margin-left:4px;">{post.get("author","")}</span>' if post.get("author") and not post.get("isAnonymous") else ''
    position_badge = f'<span class="badge-position">{post["position"]}</span>'
    preview = post['whatHappened'][:45] + '...' if len(post['whatHappened']) > 45 else post['whatHappened']
    return f"""
    <div class="post-card">
        <div class="post-card-title">{post['title']}{anon_badge}{author_text}{position_badge}</div>
        <div class="post-card-meta"><span>{icon} {post['theme']}</span> &nbsp;·&nbsp; <span>{post['createdAt']}</span></div>
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
    try:
        col_logo, col_title = st.columns([1, 4])
        with col_logo:
            st.markdown("""<style>[data-testid="stImage"] img { background-color: #FAF7F2 !important; border-radius: 12px; }</style>""", unsafe_allow_html=True)
            st.image("images/logo.png", width=100)
        with col_title:
            st.markdown(f"""<div style="display:flex; flex-direction:column; justify-content:flex-end; height:100%; padding-left:4px; margin-top:38px;"><div class="app-title">こころのあいだ</div><div class="app-caption">こころのあいだを、ことばにする。</div></div>""", unsafe_allow_html=True)
    except:
        st.markdown('<div class="app-title">🧡 こころのあいだ</div>', unsafe_allow_html=True)
        st.markdown('<div class="app-caption">こころのあいだを、ことばにする。</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="concept-card">
        <div class="concept-title">このアプリについて</div>
        <div class="concept-body">
            親子のすれ違い、うまく言葉にできない気持ち——<br>
            そんなこころのあいだを、ここで書き出してみてください。<br>
            AIがあなたの言葉を丁寧に受け取り、隠れた気持ちや相手の視点を一緒に探します。
        </div>
        <div style="border-top:1px dashed #E8D0BC; margin-bottom:12px;"></div>
        <div style="font-size:12px; color:#9C7B6A; font-weight:500; margin-bottom:10px;">使い方</div>
        <div class="step-row"><div class="step-num">1</div><div class="step-text">「こころを書き出す」から、あったことと気持ちを書く</div></div>
        <div class="step-row"><div class="step-num">2</div><div class="step-text">「AIと見つめ直す」で気持ちを深く分析してもらう</div></div>
        <div class="step-row"><div class="step-num">3</div><div class="step-text">AIとチャットして、次の一歩を一緒に考える</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="concept-card" style="border-left: 4px solid #E8A87C;">
        <div class="concept-title">✍️ 書くことで、こころが動く</div>
        <div class="concept-body">
            感情的になっているとき、悩みが頭の中でぐるぐると大きくなっているとき——<br>
            そんなとき、気持ちをことばにして書き出すことには、不思議な力があります。<br><br>
            頭の中だけにある思いは、どんどん膨らんで主観的になりがちです。<br>
            でも、ことばとして外に出した瞬間、自分の気持ちを少し離れたところから見られるようになります。<br><br>
            「あ、自分はこんなふうに感じていたんだ」<br>
            「相手はもしかしたら、こういう気持ちだったのかもしれない」<br><br>
            書くことは、こころに客観性をそっと届けてくれます。<br>
            まずは、思いつくままに書き出してみてください。
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_nav1, col_nav2 = st.columns([1, 1])
    with col_nav1:
        if st.button("＋ こころを書き出す", use_container_width=True):
            st.session_state.view = "create"
            st.rerun()
    with col_nav2:
        if st.button("👤 マイページ", use_container_width=True):
            st.session_state.view = "mypage"
            st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    posts = load_posts()
    for post in posts:
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
        really_wanted = st.text_area("本当はどうしてほしかったですか？", placeholder="例：ただ話を聞いてほしかった…")
        hardest_moment = st.text_area("一番つらかった瞬間はどこですか？", placeholder="例：○○と言われたとき…")

        submitted = st.form_submit_button("静かに投稿する")
        if submitted:
            new_post = {
                "id": str(uuid.uuid4()),
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
                "createdAt": str(datetime.now().date()),
                "device_id": st.session_state.device_id
            }
            if save_post(new_post):
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
        position = st.selectbox("あなたの立場", ["親", "子ども"], index=["親", "子ども"].index(post['position']))
        theme = st.selectbox("テーマ", ["親子関係", "子育て", "受験・進路"], index=["親子関係", "子育て", "受験・進路"].index(post['theme']))
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        happened = st.text_area("何がありましたか？（事実）", value=post['whatHappened'])
        felt = st.text_area("どう感じましたか？（感情）", value=post['howFelt'])
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.caption("もう少し深く教えてください（任意）")
        really_wanted = st.text_area("本当はどうしてほしかったですか？", value=post.get('reallyWanted', ''))
        hardest_moment = st.text_area("一番つらかった瞬間はどこですか？", value=post.get('hardestMoment', ''))

        submitted = st.form_submit_button("保存する")
        if submitted:
            updated = {**post, "title": title if title else "名もなき感情", "author": author, "isAnonymous": is_anonymous, "position": position, "theme": theme, "whatHappened": happened, "howFelt": felt, "reallyWanted": really_wanted, "hardestMoment": hardest_moment}
            if update_post(updated):
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
    posts = load_posts()
    target_post = next((p for p in posts if p['id'] == target_id), None)

    st.markdown('<div class="section-header">🗑️ 投稿を削除しますか？</div>', unsafe_allow_html=True)
    if target_post:
        st.warning(f"「{target_post['title']}」を削除します。この操作は元に戻せません。")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("削除する", type="primary"):
            if delete_post(target_id):
                st.session_state.view = "home"
                st.rerun()
    with col2:
        if st.button("キャンセル"):
            st.session_state.view = "home"
            st.rerun()

# =============================
# 画面: マイページ
# =============================
elif st.session_state.view == "mypage":
    if st.button("← ホームへ戻る"):
        st.session_state.view = "home"
        st.rerun()

    st.markdown('<div class="section-header">👤 マイページ</div>', unsafe_allow_html=True)
    st.caption("この端末から投稿した記録です。")

    all_posts = load_posts()
    my_posts = [p for p in all_posts if p.get("device_id") == st.session_state.device_id]

    if not my_posts:
        st.markdown("""<div style="background:#FFFDF8; border:1.5px solid #E8D8C4; border-radius:14px; padding:24px; text-align:center; color:#9C7B6A; font-size:14px; line-height:1.8;">まだ投稿がありません。<br>「こころを書き出す」から最初の一歩を。</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="font-size:13px; color:#9C7B6A; margin-bottom:12px;">投稿数：{len(my_posts)}件</div>', unsafe_allow_html=True)
        for post in my_posts:
            st.markdown(render_post_card(post), unsafe_allow_html=True)
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                if st.button("✨ AI分析を見る", key=f"my_detail_{post['id']}"):
                    st.session_state.selected_post = post
                    st.session_state.analysis_result = None
                    st.session_state.chat_history = []
                    st.session_state.view = "detail"
                    st.rerun()
            with col2:
                if st.button("✏️ 編集", key=f"my_edit_{post['id']}"):
                    st.session_state.selected_post = post
                    st.session_state.view = "edit"
                    st.rerun()
            with col3:
                if st.button("🗑️ 削除", key=f"my_delete_{post['id']}"):
                    st.session_state.delete_target_id = post['id']
                    st.session_state.view = "confirm_delete"
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
            with st.spinner("言葉を紡いでいます..."):
                result = analyze_post(post)
                if "error" in result:
                    st.error(f"分析に失敗しました: {result['error']}")
                else:
                    st.session_state.analysis_result = result
                    st.session_state.chat_history = [{"role": "assistant", "content": "分析が終わりました。気になること、もっと深めたいこと、何でも話しかけてみてください。一緒に考えます🧡"}]
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
