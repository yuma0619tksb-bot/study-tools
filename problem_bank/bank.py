"""全科目の問題を決定的に生成する。"""
import random

from . import core

SEED = 20261027


def modules():
    from . import kaiseki, bisekibun2, butsuri2

    return [kaiseki, bisekibun2, butsuri2]


def render_one(kind_name, params):
    fields, value = core.REGISTRY[kind_name].render(params)
    return fields, value


def build():
    """(problems, params_map) を返す。problems は JSON 出力そのもの。"""
    problems, pmap = [], {}
    order = 0
    for mod in modules():
        rng = random.Random(f"{SEED}-{mod.PREFIX}")
        for i, (kname, level, params) in enumerate(mod.specs(rng), start=1):
            fields, _ = render_one(kname, params)
            order += 1
            pid = f"{mod.PREFIX}{i:03d}"
            problems.append({
                "id": pid,
                "order": order,
                "subject": mod.SUBJECT,
                "title": fields["title"],
                "level": level,
                "question": fields["question"],
                "tool": fields["tool"],
                "steps": fields["steps"],
                "answer": fields["answer"],
            })
            pmap[pid] = {"kind": kname, "level": level, "params": params}
    return problems, pmap
