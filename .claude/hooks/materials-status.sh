#!/bin/bash
# セッション開始時に、OCR待ち・要約待ちの資料があれば Claude に知らせる。
cd "$CLAUDE_PROJECT_DIR" 2>/dev/null || exit 0
[ -d materials ] || exit 0
python3 tools/materials.py ingest >/dev/null 2>&1 || exit 0
out=$(python3 tools/materials.py status --quiet 2>/dev/null)
[ -z "$out" ] && exit 0
echo "【資料の未処理があります】.claude/skills/materials/SKILL.md の手順で OCR と要約を処理し、ユーザーの依頼に答える前か後に「未処理の資料を処理します」と一言伝えてから進めること。"
echo "$out"
exit 0
