
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

重要:
- 過去のAIるの世界観・デザイン・投稿形式には縛られない。
- 毎回同じ「問い→結論」の型にしなくてよい。
- 15〜35秒程度のInstagram Reelsを中心に考える。
- 単なるAI豆知識、薄い名言、既視感の強い自己啓発にしない。
- 見た人が一瞬止まり、考えたくなる切り口を優先する。
- 人間、意識、記憶、時間、社会、未来、テクノロジー、自然、孤独、愛、死生観、選択など幅広く扱える。
- 科学的・歴史的事実を使う場合、断定しすぎず、要検証事項を明示する。
- 医療、法律、金融の個別助言をしない。
- 差別、誹謗中傷、危険行為を助長しない。
- 「AIだから正しい」という態度を取らない。
- 量産AIコンテンツに見えない、映像として魅力のある企画を目指す。

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

    past_themes = history["theme"].dropna().astype(str).tolist()[-100:]
    history_text = "\n".join(f"- {x}" for x in past_themes) if past_themes else "まだありません。"

    prompt = f"""
以下の条件で、今日のInstagram Reels企画を1本作ってください。

今日の方向性: {category}
希望トーン: {tone}

過去テーマ:
{history_text}

過去テーマと意味がほぼ同じ企画は避けてください。
テーマだけでなく、切り口・見せ方にも新鮮さを出してください。

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
  "image_video_prompts": [
    "生成AI向けの具体的な映像または画像プロンプト"
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
