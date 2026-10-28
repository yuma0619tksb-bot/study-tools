"""検算の結果をもとに、下書きを toeic/questions_src.json に取り込む。

  python scripts/merge_toeic.py --drafts toeic/drafts/p5-*.json --checks toeic/drafts/check-*.json
    → すべての設問が検算と一致したセットは verified="agree" を付けて取り込む。
      1問でも食い違い・あいまいがあるセットは toeic/drafts/review-<日時>.json に出す。
  python scripts/merge_toeic.py --reviewed toeic/drafts/review-XXXX.json
    → 見直し済みのファイル(各設問に verified="reviewed" を付け、捨てるセットは削除したもの)を取り込む。
"""
import argparse
import datetime
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "toeic" / "questions_src.json"


def load_src():
    return json.loads(SRC.read_text(encoding="utf-8")) if SRC.exists() else []


def tidy(it):
    for q in it.get("questions", []):
        if it.get("part") == 5:
            q["q"] = re.sub(r"_{3,}", "____", q.get("q", ""))
        q["choices"] = [str(c).strip() for c in q.get("choices", [])]
    return it


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drafts", nargs="*", default=[])
    ap.add_argument("--checks", nargs="*", default=[])
    ap.add_argument("--reviewed")
    a = ap.parse_args()
    src = load_src()
    if a.reviewed:
        items = json.loads(pathlib.Path(a.reviewed).read_text(encoding="utf-8"))
        ok = [tidy(it) for it in items if all(q.get("verified") == "reviewed" for q in it.get("questions", []))]
        src += [{k: v for k, v in it.items() if k != "_flags"} for it in ok]
        SRC.write_text(json.dumps(src, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"見直し済み {len(ok)} セットを取り込んだ(取り込まなかった {len(items) - len(ok)} セット)")
        return
    reports = [json.loads(pathlib.Path(c).read_text(encoding="utf-8")) for c in a.checks]
    agreed, review = [], []
    for f in a.drafts:
        d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        for i, it in enumerate(d["items"]):
            it = tidy(it)
            flags = []
            for j, q in enumerate(it.get("questions", [])):
                qid = f"{pathlib.Path(f).stem}#{i}.{j}"
                rs = [r[qid] for r in reports if qid in r]
                if not rs:
                    flags.append({"q": j, "why": "検算なし"})
                for r in rs:
                    if r["solver"] != q.get("answer") or r["ambiguous"]:
                        flags.append({"q": j, "key": q.get("answer"), "solver": r["solver"], "ambiguous": r["ambiguous"], "note": r["note"], "model": r["model"]})
            if flags:
                review.append({**it, "_flags": flags})
            else:
                for q in it["questions"]:
                    q["verified"] = "agree"
                agreed.append(it)
    src += agreed
    SRC.write_text(json.dumps(src, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    rv = ROOT / "toeic" / "drafts" / f"review-{stamp}.json"
    rv.write_text(json.dumps(review, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"一致したセット {len(agreed)} を取り込み、要確認 {len(review)} セットを {rv.relative_to(ROOT)} に出した")


if __name__ == "__main__":
    main()
