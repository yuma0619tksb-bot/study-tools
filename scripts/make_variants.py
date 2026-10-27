"""×や△だった問題の類題(同じ出題枠で数値を変えたもの)を、検算に通ったものだけ追加する。

使い方:
  python scripts/make_variants.py k024 b013          # 各問題につき1題ずつ
  python scripts/make_variants.py k024 --per 2       # 2題ずつ
その後 python scripts/build.py && python scripts/verify.py を実行する。

追加先は problem_bank/variants.json(型・レベル・パラメータをそのまま保存)。
数値の選択肢を使い切った枠は「作れなかった」と表示して飛ばす。
"""
import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from problem_bank import core  # noqa: E402
from problem_bank.bank import VARIANTS_FILE, base_specs, build, load_variants, module_for, render_one  # noqa: E402

MAX_TRIES = 300


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--per", type=int, default=1)
    a = ap.parse_args()

    problems, pmap = build()
    seen = {p["question"] for p in problems}
    variants = load_variants()
    added, failed = [], []
    for pid in a.ids:
        if pid not in pmap:
            print(f"{pid}: そのような問題はない")
            failed.append(pid)
            continue
        entry = pmap[pid]
        mod = module_for(pid[0])
        made = 0
        for s in range(1, MAX_TRIES + 1):
            if made >= a.per:
                break
            kname, level, params = base_specs(mod, f"-v{s}")[entry["family"]]
            if kname != entry["kind"]:
                continue
            fields, value = render_one(kname, params)
            if fields["question"] in seen:
                continue
            kd = core.REGISTRY[kname]
            try:
                ok = kd.same(value, kd.check(params))
            except Exception as e:  # noqa: BLE001
                ok = False
                print(f"{pid}: 検算で例外が出た候補を捨てた (seed {s}): {e}")
            if not ok:
                print(f"{pid}: 検算に通らない候補を捨てた (seed {s})")
                continue
            seen.add(fields["question"])
            variants.append({"source": pid, "family": entry["family"], "kind": kname, "level": level, "params": params})
            made += 1
            added.append((pid, fields["question"]))
        if made < a.per:
            failed.append(pid)
    VARIANTS_FILE.write_text(json.dumps(variants, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for pid, q in added:
        print(f"+ {pid} の類題: {q[:60]}…")
    if failed:
        print("作れなかった(数値の選択肢を使い切った、または固定の問題): " + ", ".join(failed))
    print(f"{len(added)} 題を problem_bank/variants.json に追加した。次に build.py と verify.py を実行すること。")


if __name__ == "__main__":
    main()
