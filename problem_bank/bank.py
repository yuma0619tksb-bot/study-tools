"""全科目の問題を決定的に生成する。

基本の問題は各科目モジュールの specs(rng) から作る。
類題(variants.json)は「元の問題と同じ出題枠(family)を別の乱数で作り直したもの」で、
型とパラメータをそのまま保存してあるので、何度 build しても同じ問題になる。
"""
import json
import pathlib
import random

from . import core

SEED = 20261027
VARIANTS_FILE = pathlib.Path(__file__).with_name("variants.json")

# 理解度を単元ごとに集計するための単元名
UNITS = {
    "k_tel_a": "望遠鏡和", "k_tel_b": "望遠鏡和", "k_tel_quad": "望遠鏡和", "k_tel_c": "望遠鏡和",
    "k_log_div": "望遠鏡和", "k_log_prod": "望遠鏡和", "k_fact_tel": "望遠鏡和",
    "k_ratio": "収束判定", "k_ratio_e": "収束判定", "k_root": "収束判定", "k_comp": "収束判定",
    "k_alt": "絶対収束・条件収束", "k_alt_param": "絶対収束・条件収束",
    "k_param_an": "パラメータの場合分け", "k_param_np": "パラメータの場合分け", "k_param_a2n": "パラメータの場合分け",
    "b_pd": "偏微分", "b_pd_pt": "偏微分",
    "b_chain_t": "連鎖律", "b_chain_uv": "連鎖律", "b_chain_polar": "連鎖律",
    "b_tp": "接平面", "b_tp_imp": "接平面", "b_tp_par": "接平面",
    "b_lim_exist": "2変数の極限(存在する)", "b_lim_none": "2変数の極限(存在しない)",
    "b_high": "高階偏導関数", "b_td": "全微分", "b_td_approx": "全微分", "b_td_err": "全微分",
    "p_latent": "エントロピー", "p_heat": "エントロピー", "p_ice_water": "エントロピー", "p_mix": "エントロピー",
    "p_U": "内部エネルギーと第1法則", "p_isochoric": "内部エネルギーと第1法則", "p_isobaric": "内部エネルギーと第1法則",
    "p_carnot": "カルノー機関", "p_carnot_raise": "カルノー機関",
    "p_iso": "等温変化", "p_adia": "断熱変化",
    "r_forced": "強制振動・減衰振動", "r_forced_cos": "強制振動・減衰振動", "r_resonance": "強制振動・減衰振動", "r_damped": "強制振動・減衰振動",
    "r_tube": "回転する座標(円管)", "r_tube_work": "回転する座標(円管)",
    "r_elevator": "慣性力", "r_turntable": "慣性力", "r_disk_walk": "慣性力",
    "r_reduced": "2体問題・換算質量", "r_twobody_rot": "2体問題・換算質量", "r_twobody_vib": "2体問題・換算質量",
    "r_system": "質点系と衝突", "r_collision": "質点系と衝突",
    "r_pend": "連成振動", "r_springs3": "連成振動", "r_unequal": "連成振動", "r_beats": "連成振動",
}


def unit_of(kind_name, params):
    if kind_name == "k_radius":
        return "収束半径(x²ⁿ型)" if params.get("k", 1) > 1 else "収束半径"
    return UNITS[kind_name]


def modules():
    from . import kaiseki, bisekibun2, butsuri2, rikigaku

    return [kaiseki, bisekibun2, butsuri2, rikigaku]


def module_for(prefix):
    return {m.PREFIX: m for m in modules()}[prefix]


def render_one(kind_name, params):
    fields, value = core.REGISTRY[kind_name].render(params)
    return fields, value


def base_specs(mod, tag=""):
    """出題枠の一覧。tag を変えると同じ枠で数値だけ違う問題になる。"""
    return mod.specs(random.Random(f"{SEED}-{mod.PREFIX}{tag}"))


def load_variants():
    try:
        return json.loads(VARIANTS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []


def build():
    """(problems, params_map) を返す。problems は JSON 出力そのもの。"""
    problems, pmap = [], {}
    order = 0
    variants = load_variants()
    for mod in modules():
        entries = [(k, lv, p, fam, None) for fam, (k, lv, p) in enumerate(base_specs(mod))]
        entries += [(v["kind"], v["level"], v["params"], v["family"], v["source"])
                    for v in variants if v["source"][0] == mod.PREFIX]
        for i, (kname, level, params, family, source) in enumerate(entries, start=1):
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
            pmap[pid] = {"kind": kname, "level": level, "params": params, "family": family,
                         "unit": unit_of(kname, params), "variant_of": source}
    return problems, pmap
