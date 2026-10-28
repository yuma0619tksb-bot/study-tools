"""toeic/questions_src.json を検証して toeic/questions.json(id 付き)を書き出す。問題があれば終了コード 1。

確かめること: パート・レベル・分野が定義どおり、選択肢の数と重複なし、正解の番号が範囲内、
Part 6 の本文に [1]〜[4] がある、リスニングの台本の形、解説がある、同じ問題文の重複なし、
そして全問に検算の記録(verified が "agree" か "reviewed")があること。検算していない問題は入れない。
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "toeic"))

from taxonomy import LEVELS, N_CHOICES, SKILLS  # noqa: E402


def main():
    src = json.loads((ROOT / "toeic" / "questions_src.json").read_text(encoding="utf-8"))
    errors, out, seen, counters = [], [], set(), {}
    for n, it in enumerate(src):
        part = it.get("part")
        where = f"#{n} (Part {part})"
        if part not in SKILLS:
            errors.append(f"{where}: パートが不正"); continue
        if it.get("level") not in LEVELS:
            errors.append(f"{where}: レベルが不正 {it.get('level')}")
        qs = it.get("questions") or []
        want = {5: (1, 1), 2: (1, 1), 6: (4, 4), 7: (2, 4), 3: (3, 3), 4: (3, 3)}[part]
        if not want[0] <= len(qs) <= want[1]:
            errors.append(f"{where}: 設問数 {len(qs)} が {want} の範囲外")
        if part in (6, 7):
            text = (it.get("passage") or {}).get("text", "")
            if len(text) < 200:
                errors.append(f"{where}: 本文が短すぎる")
            if part == 6 and re.findall(r"\[(\d)\]", text) != ["1", "2", "3", "4"]:
                errors.append(f"{where}: 本文の [1]〜[4] がそろっていない")
        if part in (2, 3, 4):
            sc = it.get("script") or []
            if not sc or any(not s.get("t") or s.get("sp") not in ("M", "W", "M2", "W2") for s in sc):
                errors.append(f"{where}: 台本の形が不正")
            if part == 2 and len(sc) != 1:
                errors.append(f"{where}: Part 2 の台本は1行")
            if part == 3 and len(sc) < 4:
                errors.append(f"{where}: Part 3 の会話が短すぎる")
            if part == 4 and len({s.get("sp") for s in sc}) != 1:
                errors.append(f"{where}: Part 4 は話し手1人")
        for j, q in enumerate(qs):
            w = f"{where} 設問{j + 1}"
            ch = q.get("choices") or []
            if len(ch) != N_CHOICES[part] or len({c.strip().lower() for c in ch}) != len(ch) or any(not str(c).strip() for c in ch):
                errors.append(f"{w}: 選択肢が {N_CHOICES[part]} 個でないか重複・空がある")
            if not isinstance(q.get("answer"), int) or not 0 <= q["answer"] < len(ch):
                errors.append(f"{w}: 正解の番号が不正")
            if q.get("skill") not in SKILLS[part]:
                errors.append(f"{w}: 分野 {q.get('skill')} が Part {part} の定義にない")
            if not str(q.get("explain", "")).strip():
                errors.append(f"{w}: 解説がない")
            if q.get("verified") not in ("agree", "reviewed"):
                errors.append(f"{w}: 検算の記録がない(verified)")
            if part == 5 and q.get("q", "").count("____") != 1:
                errors.append(f"{w}: Part 5 の空所 ____ が1つでない")
            key = (part, q.get("q", "") if part in (5,) else json.dumps(it.get("script") or it.get("passage"), ensure_ascii=False)[:200] + str(j))
            if key in seen:
                errors.append(f"{w}: 同じ問題がすでにある")
            seen.add(key)
        counters[part] = counters.get(part, 0) + 1
        iid = f"t{part}_{counters[part]:03d}"
        out.append({**it, "id": iid, "questions": [{**q, "qid": f"{iid}-{j + 1}"} for j, q in enumerate(qs)]})
    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1
    (ROOT / "toeic" / "questions.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    nq = sum(len(i["questions"]) for i in out)
    by = {}
    for i in out:
        for q in i["questions"]:
            by[(i["part"], i["level"])] = by.get((i["part"], i["level"]), 0) + 1
    print(f"OK: {len(out)} セット・{nq} 問")
    for p in sorted({k[0] for k in by}):
        print(f"  Part {p}: " + " / ".join(f"{lv}: {by.get((p, lv), 0)}" for lv in LEVELS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
