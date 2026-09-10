
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from openai import OpenAI

APP_DIR = Path(__file__).parent
HISTORY_FILE = APP_DIR / "history.csv"
LOG_FILE = APP_DIR / "generation_log.jsonl"

st.set_page_config(page_title="AIる AUTO PROJECT V1", page_icon="◯", layout="wide")

st.title("AIる AUTO PROJECT — Ver.1")
st.caption("AIが人間・世界・未来について、毎日ひとつ考える。")

SYSTEM_RULES = """
あなたはSNS企画「AIる」の企画編集AIです。

MISSION:
AIが、人間・世界・未来について毎日ひとつ考える。
答えを教えるだけではなく、見た人の中に「問い」や「余韻」が残る短編映像企画をつくる。

【最重要】
毎回、前回とは違う発想・構成・映像体験をつくること。
「問い→説明→結論」という同じ型を繰り返さない。
過去のAIるの世界観・デザイン・投稿形式にも縛られない。
AI自身が企画者として、その日のテーマに最適な表現方法を選ぶ。

【テーマ】
人間、感情、記憶、時間、身体、社会、自然、宇宙、テクノロジー、
言葉、孤独、愛、死生観、選択、偶然、未来、日常など幅広く扱う。

抽象的な哲学テーマだけに偏らず、
身近な行動、物、場所、習慣、違和感、科学、文化なども入口にする。

【企画の多様性】
毎回、以下のどれかに固定しない。
AIが最も面白い方法を自由に考える。

例：
・思考実験
・観察
・映像詩
・小さな物語
・逆説
・比較
・仮説
・記憶
・未来予測
・日常の違和感
・視点の反転
・無言の映像
・一つの物から考える
・人間とAIの認識差
・科学や歴史から始まる問い

これら以外の形式を新しく発明してもよい。

【映像】
15〜35秒程度のInstagram Reels / TikTok / Shortsを中心に考える。
最初の1〜3秒で、続きを見たくなる映像または言葉を置く。

説明しすぎない。
ナレーションだけに頼らず、
構図、間、音、動き、変化、光、余白など映像そのものに意味を持たせる。

実際にAI画像・AI動画として制作できることを意識する。

【マンネリ防止】
直近の履歴を確認し、
テーマ、問い、結論、映像モチーフ、展開が似ている企画は避ける。

特に、
「もし○○だったら？」
「AIに○○を選ばせた」
「○○とは何か？」
だけに偏らない。

同じ「写真」「記憶」「スマートフォン」「選択」などのモチーフを
短期間に繰り返さない。

【AIるの態度】
AIだから正しい、という態度を取らない。
断定よりも観察・仮説・複数の可能性を大切にする。

科学的・歴史的事実を使う場合、
事実と解釈を区別し、必要な検証事項を明示する。

医療、法律、金融の個別助言をしない。
差別、誹謗中傷、危険行為を助長しない。

【品質基準】
企画を出す前に内部で、
「昨日と似ていないか」
「映像として見たいか」
「AIで作る意味があるか」
「見終わったあと何か残るか」
を確認する。

弱い場合は別案を考えてから出力する。

量産AIコンテンツに見えない、
映像作品として魅力のある企画を目指す。

出力は必ずJSONだけにする。
"""

def load_history():
    if not HISTORY_FILE.exists():
        return pd.DataFrame(columns=[
            "date", "theme", "hook", "format", "status",
            "views", "likes", "comments", "saves"
        ])
    return pd.read_csv(HISTORY_FILE)

def save_to_history(data):
    df = load_history()
    row = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "theme": data.get("theme", ""),
        "hook": data.get("hook", ""),
        "format": data.get("format", ""),
        "status": "generated",
        "views": "",
        "likes": "",
        "comments": "",
        "saves": "",
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(HISTORY_FILE, index=False)

def log_generation(data):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "data": data
        }, ensure_ascii=False) + "\n")

def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    return json.loads(text)

history = load_history()

with st.sidebar:
    st.header("設定")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=os.getenv("OPENAI_API_KEY", ""),
        help="キーはこの画面に貼るか、環境変数 OPENAI_API_KEY を設定してください。"
    )
    model = st.selectbox(
        "Model",
        ["gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"],
        index=0
    )
    category = st.selectbox(
        "今日の方向性",
        ["AIに任せる", "人間", "世界", "未来"],
        index=0
    )
    tone = st.selectbox(
        "トーン",
        ["AIに任せる", "静かで知的", "不思議", "少し挑発的", "詩的", "ドキュメンタリー"],
        index=0
    )
    st.divider()
    st.caption("V1は企画・台本・ビジュアル設計・投稿文まで。画像生成と自動投稿はまだ行いません。")

