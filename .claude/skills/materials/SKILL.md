---
name: materials
description: materials/ に入れた授業資料(PDF・スキャン・画像・Word・PowerPoint・過去問)を取り込み、OCR・要約(digest)・目次更新・Obsidian保存まで行う。「資料を入れた」「資料を追加した」「この資料を読んで」「〇〇はどの資料に載ってる?」と言われたとき、または資料について質問されたときに使う。
---

# 授業資料の取り込みと読み方

## 取り込み
1. 元ファイルが `materials/<科目>/raw/` にあるか確認する(なければユーザーに科目名を聞いてそこへ移す)。
2. `python3 tools/materials.py ingest` → `python3 tools/materials.py status`
3. **OCR待ち**: `python3 tools/materials.py ocr --subject <科目>` で出た画像を Read で読み、
   `text/<名前>.md` の `## p.N` の直後にある `[OCR待ち] …` の行を、書き起こした本文に置き換える。
   - 数式は LaTeX(`$...$`)、表は Markdown 表、図は `[図: 何を示すか]` と一行で説明する。
   - 読めない箇所は `[判読不能]` と書き、推測で埋めない。
   - ページ数が多い(目安20ページ超)ときは、gemini-pdf-digest スキルが使えるなら先にそちらを検討する。
4. **digest**: `docs/digest-template.md` の形で `materials/<科目>/digest/<名前>.md` を書く。
   - `sha1` は catalog.json の値を写す。text は必要なページだけ読んでよい(目次・まとめのページを優先)。
   - 過去問は「キーワード→ページ」の代わりに「大問ごとの分野・使う道具・関連する講義回」を書く。
5. もう一度 `ingest` して INDEX.md に一言要約が載ったことを確認する。
6. Obsidian: `obsidian_` ツールがあれば obsidian-vault-notes スキルの手順で、科目フォルダに digest を保存し目次を更新する。
   なければ `python3 tools/materials.py export-obsidian` を実行し、`exports/obsidian/` に書き出したと伝える。
7. commit・push する。

## 質問に答えるとき
CLAUDE.md の「資料の読み方」の順(INDEX → digest → search → 該当ページ)で読み、回答には出典を `(<資料名> p.N)` の形で添える。
資料に載っていないことを答えるときは、そう明記する。

## claude.ai プロジェクトへ渡すとき
`python3 tools/materials.py bundle --subject <科目>` で `exports/claude_project/<科目>/` を作り、
中身(00_資料目次.md と各資料の .md)をプロジェクトのナレッジにアップするよう案内する。元PDFより軽く、ページ番号付きで引用できる。
指示文に貼る定型文は `docs/claude-project-instructions.md`。
