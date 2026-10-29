# study-tools

学習用ツール置き場。

## 授業資料の管理(materials/)

```
materials/
  INDEX.md               全資料の目次(自動生成)— Claudeは最初にここを読む
  catalog.json           目録(自動生成)
  <科目>/raw/            ← 元ファイルをここに入れる(PDF・画像・docx・pptx・doc/ppt、サブフォルダ可)
  <科目>/text/<名前>.md  ページ単位のテキスト(## p.N)。スキャンは [OCR待ち]
  <科目>/digest/<名前>.md 要約+キーワード→ページ索引(Claudeが書く)
```

ファイル名に「第3回」「lec03」などがあれば回数を、「過去問・試験・期末」「課題・レポート」などがあれば種類を自動で判定する。

### 使い方
1. Google Drive の「授業資料」フォルダに科目名のフォルダを作り、その中に資料を入れる
   (次に Claude Code を開いたとき、Claude が新着を取り込む。GitHub の `materials/<科目>/raw/` に直接 push してもよい)
2. Claude Code に「資料を入れた」と言う → 取り込み・OCR・要約・目次更新・Obsidian保存まで行う
3. 以降は「〇〇はどこに載ってる?」「第3回の要点は?」などと聞けば、目次→要約→該当ページだけ読んで答える

### コマンド
| コマンド | 内容 |
|---|---|
| `python3 tools/materials.py ingest` | 新規・更新ファイルだけテキスト化し、目次を更新 |
| `python3 tools/materials.py status` | 要約待ち・OCR待ちの一覧 |
| `python3 tools/materials.py search 語1 語2 [--subject 科目]` | 全語を含むページを検索 |
| `python3 tools/materials.py ocr` | OCR待ちページを画像化(Claudeが読んで書き起こす) |
| `python3 tools/materials.py export-obsidian [--out Vaultのパス]` | 要約をObsidianノートとして書き出し |
| `python3 tools/materials.py bundle [--subject 科目]` | claude.aiプロジェクトのナレッジ用一式を `exports/claude_project/` に作成 |

claude.ai プロジェクト側の指示に貼る定型文: `docs/claude-project-instructions.md`

### 自動化
- **GitHub Actions**(`.github/workflows/materials.yml`):main に `materials/<科目>/raw/` の資料が push されると、テキスト化と目次の更新を自動で行い commit する。claude.ai プロジェクト用一式は、Actions の実行結果ページから `claude_project` としてダウンロードできる(30日保存)。
- **起動時フック**(`.claude/settings.json`):Claude Code のセッションを開くと未処理(OCR待ち・要約待ち)を確認し、あれば Claude が自動で処理する。
