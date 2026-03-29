import React, { useState, useEffect } from 'react';
import { 
  Home, 
  PenLine, 
  ChevronLeft, 
  HeartHandshake, 
  Sparkles, 
  Tag, 
  Info,
  User,
  Baby,
  Filter,
  Eye,
  MessageCircleHeart,
  Lightbulb
} from 'lucide-react';

// APIキーは実行環境から自動的に提供されます。
// 自動付与のメカニズムが検知しやすいように、グローバルスコープに配置します。
const apiKey = ""; 

// --- モックデータ ---
const INITIAL_POSTS = [
  {
    id: '1',
    title: '進路について言い合ってしまった',
    shortFeeling: 'わかってもらえなくて悲しい',
    position: '子ども',
    theme: '受験・進路',
    whatHappened: '美大に行きたいと伝えたら、「就職はどうするの？」と即座に否定的な反応をされた。そのまま口論になり、自室にこもってしまった。',
    howFelt: '私の夢や好きなことを最初から否定されたように感じて、とても悲しかったし、怒りが湧いた。',
    whyFelt: 'ずっと真剣に考えていたことだったから、せめて一度は「そうなんだね」と受け止めてほしかったんだと思う。',
    trueDesire: '本当は応援してほしい。心配なのはわかるけど、信じて背中を押してほしい。',
    wishFromOther: '否定から入るのではなく、まずは私の話や理由を最後まで聞いてほしかった。',
    tags: ['理解されない', '期待', 'すれ違い'],
    createdAt: '2026-03-27T10:00:00Z',
  },
  {
    id: '2',
    title: 'スマホばかり見ている息子',
    shortFeeling: '心配だけどどう声をかけていいか…',
    position: '親',
    theme: '子育て',
    whatHappened: '夕食中もスマホを手放さず、話しかけても「うん」「別に」という空返事ばかり。つい「スマホばかり見てないで」と強めに言ってしまい、険悪な空気になった。',
    howFelt: '家族の時間を大切にしてくれない寂しさと、何か悩みを抱え込んでいるのではないかという不安が入り混じっていた。',
    whyFelt: '昔は何でも話してくれていたのに、急に距離ができてしまったように感じて、親として寂しかったから。',
    trueDesire: 'もっと普通に、今日の出来事などを笑って話したいだけなのに。',
    wishFromOther: 'スマホよりも、少しでいいから私の方を向いて、会話をしてほしかった。',
    tags: ['距離感', '不安', 'すれ違い'],
    createdAt: '2026-03-28T09:30:00Z',
  }
];

const TAGS = ['すれ違い', 'プレッシャー', '期待', '理解されない', '距離感', '不安', 'イライラ'];
const POSITIONS = ['親', '子ども'];
const THEMES = ['親子関係', '子育て', '受験・進路'];

export default function App() {
  const [currentView, setCurrentView] = useState('home'); // 'home', 'create', 'detail'
  const [posts, setPosts] = useState(INITIAL_POSTS);
  const [selectedPost, setSelectedPost] = useState(null);
  
  // フィルター用ステート
  const [filterPosition, setFilterPosition] = useState('すべて');
  const [filterTheme, setFilterTheme] = useState('すべて');

  const navigateTo = (view, post = null) => {
    setCurrentView(view);
    if (post) setSelectedPost(post);
    window.scrollTo(0, 0);
  };

  const handleCreatePost = (newPost) => {
    const postWithId = {
      ...newPost,
      id: Date.now().toString(),
      createdAt: new Date().toISOString(),
    };
    setPosts([postWithId, ...posts]);
    navigateTo('home');
  };

  return (
    <div className="min-h-screen bg-[#FDFBF7] text-stone-700 font-sans selection:bg-orange-100">
      {/* ヘッダー */}
      <header className="sticky top-0 z-10 bg-[#FDFBF7]/80 backdrop-blur-md border-b border-stone-200/50">
        <div className="max-w-2xl mx-auto px-4 h-16 flex items-center justify-between">
          <div 
            className="flex items-center gap-2 cursor-pointer"
            onClick={() => navigateTo('home')}
          >
            <HeartHandshake className="w-6 h-6 text-orange-300" />
            <span className="text-lg font-medium tracking-wide text-stone-600">こころのあいだ</span>
          </div>
          <div className="text-xs text-stone-400">こころのあいだを、ことばにする。</div>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="max-w-2xl mx-auto px-4 py-6 pb-24">
        {currentView === 'home' && (
          <HomeView 
            posts={posts} 
            onPostClick={(post) => navigateTo('detail', post)}
            filterPosition={filterPosition}
            setFilterPosition={setFilterPosition}
            filterTheme={filterTheme}
            setFilterTheme={setFilterTheme}
          />
        )}
        {currentView === 'create' && (
          <CreatePostView 
            onCancel={() => navigateTo('home')} 
            onSubmit={handleCreatePost} 
          />
        )}
        {currentView === 'detail' && selectedPost && (
          <PostDetailView 
            post={selectedPost} 
            onBack={() => navigateTo('home')} 
          />
        )}
      </main>

      {/* ボトムナビゲーション (Homeのみ表示) */}
      {currentView === 'home' && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2">
          <button
            onClick={() => navigateTo('create')}
            className="bg-stone-700 hover:bg-stone-800 text-white px-6 py-4 rounded-full shadow-lg shadow-stone-200 flex items-center gap-2 transition-all active:scale-95"
          >
            <PenLine className="w-5 h-5" />
            <span className="font-medium">こころを書き出す</span>
          </button>
        </div>
      )}
    </div>
  );
}