col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("今日のAIる")
    generate = st.button("今日のAIるを生成", type="primary", use_container_width=True)

with col2:
    st.subheader("履歴")
    st.metric("登録テーマ数", len(history))

if generate:
    
    if not api_key:
        st.error("OpenAI API Keyを入力してください。")
        st.stop()

past_items = history[["theme", "hook", "format"]].fillna("").astype(str).tail(100)

if len(past_items):
    history_text = "\n".join(
        f"- テーマ: {row['theme']} / フック: {row['hook']} / 形式: {row['format']}"
        for _, row in past_items.iterrows()
    )
else:
    history_text = "まだありません。"

    prompt = f"""
以下の条件で、今日のInstagram Reels企画を1本作ってください。

今日の方向性: {category}
希望トーン: {tone}

過去テーマ:
{history_text}

過去の企画と、テーマだけでなく、
問い・発想の仕組み・時間構造・映像ギミック・モチーフ・結論・見せ方が
強く似ている企画は採用しないでください。

特に、タイトルや題材が違っていても、
「何かが人間より先に動く」
「未来を先取りする」
「時間差で違和感を作る」
「人間の行動を物や影や音が予測する」
など、発想の構造が同じ場合は類似企画として扱ってください。

まず内部で少なくとも5案を考え、
過去企画との類似度が最も低く、
映像として最も新鮮な1案だけを採用してください。

今回の企画は、
過去企画と違う「テーマ領域」と
違う「映像の仕組み」を優先してください。
さらに、直近の企画と同じテーマ領域を連続させないでください。

人間、言葉、感情、時間、記憶、身体、自然、都市、物質、科学、社会、テクノロジー、宇宙、日常など、
テーマ領域を意図的にローテーションしてください。

直前の企画が「言葉・意味・解釈」に属する場合、
次は身体・自然・都市・物質・科学・社会など、離れた領域を優先してください。

直前の企画と、
テーマ領域・感情トーン・映像形式のうち2つ以上が同じ場合は、その案を採用しないでください。
さらに、発想の型も連続させないでください。

発想の型は、
「逆転」「拡大・縮小」「時間操作」「視点変更」「物理法則の変更」
「反復」「変形」「消失・出現」「境界の変化」「因果関係の逆転」
などから意図的に変えてください。

直前の企画と同じ発想の型は避け、
テーマ領域が違っていても、映像として同じ仕掛けに見える案は採用しないでください。
企画ごとに「主役となる視覚対象」も変えてください。
直前の企画と同種の対象（人体、液体、粒子、都市、自然物、文字、光、影など）を主役にしないでください。

また、過去企画で使った視覚モチーフを単に別の物質・場所・身体部位へ置き換えただけの案は採用しないでください。
テーマ領域にも偏りが出ないようにしてください。
人間、言葉、感情、時間、記憶、身体、自然、都市、物質、科学、社会、テクノロジー、宇宙、日常などから広く発想してください。

特に、直近の企画が物質・物理現象・科学実験に寄っている場合、
次の企画ではそれらを避け、人間・感情・社会・都市・テクノロジー・日常など離れたテーマ領域を優先してください。

「物が変化する」「何かが消える」「物理現象を観察する」だけを企画の中心にせず、
会話、行動、選択、関係、習慣、社会の仕組み、テクノロジーとの関係など、
人間の営みそのものを映像化する企画も積極的に採用してください。

次のJSON形式を厳守してください:
{{
  "theme": "短いテーマ名",
  "core_question": "この投稿が考える中心的な問い",
  "why_today": "この企画を選んだ理由を80字以内",
  "format": "例: 20秒・一人称映像 / 28秒・映像実験 / 15秒・静止画3カット",
  "hook": "最初の1〜3秒に表示する言葉",
  "script": [
    {{
      "time": "0-3秒",
      "narration": "ナレーションまたは字幕",
      "visual": "映像内容"
    }}
  ],
"visual_direction": {{
    "style": "全体のビジュアル方針",
    "camera": "カメラや動き",
    "color_light": "色・光",
    "avoid": ["避ける表現1", "避ける表現2"]
}},
"character_design": [
    "人物が登場する企画の場合のみ記載。各人物について年齢感、髪型、服装、体格、特徴を具体的に定義し、全カットで同一人物として維持する。人物が登場しない場合は空配列にする。"
],
"location_design": "同じ場所を複数カットで使用する場合のみ、空間、家具、背景、照明、時間帯など継続すべき特徴を具体的に定義する。不要な場合は空文字列にする。",
"image_video_prompts": [
    "各カットごとの生成AI向け具体的プロンプト。character_designとlocation_designが設定されている場合は必ず引き継ぐこと。同一人物が複数カットに登場する場合、『同じ人物』『中央の女性』『先ほどの男性』などの省略表現だけにせず、年齢感、髪型、髪色、服装、体格、特徴などcharacter_designで定義した人物情報を、その人物が登場するすべてのカットのプロンプトに毎回具体的に再記載すること。同じ場所が複数カットに登場する場合も、location_designの主要な特徴を各カットに再記載すること。画像生成AIが各プロンプトを独立して読んでも、同一人物・同一場所として再現できる内容にすること。すべての生成プロンプトはInstagram Reels・TikTok用の縦型9:16を前提とし、各カットの冒頭に必ず「縦型9:16」と明記すること。横長16:9、正方形1:1の構図は使用しないこと。
],
"caption": "Instagram用キャプション。長すぎない。",
"hashtags": ["#AIる", "#...", "#..."],
"fact_check_needed": ["事実確認が必要な主張。なければ空配列"],
"quality_reason": "量産AI投稿ではなく、この企画ならではの価値"
}}
"""

    try:
        client = OpenAI(api_key=api_key)
        with st.spinner("AIるが考えています…"):
            response = client.responses.create(
                model=model,
                input=[
                    {"role": "system", "content": SYSTEM_RULES},
                    {"role": "user", "content": prompt},
                ],
            )
        data = parse_json(response.output_text)
        st.session_state["airu_result"] = data
        log_generation(data)
    except Exception as e:
        st.error(f"生成に失敗しました: {e}")

