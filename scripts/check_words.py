"""toeic/words_src.py を検証して toeic/words.json を書き出す。問題があれば終了コード 1。

確かめること: 単語の重複なし、例文に [ ] がちょうど1つ、[ ] の中が見出し語の変化形、
誤答が3つで互いに違い答えとも違う、大文字小文字が答えとそろっている、訳と意味が空でない。
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "toeic"))

import words_src  # noqa: E402

POS = {"名", "動", "形", "副", "前"}


def stem_ok(word, form):
    w, f = word.lower(), form.lower()
    if f.startswith(w):
        return True
    # apply→applied, supply→supplies, cancel→canceled など
    for cut in (1, 2):
        if len(w) > 4 and f.startswith(w[:-cut]):
            return True
    return False


def main():
    errors, out, seen = [], [], set()
    for band, rows in ((600, words_src.B600), (730, words_src.B730), (860, words_src.B860)):
        for i, (w, pos, ja, s, sja, d) in enumerate(rows, start=1):
            where = f"{band}/{w}"
            if w.lower() in seen:
                errors.append(f"{where}: 単語が重複")
            seen.add(w.lower())
            if pos not in POS:
                errors.append(f"{where}: 品詞が不正 {pos}")
            m = re.findall(r"\[([^\]]+)\]", s)
            if len(m) != 1:
                errors.append(f"{where}: 例文の [ ] が1つでない")
                continue
            form = m[0]
            if not stem_ok(w, form):
                errors.append(f"{where}: [ ] の中 {form} が見出し語の形でない")
            if len(d) != 3 or len(set(x.lower() for x in d)) != 3 or form.lower() in (x.lower() for x in d):
                errors.append(f"{where}: 誤答が不正 {d}")
            if any(x[0].isupper() != form[0].isupper() for x in d):
                errors.append(f"{where}: 誤答の大文字小文字が答えとそろっていない")
            if not ja.strip() or not sja.strip():
                errors.append(f"{where}: 意味か訳が空")
            out.append({"id": f"w{band}_{i:02d}", "w": w, "pos": pos, "ja": ja, "s": s, "sja": sja, "d": d, "band": band})
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    (ROOT / "toeic" / "words.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"OK: {len(out)} 語(600: {len(words_src.B600)}, 730: {len(words_src.B730)}, 860: {len(words_src.B860)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
