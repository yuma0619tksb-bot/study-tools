"""output/problems.json(と検算用の output/params.json)を決定的に再生成する。

使い方: python scripts/build.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from problem_bank.bank import build  # noqa: E402


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def main():
    problems, pmap = build()
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    (out / "problems.json").write_text(dump(problems), encoding="utf-8")
    (out / "params.json").write_text(dump(pmap), encoding="utf-8")
    print(f"{len(problems)} 問を書き出した: output/problems.json, output/params.json")


if __name__ == "__main__":
    main()
