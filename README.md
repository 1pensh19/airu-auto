
# AIる AUTO PROJECT — Ver.1

AIが人間・世界・未来について、毎日ひとつ考えるInstagram企画を自動生成するMVPです。

## V1でできること

- 過去テーマを読み込む
- 新しいテーマを1つ選ぶ
- 冒頭フックを作る
- 15〜35秒のReels構成を作る
- 台本を作る
- ビジュアル方針を作る
- 画像・動画生成用プロンプトを作る
- Instagramキャプションとハッシュタグを作る
- 事実確認が必要な主張を明示する
- 採用した企画を history.csv に保存する

V1では画像生成、動画生成、Instagram自動投稿はまだ実行しません。

## 必要なもの

- PC（Mac / Windows）
- Python 3.10以上推奨
- OpenAI API key

注意: ChatGPT PlusとOpenAI APIの料金は別です。APIは使用量に応じて課金されます。

## 起動

ターミナルでこのフォルダに移動し、

```bash
pip install -r requirements.txt
streamlit run app.py
```

ブラウザが開いたら、左側にOpenAI API Keyを入力します。

環境変数を使う場合:

Mac / Linux:

```bash
export OPENAI_API_KEY="YOUR_KEY"
streamlit run app.py
```

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="YOUR_KEY"
streamlit run app.py
```

## ファイル

- app.py : 本体
- history.csv : 採用した過去テーマと成績を保存
- generation_log.jsonl : 生成履歴（初回生成後に作成）
- requirements.txt : 必要ライブラリ

## 次のVer.2候補

- 画像生成APIとの接続
- AIによる画像品質チェック
- 9:16素材の自動生成
- 投稿候補を3案作ってAIが自己採点
- Web検索を使った事実確認
- Instagram投稿APIへの接続
- 投稿結果を自動取得し、次回企画へ反映
