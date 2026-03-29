import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="こころのあいだ", page_icon="🧡", layout="centered")

# CSSでデザインを整える
st.markdown("""
    <style>
    .main { background-color: #FDFBF7; }
    .stButton>button { border-radius: 20px; background-color: #4A4A4A; color: white; }
    .post-card { background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #E0E0E0; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True) # ← ここを修正しました！

# --- API設定 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.warning("APIキーが設定されていません。アプリを動かすにはSecretsに GOOGLE_API_KEY を設定してください。")

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
    # モデルを指定（2026年現在の最新推奨モデルを使用）
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    以下の親子関係の悩みを分析し、日本語のJSON形式で出力してください。
    立場: {post['position']}
    テーマ: {post['theme']}
    内容: {post['whatHappened']}
    感情: {post['howFelt']}

    出力項目（日本語で回答すること）:
    1. overview (この投稿の整理)
    2. hidden_feelings (表面には見えない奥にある気持ち)
    3. parent_perspective (親の立場から見た視点とアドバイス)
    4. child_perspective (子の立場から見た視点とアドバイス)
    5. actionable_hints (関係を少しよくするためのヒント、3つのリスト)
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}

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
            if st.button(f"詳細・AI分析を見る", key=post['id']):
                st.session_state.selected_post = post
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

# --- 画面: 詳細・分析 ---
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
    if st.button("✨ AIと見つめ直す"):
        if "GOOGLE_API_KEY" not in st.secrets:
            st.error("APIキーが設定されていないため、AI機能を使えません。")
        else:
            with st.spinner("言葉を紡いでいます..."):
                result = analyze_post(post)
                if "error" in result:
                    st.error(f"分析に失敗しました: {result['error']}")
                else:
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
