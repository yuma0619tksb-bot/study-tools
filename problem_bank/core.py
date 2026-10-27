"""共通ユーティリティ: TeX 整形、有効数字、数値チェック、問題レジストリ。"""
import math
import re
import random

import mpmath
import sympy as sp

mpmath.mp.dps = 50

n = sp.Symbol("n", integer=True, positive=True)
x, y, z, t = sp.symbols("x y z t", real=True)
N = sp.Symbol("N", integer=True, positive=True)


# ---------------------------------------------------------------- TeX
def _dfrac_outside_scripts(s):
    """上付き・下付きの中以外の \\frac を \\dfrac に置き換える(スマホで読みやすくするため)。"""
    out, i, stack = [], 0, []  # stack: 各 { が script 由来かどうか
    pending_script = False
    while i < len(s):
        c = s[i]
        if c in "^_":
            pending_script = True
            out.append(c)
            i += 1
            continue
        if c == "{":
            stack.append(pending_script)
            pending_script = False
            out.append(c)
            i += 1
            continue
        pending_script = False
        if c == "}":
            if stack:
                stack.pop()
            out.append(c)
            i += 1
            continue
        if s.startswith(r"\frac", i) and not any(stack):
            out.append(r"\dfrac")
            i += len(r"\frac")
            continue
        out.append(c)
        i += 1
    return "".join(out)


def tex(e, **kw):
    if isinstance(e, str):
        return e
    e = sp.sympify(e)
    s = sp.latex(e, **kw)
    if "^{- " in s and not e.is_Add:
        num, den = sp.fraction(e)
        if den != 1:
            s = r"\frac{%s}{%s}" % (sp.latex(num, **kw), sp.latex(den, **kw))
    s = s.replace(r"\operatorname{atan}", r"\arctan")
    s = re.sub(r"\^\{\\frac\{(\d+)\}\{(\d+)\}\}", r"^{\1/\2}", s)
    s = re.sub(r"\\log\{\\left\((\w+) \\right\)\}(?!\^)", r"\\log \1", s)
    s = re.sub(r"\\(log|sin|cos|tan|arctan)\{\\left\(([^{}]*?) \\right\)\}", r"\\\1\\left(\2\\right)", s)
    s = s.replace("n!^{2}", r"\left(n!\right)^{2}")
    s = re.sub(r"\\log\\left\((\w)\\right\)\^\{2\}", r"\\left(\\log \1\\right)^{2}", s)
    return _dfrac_outside_scripts(s)


def ptex(e):
    """和の一部として書くときに必要なら括弧でくくる。"""
    e = sp.sympify(e)
    return r"\left(%s\right)" % tex(e) if (e.is_Add or e.could_extract_minus_sign()) else tex(e)


def btex(e):
    """累乗の底として書くときに必要なら括弧でくくる。"""
    e = sp.sympify(e)
    return tex(e) if (e.is_Integer and e >= 0) or e.is_Symbol else r"\left(%s\right)" % tex(e)


def m(e):
    """インライン TeX($...$)にする。"""
    return f"${tex(e)}$"


# ---------------------------------------------------------------- 有効数字
def round_sig(v, k=3):
    if v == 0:
        return 0.0
    mant, ex = f"{v:.{k-1}e}".split("e")
    return float(mant) * 10 ** int(ex)


def sig3(v, unit="", k=3):
    """有効数字 k 桁(既定3桁)の TeX 文字列。|v|>=1000 は指数表記。"""
    if v == 0:
        body = "0"
    else:
        mant, ex = f"{v:.{k-1}e}".split("e")
        ex = int(ex)
        if -3 <= ex <= 2:
            body = f"{float(mant) * 10 ** ex:.{max(0, k - 1 - ex)}f}"
        else:
            body = rf"{mant}\times 10^{{{ex}}}"
    if unit:
        body += rf"\ \mathrm{{{unit}}}"
    return body


def parse_sig(s):
    """sig3 の出力(単位なし部分)を float に戻す。"""
    s = s.split(r"\ ")[0]
    if r"\times" in s:
        mant, ex = s.split(r"\times 10^")
        return float(mant) * 10 ** int(ex.strip("{}"))
    return float(s)


# ---------------------------------------------------------------- 数値チェック
def num_close(a, b, rel=1e-9, abs_=1e-12):
    return abs(a - b) <= max(abs_, rel * max(abs(a), abs(b)))


def assert_close(a, b, what, rel=1e-9):
    if not num_close(float(a), float(b), rel=rel):
        raise AssertionError(f"{what}: {a} != {b}")


def assert_sym_eq(a, b, what):
    d = sp.simplify(sp.sympify(a) - sp.sympify(b))
    if d != 0:
        # 数値でも確かめる(simplify が弱い場合の保険)
        fs = sorted((sp.sympify(a) - sp.sympify(b)).free_symbols, key=str)
        rng = random.Random(0)
        for _ in range(6):
            sub = {s: sp.Rational(rng.randint(11, 29), 10) for s in fs}
            val = complex(sp.N((sp.sympify(a) - sp.sympify(b)).subs(sub), 30))
            if abs(val) > 1e-20:
                raise AssertionError(f"{what}: {a} != {b}")


def limit_numeric(expr, var, big=10**8):
    """大きな var での値(mpmath 高精度)。極限の数値的な裏付けに使う。"""
    f = sp.lambdify(var, expr, "mpmath")
    return float(f(mpmath.mpf(big)))


# ---------------------------------------------------------------- 問題の型
class Kind:
    """問題の型。render(params)->(fields, value), check(params)->value を持つ。"""

    def __init__(self, name, render, check, same=None):
        self.name, self.render, self.check = name, render, check
        self.same = same or (lambda a, b: a == b)


REGISTRY = {}


def kind(name, check, same=None):
    def deco(render):
        REGISTRY[name] = Kind(name, render, check, same)
        return render

    return deco


def sym_same(a, b):
    try:
        assert_sym_eq(a, b, "")
        return True
    except AssertionError:
        return False


def tuple_same(a, b):
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(tuple_same(p, q) for p, q in zip(a, b))
    if isinstance(a, float) or isinstance(b, float):
        return num_close(float(a), float(b), rel=1e-6)
    if isinstance(a, sp.Basic) or isinstance(b, sp.Basic):
        return sym_same(a, b)
    return a == b


def R(s):
    """params の文字列 '1/2' などを SymPy の数にする。"""
    return sp.Rational(s) if isinstance(s, (int, str)) else s