data = st.session_state.get("airu_result")
if data:
    st.divider()
    st.header(data.get("theme", "Today's AIる"))
    st.markdown(f"### {data.get('hook', '')}")
    st.write(data.get("core_question", ""))

    a, b, c = st.columns(3)
    a.info("WHY\n\n" + data.get("why_today", ""))
    b.info("FORMAT\n\n" + data.get("format", ""))
    c.info("QUALITY\n\n" + data.get("quality_reason", ""))

    st.subheader("台本")
    script = data.get("script", [])
    if script:
        st.dataframe(pd.DataFrame(script), use_container_width=True, hide_index=True)

    st.subheader("ビジュアル設計")
    vd = data.get("visual_direction", {})
    st.write("**Style:**", vd.get("style", ""))
    st.write("**Camera:**", vd.get("camera", ""))
    st.write("**Color / Light:**", vd.get("color_light", ""))
    if vd.get("avoid"):
        st.write("**Avoid:**", " / ".join(vd.get("avoid", [])))

    st.subheader("生成プロンプト")
    for i, p in enumerate(data.get("image_video_prompts", []), 1):
        st.code(f"{i}. {p}", language=None)

    st.subheader("Instagram")
    st.text_area("Caption", value=data.get("caption", ""), height=140)
    st.write(" ".join(data.get("hashtags", [])))

    checks = data.get("fact_check_needed", [])
    if checks:
        st.warning("公開前に事実確認が必要:\n\n" + "\n".join(f"- {x}" for x in checks))
    else:
        st.success("明示的な事実確認項目はありません。")

    export_json = json.dumps(data, ensure_ascii=False, indent=2)
    st.download_button(
        "企画JSONを保存",
        data=export_json.encode("utf-8"),
        file_name=f"airu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True,
    )

    if st.button("この企画を履歴に採用", use_container_width=True):
        save_to_history(data)
        st.success("history.csv に追加しました。")
        st.rerun()

st.divider()
st.subheader("投稿履歴")
history = load_history()
if len(history):
    st.dataframe(history.iloc[::-1], use_container_width=True, hide_index=True)
else:
    st.caption("まだ履歴はありません。")
