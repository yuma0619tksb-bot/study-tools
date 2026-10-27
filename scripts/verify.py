"""output/problems.json を検証する。1つでも問題があれば終了コード 1 で止まる。

検証内容
  1. JSON の形式: 必須キーちょうど・型・id の一意性と接頭辞・order の一意性・
     基本の問題数 80〜100(類題は別に数える)・$ の対応・{ } と \\left \\right の対応・問題文の重複なし
  2. 再現性: output/params.json の型とパラメータから問題を作り直し、
     保存されている title / level / question / tool / steps / answer と完全一致するか
  3. 検算: 各問題の答えを解答とは別ルート(厳密な部分和、数値微分、
     数値積分、常微分方程式、サイクルの模擬計算など)で求め直して一致するか
  4. 物理: 答えに出てくる数値がすべて、別ルートで求めた値の有効数字3桁表記か
  5. 決定性: 生成器をもう一度動かすと保存済みの JSON とバイト単位で同じになるか

使い方: python scripts/verify.py
"""
import collections
import json
import pathlib
import re
import sys
import traceback

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from problem_bank import core  # noqa: E402
from problem_bank.bank import build, modules, render_one  # noqa: E402

KEYS = {"id", "order", "subject", "title", "level", "question", "tool", "steps", "answer"}
SUBJECTS = {"解析学": "k", "微積第二": "b", "物理学概論第二": "p"}
TEXT_FIELDS = ["title", "question", "tool", "answer"]


def unescaped_dollars(s):
    return len(re.findall(r"(?<!\\)\$", s))


def check_tex(s, where, errors):
    if unescaped_dollars(s) % 2:
        errors.append(f"{where}: $ の数が奇数")
    depth = 0
    for c in re.sub(r"\\[{}]", "", s):
        depth += c == "{"
        depth -= c == "}"
        if depth < 0:
            break
    if depth != 0:
        errors.append(f"{where}: {{ }} の対応がとれていない")
    if s.count(r"\left") != s.count(r"\right"):
        errors.append(f"{where}: \\left と \\right の数が違う")


def validate_schema(problems, errors):
    if not isinstance(problems, list):
        errors.append("トップレベルが配列ではない")
        return
    if len(problems) < 80:
        errors.append(f"問題数が 80 未満: {len(problems)}")
    ids, orders, questions = set(), set(), set()
    for i, p in enumerate(problems):
        where = p.get("id", f"#{i}") if isinstance(p, dict) else f"#{i}"
        if not isinstance(p, dict):
            errors.append(f"{where}: オブジェクトではない")
            continue
        if set(p) != KEYS:
            errors.append(f"{where}: キーが違う(過不足: {sorted(set(p) ^ KEYS)})")
            continue
        if not isinstance(p["id"], str) or not re.fullmatch(r"[kbp]\d{3}", p["id"]):
            errors.append(f"{where}: id の形式が不正")
        if p["subject"] not in SUBJECTS:
            errors.append(f"{where}: subject が不正 {p['subject']!r}")
        elif not p["id"].startswith(SUBJECTS[p["subject"]]):
            errors.append(f"{where}: id の接頭辞が subject と合わない")
        if p["id"] in ids:
            errors.append(f"{where}: id が重複")
        ids.add(p["id"])
        if type(p["order"]) is not int:
            errors.append(f"{where}: order が整数でない")
        elif p["order"] in orders:
            errors.append(f"{where}: order が重複")
        orders.add(p["order"])
        if type(p["level"]) is not int or p["level"] not in (1, 2, 3):
            errors.append(f"{where}: level が 1|2|3 でない")
        for k in TEXT_FIELDS:
            if not isinstance(p[k], str) or not p[k].strip():
                errors.append(f"{where}: {k} が空または文字列でない")
            else:
                check_tex(p[k], f"{where}.{k}", errors)
        if not isinstance(p["steps"], list) or not p["steps"]:
            errors.append(f"{where}: steps が空または配列でない")
        else:
            for j, s in enumerate(p["steps"]):
                if not isinstance(s, str) or not s.strip():
                    errors.append(f"{where}.steps[{j}]: 空または文字列でない")
                else:
                    check_tex(s, f"{where}.steps[{j}]", errors)
        if p["question"] in questions:
            errors.append(f"{where}: 同じ問題文がすでにある")
        questions.add(p["question"])