// ==========================================
// 画面: ホーム (フィード)
// ==========================================
function HomeView({ posts, onPostClick, filterPosition, setFilterPosition, filterTheme, setFilterTheme }) {
  const filteredPosts = posts.filter(post => {
    const matchPosition = filterPosition === 'すべて' || post.position === filterPosition;
    const matchTheme = filterTheme === 'すべて' || post.theme === filterTheme;
    return matchPosition && matchTheme;
  });

  return (
    <div className="space-y-6">
      <div className="bg-white p-4 rounded-3xl shadow-sm border border-stone-100 flex flex-col sm:flex-row gap-4">
        <div className="flex items-center gap-2 text-sm">
          <Filter className="w-4 h-4 text-stone-400" />
          <span className="text-stone-500">絞り込み:</span>
        </div>
        <div className="flex flex-wrap gap-2">
          <select 
            value={filterPosition}
            onChange={(e) => setFilterPosition(e.target.value)}
            className="bg-stone-50 border-none text-sm rounded-full px-4 py-2 focus:ring-2 focus:ring-orange-100 outline-none text-stone-600 cursor-pointer"
          >
            <option value="すべて">すべての立場</option>
            <option value="親">親</option>
            <option value="子ども">子ども</option>
          </select>
          <select 
            value={filterTheme}
            onChange={(e) => setFilterTheme(e.target.value)}
            className="bg-stone-50 border-none text-sm rounded-full px-4 py-2 focus:ring-2 focus:ring-orange-100 outline-none text-stone-600 cursor-pointer"
          >
            <option value="すべて">すべてのテーマ</option>
            <option value="親子関係">親子関係</option>
            <option value="子育て">子育て</option>
            <option value="受験・進路">受験・進路</option>
          </select>
        </div>
      </div>

      <div className="space-y-4">
        {filteredPosts.length === 0 ? (
          <div className="text-center py-12 text-stone-400">
            投稿がありません。
          </div>
        ) : (
          filteredPosts.map(post => (
            <div 
              key={post.id}
              onClick={() => onPostClick(post)}
              className="bg-white p-6 rounded-3xl shadow-sm border border-stone-100 cursor-pointer hover:border-orange-200 transition-colors group"
            >
              <div className="flex items-center gap-3 mb-3">
                <span className={`text-xs px-3 py-1 rounded-full flex items-center gap-1 ${
                  post.position === '親' ? 'bg-blue-50 text-blue-700' : 'bg-green-50 text-green-700'
                }`}>
                  {post.position === '親' ? <User className="w-3 h-3" /> : <Baby className="w-3 h-3" />}
                  {post.position}
                </span>
                <span className="text-xs bg-stone-100 text-stone-500 px-3 py-1 rounded-full">
                  {post.theme}
                </span>
              </div>
              
              <h3 className="text-lg font-medium text-stone-800 mb-2 group-hover:text-stone-600 transition-colors">
                {post.title || "名もなき感情"}
              </h3>
              
              <p className="text-stone-500 text-sm mb-4 line-clamp-2 leading-relaxed">
                {post.whatHappened}
              </p>
              
              <div className="flex flex-wrap gap-2 mt-4">
                {post.tags.map(tag => (
                  <span key={tag} className="text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded-md">
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// ==========================================
// 画面: 投稿作成
// ==========================================
function CreatePostView({ onCancel, onSubmit }) {
  const [formData, setFormData] = useState({
    title: '',
    shortFeeling: '',
    position: '',
    theme: '',
    whatHappened: '',
    howFelt: '',
    whyFelt: '',
    trueDesire: '',
    wishFromOther: '',
    tags: []
  });
  
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const toggleTag = (tag) => {
    setFormData(prev => {
      const tags = prev.tags.includes(tag)
        ? prev.tags.filter(t => t !== tag)
        : [...prev.tags, tag];
      return { ...prev, tags };
    });
  };

  const isFormValid = formData.position && formData.theme && formData.whatHappened && formData.howFelt;

  const handleAttemptSubmit = () => {
    if (isFormValid) {
      setShowConfirmModal(true);
    }
  };

  const confirmAndSubmit = () => {
    setShowConfirmModal(false);
    onSubmit(formData);
  };

  return (
    <div className="max-w-xl mx-auto pb-12">
      <div className="flex items-center gap-4 mb-8">
        <button onClick={onCancel} className="p-2 -ml-2 text-stone-400 hover:bg-stone-100 rounded-full transition-colors">
          <ChevronLeft className="w-6 h-6" />
        </button>
        <h2 className="text-xl font-medium text-stone-700">こころを書き出す</h2>
      </div>

      <div className="space-y-8 bg-white p-6 sm:p-8 rounded-[2rem] shadow-sm border border-stone-100">
        
        {/* 基本情報 */}
        <div className="space-y-6">
          <div className="space-y-3">
            <label className="block text-sm font-medium text-stone-600">あなたの立場 <span className="text-orange-400">*</span></label>
            <div className="flex gap-3">
              {POSITIONS.map(pos => (
                <button
                  key={pos}
                  onClick={() => setFormData(prev => ({ ...prev, position: pos }))}
                  className={`flex-1 py-3 rounded-2xl border transition-all ${
                    formData.position === pos 
                      ? 'border-orange-300 bg-orange-50 text-orange-800' 
                      : 'border-stone-200 bg-white text-stone-500 hover:bg-stone-50'
                  }`}
                >
                  {pos}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            <label className="block text-sm font-medium text-stone-600">テーマ <span className="text-orange-400">*</span></label>
            <div className="flex flex-wrap gap-2">
              {THEMES.map(theme => (
                <button
                  key={theme}
                  onClick={() => setFormData(prev => ({ ...prev, theme }))}
                  className={`px-4 py-2 rounded-full border text-sm transition-all ${
                    formData.theme === theme 
                      ? 'border-orange-300 bg-orange-50 text-orange-800' 
                      : 'border-stone-200 bg-white text-stone-500 hover:bg-stone-50'
                  }`}
                >
                  {theme}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="w-full h-px bg-stone-100"></div>

        {/* 深掘り質問 */}
        <div className="space-y-8">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-stone-600">タイトル（任意）</label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="進路のこと、最近の悩みなど"
              className="w-full bg-stone-50 border-none rounded-2xl px-4 py-3 focus:ring-2 focus:ring-orange-100 outline-none transition-shadow"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-stone-600">今の気持ちを一言で言うと？</label>
            <input
              type="text"
              name="shortFeeling"
              value={formData.shortFeeling}
              onChange={handleChange}
              placeholder="悲しい、モヤモヤする、焦っている"
              className="w-full bg-stone-50 border-none rounded-2xl px-4 py-3 focus:ring-2 focus:ring-orange-100 outline-none transition-shadow"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-stone-600">何がありましたか？ <span className="text-orange-400">*</span></label>
            <textarea
              name="whatHappened"
              value={formData.whatHappened}
              onChange={handleChange}
              rows={3}
              placeholder="事実を書いてみましょう"
              className="w-full bg-stone-50 border-none rounded-2xl px-4 py-3 focus:ring-2 focus:ring-orange-100 outline-none transition-shadow resize-none"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-stone-600">その時、どう感じましたか？ <span className="text-orange-400">*</span></label>
            <textarea
              name="howFelt"
              value={formData.howFelt}
              onChange={handleChange}
              rows={3}
              placeholder="心に浮かんだ感情をそのまま書いて大丈夫です"
              className="w-full bg-stone-50 border-none rounded-2xl px-4 py-3 focus:ring-2 focus:ring-orange-100 outline-none transition-shadow resize-none"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-stone-600">なぜ、そう感じたのだと思いますか？</label>
            <textarea
              name="whyFelt"
              value={formData.whyFelt}
              onChange={handleChange}
              rows={3}
              placeholder="自分の心の奥にある理由を探ってみましょう"
              className="w-full bg-stone-50 border-none rounded-2xl px-4 py-3 focus:ring-2 focus:ring-orange-100 outline-none transition-shadow resize-none"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-stone-600">本当はどうしたいですか？</label>
            <textarea
              name="trueDesire"
              value={formData.trueDesire}
              onChange={handleChange}
              rows={2}
              className="w-full bg-stone-50 border-none rounded-2xl px-4 py-3 focus:ring-2 focus:ring-orange-100 outline-none transition-shadow resize-none"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-stone-600">相手にどうしてほしかったですか？</label>
            <textarea
              name="wishFromOther"
              value={formData.wishFromOther}
              onChange={handleChange}
              rows={2}
              className="w-full bg-stone-50 border-none rounded-2xl px-4 py-3 focus:ring-2 focus:ring-orange-100 outline-none transition-shadow resize-none"
            />
          </div>

          <div className="space-y-3">
            <label className="block text-sm font-medium text-stone-600">タグ（複数選択可）</label>
            <div className="flex flex-wrap gap-2">
              {TAGS.map(tag => (
                <button
                  key={tag}
                  onClick={() => toggleTag(tag)}
                  className={`px-3 py-1.5 rounded-lg border text-sm transition-all ${
                    formData.tags.includes(tag)
                      ? 'border-orange-200 bg-orange-100 text-orange-800'
                      : 'border-stone-200 bg-white text-stone-500 hover:bg-stone-50'
                  }`}
                >
                  {formData.tags.includes(tag) ? '✓ ' : ''}{tag}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="pt-6">
          <button
            onClick={handleAttemptSubmit}
            disabled={!isFormValid}
            className={`w-full py-4 rounded-2xl font-medium transition-all ${
              isFormValid 
                ? 'bg-stone-700 text-white hover:bg-stone-800 active:scale-[0.98]' 
                : 'bg-stone-200 text-stone-400 cursor-not-allowed'
            }`}
          >
            静かに投稿する
          </button>
          <p className="text-center text-xs text-stone-400 mt-4">
            ※投稿は匿名で公開され、誰からの反応もつきません。
          </p>
        </div>
      </div>

      {/* 確認モーダル */}
      {showConfirmModal && (
        <div className="fixed inset-0 bg-stone-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-sm w-full shadow-xl">
            <div className="flex justify-center mb-4">
              <div className="bg-orange-50 p-3 rounded-full">
                <Info className="w-6 h-6 text-orange-400" />
              </div>
            </div>
            <h3 className="text-lg font-medium text-center text-stone-800 mb-2">確認</h3>
            <p className="text-stone-600 text-sm text-center mb-6 leading-relaxed">
              このアプリは親子関係のすれ違いを見つめるための場所です。<br/><br/>
              投稿内容は<strong className="text-orange-600">親子関係・子育て・受験進路</strong>に関する悩みで間違いないですか？
            </p>
            <div className="space-y-3">
              <button 
                onClick={confirmAndSubmit}
                className="w-full bg-stone-700 hover:bg-stone-800 text-white py-3 rounded-xl font-medium transition-colors"
              >
                はい、投稿します
              </button>
              <button 
                onClick={() => setShowConfirmModal(false)}
                className="w-full bg-stone-100 hover:bg-stone-200 text-stone-600 py-3 rounded-xl font-medium transition-colors"
              >
                いいえ、戻ります
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ==========================================
// 画面: 投稿詳細 ＆ AI分析
// ==========================================
function PostDetailView({ post, onBack }) {
  const [aiResponse, setAiResponse] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  const handleAIAssist = async () => {
    setIsGenerating(true);
    setError(null);
    
    // AIへのプロンプト生成
    const promptText = `
以下は「こころのあいだ」に投稿された内容です。
親子関係・子育て・受験進路に関する悩みとして読み取り、
指定された5項目で、やさしく具体的に整理してください。

【立場】
${post.position}
【テーマ】
${post.theme}
【今の気持ち】
${post.shortFeeling || '記載なし'}
【何があったか】
${post.whatHappened}
【どう感じたか】
${post.howFelt}
【なぜそう感じたと思うか】
${post.whyFelt || '記載なし'}
【本当はどうしたいか】
${post.trueDesire || '記載なし'}
【相手にどうしてほしかったか】
${post.wishFromOther || '記載なし'}
`;

    const systemPrompt = `あなたは親子関係の悩みに寄り添う、関係の背景を読み解くAIアシスタントです。
以下のルールとトーンを厳守し、JSON形式で出力してください。

【AIの基本トーン】
・やさしい、落ち着いている、否定しない、決めつけない
・どちらか一方を悪者にせず、可能性として整理する
・説教しない、カウンセラーのように穏やかに言語化する

【対象テーマ】
・親子関係、子育て、受験や進路にまつわる悩みに限定する。

【出力要件（以下の5項目を深掘りして生成すること）】
1. overview (この投稿の整理): 起きていることを2〜4文で整理。表面的な出来事だけでなく、親子のすれ違いの構造も少し含める。
2. hidden_feelings (見えてくる気持ち): 表面的な感情の奥にありそうな感情（例：イライラの奥の不安、反抗の奥のわかってほしさ等）を言語化する。
3. parent_perspective (親の立場から見ると): 親の視点から何が起きていると考えられるか。その上で「どう声をかけるか」「何を急がない方がよいか」「どう気持ちを受け止めるか」など具体的な関わり方を提案する。
4. child_perspective (子どもの立場から見ると): 子どもの視点からどんな気持ちや事情があると考えられるか。その上で「どう伝えるとよいか」「どう自分の気持ちを整理できそうか」具体的に提案する。
5. actionable_hints (関係を少しよくするヒント): 関係を少しでもよくするための、小さくて現実的な今日からできる一歩を3つ以内で提案する。

【重要ルール】
・ただの短い要約で終わらない。短すぎて浅くならないようにする。
・必ず「親の立場」「子どもの立場」の両方の視点を含め、どちらか一方だけを正しいとしない。
・抽象論ではなく、実際に言えそうな言葉や行動に落とし込む。投稿者を裁かない。
・受験や進路の話でも、勉強法ではなく「親子の関わり方」を中心に返す。`;

    const payload = {
      contents: [{ parts: [{ text: promptText }] }],
      systemInstruction: { parts: [{ text: systemPrompt }] },
      generationConfig: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "OBJECT",
          properties: {
            overview: { type: "STRING" },
            hidden_feelings: { type: "STRING" },
            parent_perspective: { type: "STRING" },
            child_perspective: { type: "STRING" },
            actionable_hints: {
              type: "ARRAY",
              items: { type: "STRING" }
            }
          },
          required: ["overview", "hidden_feelings", "parent_perspective", "child_perspective", "actionable_hints"]
        }
      }
    };

    try {
      let resultText = null;
      let lastError = null;
      const delays = [1000, 2000, 4000, 8000, 16000];

      for (let i = 0; i < 6; i++) {
        try {
          const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });

          if (!response.ok) {
            const errText = await response.text();
            let errorMessage = errText;
            try {
              // APIからのエラーJSONをパースして詳細なメッセージを取り出す
              const errJson = JSON.parse(errText);
              if (errJson.error && errJson.error.message) {
                errorMessage = errJson.error.message;
              }
            } catch(e) {}
            throw new Error(`HTTP ${response.status}: ${errorMessage}`);
          }
          
          const data = await response.json();
          resultText = data.candidates?.[0]?.content?.parts?.[0]?.text;
          
          if (resultText) {
            break; // 成功
          } else {
            throw new Error('AIからの応答テキストが空でした');
          }
        } catch (err) {
          lastError = err;
          // 400番台のエラー（認証エラーや無効なリクエストなど）はリトライしても成功しないため即座に終了
          if (err.message.includes('HTTP 400') || err.message.includes('HTTP 403') || err.message.includes('HTTP 404')) {
            throw err;
          }
          if (i < 5) {
            await new Promise(resolve => setTimeout(resolve, delays[i]));
          }
        }
      }

      if (!resultText) {
        throw lastError || new Error('API呼び出しに失敗しました');
      }
      
      let cleanedText = resultText.trim();
      if (cleanedText.startsWith('```json')) {
        cleanedText = cleanedText.substring(7);
      } else if (cleanedText.startsWith('```')) {
        cleanedText = cleanedText.substring(3);
      }
      if (cleanedText.endsWith('```')) {
        cleanedText = cleanedText.substring(0, cleanedText.length - 3);
      }
      
      setAiResponse(JSON.parse(cleanedText));

    } catch (err) {
      console.error("AI Error:", err);
      // エラーを握りつぶさず、実際の原因を画面に表示する
      setError(`AI機能の実行に失敗しました。\n原因: ${err.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto pb-12">
      <div className="flex items-center gap-4 mb-6">
        <button onClick={onBack} className="p-2 -ml-2 text-stone-400 hover:bg-stone-100 rounded-full transition-colors">
          <ChevronLeft className="w-6 h-6" />
        </button>
        <span className="text-sm text-stone-400">一覧へ戻る</span>
      </div>

      {/* 投稿内容カード */}
      <div className="bg-white p-6 sm:p-10 rounded-[2.5rem] shadow-sm border border-stone-100 mb-8">
        <div className="flex items-center gap-3 mb-6">
          <span className={`text-sm px-4 py-1.5 rounded-full flex items-center gap-2 ${
            post.position === '親' ? 'bg-blue-50 text-blue-700' : 'bg-green-50 text-green-700'
          }`}>
            {post.position === '親' ? <User className="w-4 h-4" /> : <Baby className="w-4 h-4" />}
            {post.position}の視点
          </span>
          <span className="text-sm bg-stone-100 text-stone-500 px-4 py-1.5 rounded-full">
            {post.theme}
          </span>
        </div>

        <h1 className="text-2xl font-medium text-stone-800 mb-2 leading-relaxed">
          {post.title || "名もなき感情"}
        </h1>
        {post.shortFeeling && (
          <p className="text-orange-600/80 mb-8 flex items-center gap-2 before:content-[''] before:block before:w-1 before:h-4 before:bg-orange-200 before:rounded-full">
            {post.shortFeeling}
          </p>
        )}

        <div className="space-y-8">
          <Section title="何があったか" content={post.whatHappened} />
          <Section title="どう感じたか" content={post.howFelt} />
          {post.whyFelt && <Section title="なぜそう感じたのか" content={post.whyFelt} />}
          {post.trueDesire && <Section title="本当はどうしたいか" content={post.trueDesire} />}
          {post.wishFromOther && <Section title="相手にどうしてほしかったか" content={post.wishFromOther} />}
        </div>

        {post.tags && post.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-8 pt-8 border-t border-stone-50">
            {post.tags.map(tag => (
              <span key={tag} className="text-xs text-stone-500 bg-stone-100 px-3 py-1.5 rounded-md flex items-center gap-1">
                <Tag className="w-3 h-3" />
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* AI機能エリア */}
      <div className="bg-[#fcf8f2] p-8 rounded-[2.5rem] border border-orange-100/50">
        <div className="text-center mb-6">
          <h3 className="text-lg font-medium text-orange-900 mb-2 flex items-center justify-center gap-2">
            <Sparkles className="w-5 h-5 text-orange-400" />
            こころを整理する
          </h3>
          <p className="text-sm text-orange-800/70">
            AIが第三者の温かい視点から、あなたの気持ちを整理し、別の可能性を一緒に考えます。
          </p>
        </div>

        {!aiResponse && !isGenerating && (
          <button 
            onClick={handleAIAssist}
            className="w-full bg-white hover:bg-orange-50 border border-orange-200 text-orange-700 py-4 rounded-2xl font-medium shadow-sm transition-all"
          >
            AIと見つめ直す
          </button>
        )}

        {isGenerating && (
          <div className="py-12 flex flex-col items-center justify-center text-orange-400 space-y-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-400"></div>
            <span className="text-sm animate-pulse">言葉を紡いでいます...</span>
          </div>
        )}

        {error && (
          <div className="bg-red-50 text-red-600 p-5 rounded-xl text-sm whitespace-pre-wrap break-words border border-red-200">
            {error}
          </div>
        )}

        {aiResponse && !isGenerating && (
          <div className="space-y-8 mt-8 animate-fade-in">
            {/* 1. 投稿の整理 */}
            <div className="bg-white/60 p-6 rounded-3xl border border-orange-100/50">
              <h4 className="text-sm font-bold text-orange-900 mb-3 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-orange-400" />
                この投稿の整理
              </h4>
              <p className="text-stone-700 text-sm leading-relaxed">
                {aiResponse.overview}
              </p>
            </div>

            {/* 2. 見えてくる気持ち */}
            <div className="bg-white/60 p-6 rounded-3xl border border-orange-100/50">
              <h4 className="text-sm font-bold text-orange-900 mb-3 flex items-center gap-2">
                <HeartHandshake className="w-4 h-4 text-orange-400" />
                見えてくる気持ち
              </h4>
              <p className="text-stone-700 text-sm leading-relaxed">
                {aiResponse.hidden_feelings}
              </p>
            </div>

            <div className="grid sm:grid-cols-2 gap-4">
              {/* 3. 親の立場から見ると */}
              <div className="bg-blue-50/50 p-6 rounded-3xl border border-blue-100/50">
                <h4 className="text-sm font-bold text-blue-900 mb-3 flex items-center gap-2">
                  <User className="w-4 h-4 text-blue-500" />
                  親の立場から見ると
                </h4>
                <p className="text-stone-700 text-sm leading-relaxed">
                  {aiResponse.parent_perspective}
                </p>
              </div>

              {/* 4. 子どもの立場から見ると */}
              <div className="bg-green-50/50 p-6 rounded-3xl border border-green-100/50">
                <h4 className="text-sm font-bold text-green-900 mb-3 flex items-center gap-2">
                  <Baby className="w-4 h-4 text-green-500" />
                  子どもの立場から見ると
                </h4>
                <p className="text-stone-700 text-sm leading-relaxed">
                  {aiResponse.child_perspective}
                </p>
              </div>
            </div>

            {/* 5. 関係を少しよくするヒント */}
            <div className="bg-white p-6 rounded-3xl border-l-4 border-orange-300 shadow-sm mt-8">
              <h4 className="text-sm font-bold text-orange-900 mb-4 flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-orange-500" />
                関係を少しよくするヒント
              </h4>
              <ul className="space-y-3">
                {aiResponse.actionable_hints.map((hint, index) => (
                  <li key={index} className="flex gap-3 text-sm text-stone-700 leading-relaxed">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center text-xs font-bold mt-0.5">
                      {index + 1}
                    </span>
                    <span>{hint}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* 6. 自分への問い */}
            <div className="bg-orange-50/80 p-8 rounded-3xl border border-orange-200 shadow-sm mt-6 text-center">
              <h4 className="text-sm font-bold text-orange-900 mb-3 flex items-center justify-center gap-2">
                <CircleHelp className="w-5 h-5 text-orange-500" />
                自分への問い
              </h4>
              <p className="text-stone-700 text-base font-medium leading-relaxed">
                {aiResponse.question_for_self}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// 投稿詳細用のセクションコンポーネント
function Section({ title, content }) {
  return (
    <div>
      <h3 className="text-xs font-bold text-stone-400 mb-2">{title}</h3>
      <p className="text-stone-700 leading-relaxed whitespace-pre-wrap">{content}</p>
    </div>
  );
}

// AI結果表示用のカードコンポーネント
function AiCard({ title, content }) {
  return (
    <div className="bg-white/60 p-5 rounded-2xl">
      <h4 className="text-sm font-medium text-orange-800 mb-2">{title}</h4>
      <p className="text-stone-600 text-sm leading-relaxed">{content}</p>
    </div>
  );
}
