"""下書きの問題を、作ったのとは別の Gemini モデルに「答えを見せずに」解かせて食い違いを洗い出す。

使い方: python scripts/crosscheck_toeic.py toeic/drafts/p5-*.json ... [--model gemini-flash-lite-latest]
結果: toeic/drafts/check-<日時>.json に、問題ごとの {key, solver, ambiguous, note} を保存し、
食い違い・あいまいと判定された問題だけを画面に出す(それを Claude が見直す)。
"""
import argparse
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "toeic"))

from gemini import generate_json  # noqa: E402

PROMPT = """You are an expert TOEIC test-taker and item reviewer. Solve each question below WITHOUT any answer key.
For each question return: {"id": "<id>", "answer": <0-based index of the single best choice>, "ambiguous": <true if two or more choices could reasonably be correct, or none is correct>, "note": "<if ambiguous: which choices and why, in <=25 words; else empty>"}.
For listening items the "script" is what the student hears; Part 2 choices are spoken responses.
Output ONLY a JSON array with one object per question id, in the same order.

QUESTIONS:
"""


def blind(files):
    out, keys = [], {}
    for f in files:
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        items = d["items"] if isinstance(d, dict) else d
        for i, it in enumerate(items):
            ctx = {}
            if it.get("passage"):
                ctx["passage"] = it["passage"].get("text", "")
            if it.get("script"):
                ctx["script"] = " / ".join(f'{s.get("sp")}: {s.get("t")}' for s in it["script"])
            for j, q in enumerate(it.get("questions", [])):
                qid = f"{pathlib.Path(f).stem}#{i}.{j}"
                keys[qid] = q.get("answer")
                out.append({"id": qid, "part": it.get("part"), **ctx, "question": q.get("q", ""),
                            "choices": [f"({chr(65 + k)}) {c}" for k, c in enumerate(q.get("choices", []))]})
                ctx = {"same_text_as_previous": True}  # 同じ本文は1回だけ送る(トークン節約)
    return out, keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--model", default="gemini-3-flash-preview")
    a = ap.parse_args()
    qs, keys = blind(a.files)
    res, model = generate_json(PROMPT + json.dumps(qs, ensure_ascii=False), models=[a.model, "gemini-3.5-flash", "gemini-3.7-flash"], temperature=0.0)
    by = {r.get("id"): r for r in res if isinstance(r, dict)}
    report, bad = {}, []
    for qid, k in keys.items():
        r = by.get(qid, {})
        rep = {"key": k, "solver": r.get("answer"), "ambiguous": bool(r.get("ambiguous")), "note": r.get("note", ""), "model": model}
        report[qid] = rep
        if rep["solver"] != k or rep["ambiguous"]:
            bad.append(qid)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = ROOT / "toeic" / "drafts" / f"check-{stamp}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(keys)} 問を {model} で検算: 一致 {len(keys) - len(bad)} / 要確認 {len(bad)} → {out.relative_to(ROOT)}")
    for qid in bad:
        r = report[qid]
        print(f"  {qid}: 正解キー {r['key']} / 検算 {r['solver']}{' あいまい' if r['ambiguous'] else ''} {r['note']}")


if __name__ == "__main__":
    main()