NUM = re.compile(r"-?\d+(?:\.\d+)?(?:\\times 10\^\{-?\d+\})?")


def physics_numbers(answer, values, where, errors):
    allowed = set()
    for v in values:
        for w in (v, v * 100):
            allowed.add(core.sig3(w))
    # 単位 \mathrm{...} の中の数字(m^3 など)は除く
    body = re.sub(r"\\mathrm\{[^}]*\}", "", answer)
    body = re.sub(r"_(\{[^}]*\}|\w)", "", body)  # T_2 などの添字
    for tok in NUM.findall(body):
        if tok not in allowed:
            errors.append(f"{where}: 答えの数値 {tok} が検算値の有効数字3桁表記 {sorted(allowed)} にない")


def main():
    errors = []
    out = ROOT / "output"
    try:
        problems = json.loads((out / "problems.json").read_text(encoding="utf-8"))
        pmap = json.loads((out / "params.json").read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print(f"FAIL: JSON を読めない: {e}")
        return 1

    validate_schema(problems, errors)
    modules()  # 全モジュールを読み込んで REGISTRY を埋める

    base = [k for k, v in pmap.items() if not v.get("variant_of")]
    if not 80 <= len(base) <= 100:
        errors.append(f"基本の問題数が 80〜100 の範囲外: {len(base)}")
    for k, v in pmap.items():
        if v.get("variant_of") and v["variant_of"] not in pmap:
            errors.append(f"{k}: 類題の元 {v['variant_of']} が見つからない")
    ids = [p.get("id") for p in problems if isinstance(p, dict)]
    if set(ids) != set(pmap):
        errors.append(f"params.json の id が problems.json と一致しない: {sorted(set(ids) ^ set(pmap))}")

    for p in problems:
        pid = p.get("id")
        if pid not in pmap:
            continue
        entry = pmap[pid]
        kname, params = entry["kind"], entry["params"]
        if kname not in core.REGISTRY:
            errors.append(f"{pid}: 未知の型 {kname}")
            continue
        kd = core.REGISTRY[kname]
        try:
            fields, value = render_one(kname, params)
        except Exception:  # noqa: BLE001
            errors.append(f"{pid}: 再生成に失敗\n{traceback.format_exc()}")
            continue
        for k in ["title", "question", "tool", "steps", "answer"]:
            if fields[k] != p.get(k):
                errors.append(f"{pid}: {k} が保存値と違う\n  保存: {p.get(k)!r}\n  再生成: {fields[k]!r}")
        if entry.get("level") != p.get("level"):
            errors.append(f"{pid}: level が params.json と違う")
        try:
            independent = kd.check(params)
        except Exception:  # noqa: BLE001
            errors.append(f"{pid}: 検算で例外\n{traceback.format_exc()}")
            continue
        if not kd.same(value, independent):
            errors.append(f"{pid}: 答えが検算と一致しない\n  解答側: {value}\n  検算側: {independent}")
        if pid.startswith("p"):
            physics_numbers(p["answer"], [float(v) for v in independent], pid, errors)

    try:
        regen, regen_map = build()
        if regen != problems or regen_map != json.loads(json.dumps(regen_map)) or regen_map != pmap:
            errors.append("生成器の出力が保存済み JSON と一致しない(scripts/build.py を実行し直すこと)")
    except Exception:  # noqa: BLE001
        errors.append(f"再生成に失敗\n{traceback.format_exc()}")

    cnt = collections.Counter((p.get("subject"), p.get("level")) for p in problems if isinstance(p, dict))
    print("科目別・レベル別の問題数")
    for subj in SUBJECTS:
        row = [cnt[(subj, lv)] for lv in (1, 2, 3)]
        print(f"  {subj}: 計 {sum(row)} (Lv1 {row[0]} / Lv2 {row[1]} / Lv3 {row[2]})")
    print(f"  合計: {len(problems)}")

    if errors:
        print(f"\nFAIL: {len(errors)} 件の問題")
        for e in errors:
            print(" -", e)
        return 1
    print("\nOK: 形式・再現性・検算・決定性のすべてを通過")
    return 0


if __name__ == "__main__":
    sys.exit(main())
