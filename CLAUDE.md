# study-tools

授業資料を `materials/` で管理する。資料を読むときは**元ファイルを丸ごと読まない**。次の順で必要な分だけ読む。

## 資料の読み方(トークン節約の順番)
1. `materials/INDEX.md`(全資料の目次:科目・回・種類・一言要約)
2. `materials/<科目>/digest/<名前>.md`(要約+キーワード→ページ索引)
3. `python3 tools/materials.py search 語1 語2 --subject <科目>` で該当ページを特定
4. `materials/<科目>/text/<名前>.md` の該当 `## p.N` だけを Read(offset/limit か Grep -A で範囲を絞る)
5. 図・数式・表が崩れていて読めないときだけ、元PDFの該当ページを画像化して見る
   (`pdftoppm -r 150 -png -f N -l N <pdf> <出力>` → Read)

## 資料の入れ口
ユーザーは Google Drive の「授業資料/<科目>/」に資料を入れる(claude.ai のナレッジはこちらから読めないので使わない)。
セッション開始時のフックの指示に従って新着を確認し、`materials/<科目>/raw/` に取り込む。

## 新しい資料が入ったとき
資料の追加・更新を頼まれたら、または `status` で未処理が見つかったら `.claude/skills/materials/SKILL.md` の手順で処理する。
1. `python3 tools/materials.py ingest`
2. OCR待ちがあれば `python3 tools/materials.py ocr` → 画像を読んで text に書き込む → もう一度 ingest
3. 要約が「未作成・古い」の資料の digest を書く(テンプレート: `docs/digest-template.md`)→ ingest(INDEX に一言要約が載る)
4. Obsidian ツールが使えるなら obsidian-vault-notes スキルの手順で digest を Vault に保存する。
   使えないときは `export-obsidian` の書き出しで代用し、ユーザーに伝える。
5. commit して push(cloud セッションはコンテナが消えるため)

## 注意
- `INDEX.md` と `catalog.json` は ingest が作る。手で編集しない(種類・回の自動判定が外れたら catalog.json の該当資料に `kind_manual` / `lecture_manual` を足す)。
- text/ に書き込んだ OCR 結果は、元ファイルが変わらない限り ingest で上書きされない。
