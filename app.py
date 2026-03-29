import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="こころのあいだ", page_icon="🧡", layout="centered")

# CSSでデザインを整える（React版に近い雰囲気に）
st.markdown("""
    <style>
    .main { background-color: #FDFBF7; }
    .stButton>button { border-radius: 20px; background-color: #4A4A4A; color: white; }
    .post-card { background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #E0E0E0; margin-bottom: 15px; }
    .tag { background-color: #FFF5F0; color: #FF6B35; padding: 2px 8px; border-radius: 5px; font-size: 0.8em; margin-right: 5px; }
    </style>
    """, unsafe_allow_index=True)

# --- API設定 ---
# Streamlit CloudのSecretsからAPIキーを取得
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("APIキーが設定されていません。StreamlitのSecretsに GOOGLE_API_KEY を設定してください。")

# --- データ管理 ---
if "posts" not in st.session_state:
    st.session_state.posts = [
        {
            "id": "1",
            "title": "進路について言い合ってしまった",
            "position": "子ども",
            "theme": "受験・進路",
            "whatHappened": "美大に行きたいと伝えたら否定された。",
            "howFelt": "悲しかった。",
            "tags": ["理解されない", "期待"],
            "createdAt": "2026-03-27"
        }
    ]

# --- 関数: AI分析 ---
def analyze_post(post):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    以下の親子関係の悩みを分析し、JSON形式で出力してください。
    立場: {post['position']}
    テーマ: {post['theme']}
    内容: {post['whatHappened']}
    感情: {post['howFelt']}

    出力項目:
    1. overview (投稿の整理)
    2. hidden_feelings (奥にある気持ち)
    3. parent_perspective (親の視点)
    4. child_perspective (子の視点)
    5. actionable_hints (小さな一歩、3つの配列)
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}

# --- 画面遷移 ---
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
                <h3>{post['title']}</h3>
                <p style="color:gray; font-size:0.9em;">{post['position']} | {post['theme']}</p>
                <p>{post['whatHappened'][:50]}...</p>
            </div>
            """, unsafe_allow_index=True)
            if st.button(f"詳細を見る", key=post['id']):
                st.session_state.selected_post = post
                st.session_state.view = "detail"
                st.rerun()

# --- 画面: 新規投稿 ---
elif st.session_state.view == "create":
    st.header("こころを書き出す")
    with st.form("post_form"):
        title = st.text_input("タイトル")
        position = st.selectbox("あなたの立場", ["親", "子ども"])
        theme = st.selectbox("テーマ", ["親子関係", "子育て", "受験・進路"])
        happened = st.text_area("何がありましたか？")
        felt = st.text_area("どう感じましたか？")
        
        submitted = st.form_submit_state = st.form_submit_button("静かに投稿する")
        if submitted:
            new_post = {
                "id": str(datetime.now().timestamp()),
                "title": title,
                "position": position,
                "theme": theme,
                "whatHappened": happened,
                "howFelt": felt,
                "tags": ["新規"],
                "createdAt": str(datetime.now().date())
            }
            st.session_state.posts.insert(0, new_post)
            st.session_state.view = "home"
            st.rerun()
    
    if st.button("戻る"):
        st.session_state.view = "home"
        st.rerun()

# --- 画面: 詳細・分析 ---
elif st.session_state.view == "detail":
    post = st.session_state.selected_post
    st.button("← 一覧へ戻る", on_click=lambda: setattr(st.session_state, 'view', 'home'))
    
    st.subheader(post['title'])
    st.write(f"**立場:** {post['position']} / **テーマ:** {post['theme']}")
    st.write(f"**内容:**\n{post['whatHappened']}")
    st.write(f"**感情:**\n{post['howFelt']}")
    
    st.write("---")
    if st.button("✨ AIと見つめ直す"):
        with st.spinner("言葉を紡いでいます..."):
            result = analyze_post(post)
            if "error" in result:
                st.error("分析に失敗しました。APIキーを確認してください。")
            else:
                st.success("分析が完了しました")
                st.markdown(f"### 🔍 投稿の整理\n{result['overview']}")
                st.markdown(f"### 🧡 見えてくる気持ち\n{result['hidden_feelings']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**親の視点**\n\n{result['parent_perspective']}")
                with col2:
                    st.success(f"**子の視点**\n\n{result['child_perspective']}")
                
                st.warning("### 💡 関係をよくするヒント")
                for hint in result['actionable_hints']:
                    st.write(f"- {hint}")
