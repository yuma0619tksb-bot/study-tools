#!/bin/bash
# セッション開始時に、OCR待ち・要約待ちの資料があれば Claude に知らせる。
cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0
[ -d materials ] || exit 0
python3 tools/materials.py ingest >/dev/null 2>&1 || exit 0
out=$(python3 tools/materials.py status --quiet 2>/dev/null)
if [ -f materials/drive.json ]; then
  echo "【資料の新着確認】Google Drive の「授業資料」フォルダに新しい資料が無いか、.claude/skills/materials/SKILL.md の「Google Drive からの取り込み」の手順で確認すること(Drive コネクタが使えない環境なら省略してよい)。新着があれば取り込み・OCR・要約まで行い、ユーザーに一言伝える。新着が無ければ何も言わない。"
fi
[ -z "$out" ] && exit 0
echo "【資料の未処理があります】.claude/skills/materials/SKILL.md の手順で OCR と要約を処理し、ユーザーの依頼に答える前か後に「未処理の資料を処理します」と一言伝えてから進めること。"
echo "$out"
exit 0
