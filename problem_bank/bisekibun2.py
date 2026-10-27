"""微積第二: 偏微分・連鎖律・接平面・2変数の極限・高階偏導関数・全微分。

答えは SymPy の微分で求め、check では mpmath の数値微分や
「代入してから直接微分する」別ルートで求め直す。
"""
import random

import mpmath
import sympy as sp

from .core import kind, m, ptex, tex, tuple_same, x, y, z, t

SUBJECT = "微積第二"
PREFIX = "b"

mpmath.mp.dps = 40
r_, th = sp.symbols("r theta", positive=True)
u_, v_ = sp.symbols("u v", real=True)
mm = sp.Symbol("m", real=True)


def parse(e, extra=None):
    loc = {"x": x, "y": y, "z": z, "t": t, "u": u_, "v": v_, "r": r_, "theta": th, "m": mm}
    return sp.sympify(e, locals=loc)


def nice(e):
    """いくつかの簡約形のうち TeX が一番短いものを選ぶ。"""
    cands = [e, sp.simplify(e), sp.factor(e), sp.expand(e), sp.together(e)]
    num, den = sp.fraction(sp.together(e))
    if den != 1:
        cands.append(sp.expand(num) / sp.factor(den))
    cands = [c for c in cands if sp.simplify(c - e) == 0]
    return min(cands, key=lambda c: (len(tex(c)), sp.count_ops(c)))


def sample_points(k=5, seed=0):
    rng = random.Random(seed)
    return [(mpmath.mpf(rng.uniform(2.0, 3.0)), mpmath.mpf(rng.uniform(0.3, 1.2))) for _ in range(k)]


def num_partial(f, order, pt):
    g = sp.lambdify((x, y), f, "mpmath")
    return mpmath.diff(lambda a, b: g(a, b), pt, order)


def check_against_numeric(f, derivs, pts=None):
    """derivs: {(i,j): expr}。数値微分と一致するか確かめる。"""
    pts = pts or sample_points()
    for order, d in derivs.items():
        gd = sp.lambdify((x, y), d, "mpmath")
        for pt in pts:
            a = num_partial(f, order, pt)
            b = gd(*pt)
            if abs(a - b) > 1e-15 * max(1, abs(a)):
                raise AssertionError(f"数値微分と合わない {order} at {pt}: {a} vs {b}")


def explain(f, v):
    """f を変数 v で偏微分する途中式(1段だけ)の TeX。"""
    other = y if v == x else x
    if f.is_Function and len(f.args) == 1 and not f.args[0].is_Symbol:
        U = sp.Dummy("U")
        g1 = sp.diff(f.func(U), U).subs(U, f.args[0])
        return r"%s\cdot %s" % (ptex(g1), ptex(sp.diff(f.args[0], v)))
    if f.is_Pow and f.exp.is_Number and not f.base.is_Symbol:
        return r"%s\,%s\cdot %s" % (tex(f.exp), tex(f.base ** (f.exp - 1)) if f.exp - 1 != 1 else ptex(f.base),
                                     ptex(sp.diff(f.base, v)))
    num, den = sp.fraction(f)
    if den != 1 and den.has(v) and num.has(v):
        return r"\dfrac{%s\cdot %s-%s\cdot %s}{%s}" % (
            ptex(sp.diff(num, v)), ptex(den), ptex(num), ptex(sp.diff(den, v)), tex(den**2))
    if f.is_Mul:
        dep = [a for a in f.args if a.has(v)]
        const = sp.Mul(*[a for a in f.args if not a.has(v)])
        if len(dep) == 2:
            a, b = dep
            pre = "" if const == 1 else ptex(const) + r"\left("
            post = "" if const == 1 else r"\right)"
            return r"%s%s\cdot %s+%s\cdot %s%s" % (pre, ptex(sp.diff(a, v)), ptex(b), ptex(a), ptex(sp.diff(b, v)), post)
        if len(dep) == 1 and dep[0].is_Function and not dep[0].args[0].is_Symbol:
            inner = explain(dep[0], v)
            return r"%s\cdot %s" % (inner, ptex(const)) if const != 1 else inner
    return None


def deriv_step(f, v, d, name):
    e = explain(f, v)
    note = "($%s$ を定数とみる)" % ("y" if v == x else "x")
    if e:
        return r"$%s=%s=%s$%s" % (name, e, tex(d), note)
    return r"$%s=%s$%s" % (name, tex(d), note)


def point_slope(c0, terms):
    """c0 + Σ c(var - a) を係数 0, ±1 や a=0 に気をつけて TeX にする。"""
    out = "" if c0 == 0 else tex(c0)
    for c, var, a in terms:
        if c == 0:
            continue
        lin = var if a == 0 else "(%s-%s)" % (var, tex(a)) if a > 0 else "(%s+%s)" % (var, tex(-a))
        coef = "" if abs(c) == 1 else ptex(abs(c)) if not sp.sympify(c).is_number else tex(abs(c))
        sign = "-" if c < 0 else ("+" if out else "")
        out += sign + coef + lin
    return out or "0"


# ============================================================ 偏微分
def _pd(p):
    f = parse(p["f"])
    return f, nice(sp.diff(f, x)), nice(sp.diff(f, y))


def check_pd(p):
    f = parse(p["f"])
    fx, fy = sp.diff(f, x), sp.diff(f, y)
    check_against_numeric(f, {(1, 0): fx, (0, 1): fy})
    return (fx, fy)


@kind("b_pd", check_pd, tuple_same)
def pd(p):
    f, fx, fy = _pd(p)
    steps = [deriv_step(f, x, fx, "f_x"), deriv_step(f, y, fy, "f_y")]
    if p.get("extra"):
        steps.insert(0, p["extra"])
    fl = {
        "title": p["title"],
        "question": "$f(x,y)=%s$ の偏導関数 $f_x,\\ f_y$ を求めよ。途中式も書くこと。" % (p.get("ftex") or tex(f)),
        "tool": p["tool"],
        "steps": steps,
        "answer": "$f_x=%s,\\quad f_y=%s$" % (tex(fx), tex(fy)),
    }
    return fl, (fx, fy)


def check_pd_pt(p):
    f = parse(p["f"])
    pt = tuple(sp.Rational(c) for c in p["pt"])
    vals = []
    for order in [(1, 0), (0, 1)]:
        vals.append(float(num_partial(f, order, tuple(mpmath.mpf(c) for c in pt))))
    return tuple(vals)


@kind("b_pd_pt", check_pd_pt, tuple_same)
def pd_pt(p):
    f, fx, fy = _pd(p)
    a, b = (sp.Rational(c) for c in p["pt"])
    vx, vy = sp.nsimplify(fx.subs({x: a, y: b})), sp.nsimplify(fy.subs({x: a, y: b}))
    fl = {
        "title": p["title"],
        "question": "$f(x,y)=%s$ について、点 $(%s,%s)$ における $f_x,\\ f_y$ の値を求めよ。" % (tex(f), tex(a), tex(b)),
        "tool": p["tool"],
        "steps": [deriv_step(f, x, fx, "f_x"), deriv_step(f, y, fy, "f_y"),
                  "$(x,y)=(%s,%s)$ を代入する" % (tex(a), tex(b))],
        "answer": "$f_x(%s,%s)=%s,\\quad f_y(%s,%s)=%s$" % (tex(a), tex(b), tex(vx), tex(a), tex(b), tex(vy)),
    }
    return fl, (vx, vy)


# ============================================================ 連鎖律
def check_chain_t(p):
    zf = parse(p["z"]).subs({x: parse(p["x"]), y: parse(p["y"])})
    d = sp.diff(zf, t)  # 代入してから直接微分(別ルート)
    t0 = parse(p["t0"])
    return (d, sp.nsimplify(sp.simplify(d.subs(t, t0))))


@kind("b_chain_t", check_chain_t, tuple_same)
def chain_t(p):
    f, xt, yt, t0 = parse(p["z"]), parse(p["x"]), parse(p["y"]), parse(p["t0"])
    fx, fy = sp.diff(f, x), sp.diff(f, y)
    dx, dy = sp.diff(xt, t), sp.diff(yt, t)
    total = nice((fx * dx + fy * dy).subs({x: xt, y: yt}))
    val = sp.nsimplify(sp.simplify(total.subs(t, t0)))
    fl = {
        "title": p["title"],
        "question": "$z=%s$, $x=%s$, $y=%s$ のとき $\\dfrac{dz}{dt}$ を $t$ の式で求め、$t=%s$ での値も答えよ。" % (
            tex(f), tex(xt), tex(yt), tex(t0)),
        "tool": "合成関数の微分(連鎖律) $\\dfrac{dz}{dt}=z_x\\dfrac{dx}{dt}+z_y\\dfrac{dy}{dt}$ を使う。最後に $x,y$ を $t$ で書き直す。",
        "steps": [
            r"$z_x=%s,\ z_y=%s$" % (tex(fx), tex(fy)),
            r"$\dfrac{dx}{dt}=%s,\ \dfrac{dy}{dt}=%s$" % (tex(dx), tex(dy)),
            r"$\dfrac{dz}{dt}=%s\cdot %s+%s\cdot %s$" % (ptex(fx), ptex(dx), ptex(fy), ptex(dy)),
            r"$x=%s,\ y=%s$ を代入して整理すると $\dfrac{dz}{dt}=%s$" % (tex(xt), tex(yt), tex(total)),
        ],
        "answer": r"$\dfrac{dz}{dt}=%s$、$t=%s$ で $%s$" % (tex(total), tex(t0), tex(val)),
    }
    return fl, (total, val)


def check_chain_uv(p):
    F = parse(p["F"])
    sub = {u_: parse(p["u"]), v_: parse(p["v"])}
    zxy = F.subs(sub)
    return (sp.diff(zxy, x), sp.diff(zxy, y))


@kind("b_chain_uv", check_chain_uv, tuple_same)
def chain_uv(p):
    F, U, V = parse(p["F"]), parse(p["u"]), parse(p["v"])
    Fu, Fv = sp.diff(F, u_), sp.diff(F, v_)
    sub = {u_: U, v_: V}
    zx = nice((Fu * sp.diff(U, x) + Fv * sp.diff(V, x)).subs(sub))
    zy = nice((Fu * sp.diff(U, y) + Fv * sp.diff(V, y)).subs(sub))
    fl = {
        "title": p["title"],
        "question": "$z=%s$, $u=%s$, $v=%s$ のとき、$\\dfrac{\\partial z}{\\partial x}$ と $\\dfrac{\\partial z}{\\partial y}$ を $x,y$ の式で求めよ。" % (
            tex(F), tex(U), tex(V)),
        "tool": "$z$ は $u,v$ を通して $x,y$ に依存するので連鎖律 $z_x=z_u u_x+z_v v_x$, $z_y=z_u u_y+z_v v_y$ を使う。",
        "steps": [
            r"$z_u=%s,\ z_v=%s$" % (tex(Fu), tex(Fv)),
            r"$u_x=%s,\ u_y=%s,\ v_x=%s,\ v_y=%s$" % (tex(sp.diff(U, x)), tex(sp.diff(U, y)), tex(sp.diff(V, x)), tex(sp.diff(V, y))),
            r"$z_x=%s\cdot %s+%s\cdot %s$ に $u=%s,\ v=%s$ を代入して $z_x=%s$" % (ptex(Fu), ptex(sp.diff(U, x)), ptex(Fv), ptex(sp.diff(V, x)), tex(U), tex(V), tex(zx)),
            r"同様に $z_y=%s\cdot %s+%s\cdot %s=%s$" % (ptex(Fu), ptex(sp.diff(U, y)), ptex(Fv), ptex(sp.diff(V, y)), tex(zy)),
        ],
        "answer": r"$\dfrac{\partial z}{\partial x}=%s,\quad \dfrac{\partial z}{\partial y}=%s$" % (tex(zx), tex(zy)),
    }
    return fl, (zx, zy)


def check_chain_polar(p):
    f = parse(p["f"])
    g = f.subs({x: r_ * sp.cos(th), y: r_ * sp.sin(th)})
    return (sp.diff(g, r_), sp.diff(g, th))


@kind("b_chain_polar", check_chain_polar, tuple_same)
def chain_polar(p):
    f = parse(p["f"])
    fx, fy = sp.diff(f, x), sp.diff(f, y)
    sub = {x: r_ * sp.cos(th), y: r_ * sp.sin(th)}
    zr = sp.simplify(sp.trigsimp((fx * sp.cos(th) + fy * sp.sin(th)).subs(sub)))
    zt = sp.simplify(sp.trigsimp((fx * (-r_ * sp.sin(th)) + fy * r_ * sp.cos(th)).subs(sub)))
    fl = {
        "title": "極座標への連鎖律",
        "question": "$z=%s$, $x=r\\cos\\theta$, $y=r\\sin\\theta$ のとき $\\dfrac{\\partial z}{\\partial r}$ と $\\dfrac{\\partial z}{\\partial \\theta}$ を $r,\\theta$ の式で求めよ。" % tex(f),
        "tool": "連鎖律 $z_r=z_x x_r+z_y y_r$, $z_\\theta=z_x x_\\theta+z_y y_\\theta$ を使い、最後に倍角の公式で整理する。",
        "steps": [
            r"$z_x=%s,\ z_y=%s$" % (tex(fx), tex(fy)),
            r"$x_r=\cos\theta,\ y_r=\sin\theta,\ x_\theta=-r\sin\theta,\ y_\theta=r\cos\theta$",
            r"$z_r=%s\cos\theta+%s\sin\theta=%s$" % (ptex(fx.subs(sub)), ptex(fy.subs(sub)), tex(zr)),
            r"$z_\theta=%s\cdot(-r\sin\theta)+%s\cdot r\cos\theta=%s$" % (ptex(fx.subs(sub)), ptex(fy.subs(sub)), tex(zt)),
        ],
        "answer": r"$\dfrac{\partial z}{\partial r}=%s,\quad \dfrac{\partial z}{\partial \theta}=%s$" % (tex(zr), tex(zt)),
    }
    return fl, (zr, zt)


# ============================================================ 接平面
def check_tp(p):
    f = parse(p["f"])
    a, b = (sp.Rational(c) for c in p["pt"])
    pt = (mpmath.mpf(a), mpmath.mpf(b))
    g = sp.lambdify((x, y), f, "mpmath")
    f0 = g(*pt)
    fx0, fy0 = num_partial(f, (1, 0), pt), num_partial(f, (0, 1), pt)
    # 接平面との差が 2 次の微小量であること
    for h in [mpmath.mpf("1e-6"), mpmath.mpf("1e-8")]:
        err = abs(g(pt[0] + h, pt[1] - 2 * h) - (f0 + fx0 * h - 2 * fy0 * h))
        if err > 1e3 * h * h:
            raise AssertionError("接平面の誤差が1次")
    return (float(f0), float(fx0), float(fy0))


@kind("b_tp", check_tp, tuple_same)
def tp(p):
    f = parse(p["f"])
    a, b = (sp.Rational(c) for c in p["pt"])
    f0 = sp.simplify(f.subs({x: a, y: b}))
    fx, fy = sp.diff(f, x), sp.diff(f, y)
    fx0, fy0 = sp.simplify(fx.subs({x: a, y: b})), sp.simplify(fy.subs({x: a, y: b}))
    plane = sp.expand(f0 + fx0 * (x - a) + fy0 * (y - b))
    fl = {
        "title": p["title"],
        "question": "曲面 $z=%s$ 上の点 $(%s,%s,%s)$ における接平面の方程式を求めよ。" % (tex(f), tex(a), tex(b), tex(f0)),
        "tool": "接平面は $z=f(a,b)+f_x(a,b)(x-a)+f_y(a,b)(y-b)$。まず偏導関数を求めて点の値を代入する。",
        "steps": [
            r"$f_x=%s,\ f_y=%s$" % (tex(fx), tex(fy)),
            r"$f(%s,%s)=%s,\ f_x(%s,%s)=%s,\ f_y(%s,%s)=%s$" % (tex(a), tex(b), tex(f0), tex(a), tex(b), tex(fx0), tex(a), tex(b), tex(fy0)),
            "$z=%s$" % point_slope(f0, [(fx0, "x", a), (fy0, "y", b)]),
        ],
        "answer": "$z=%s$" % tex(plane),
    }
    return fl, (f0, fx0, fy0)


def _int_plane(nv, P):
    nv = [sp.nsimplify(c) for c in nv]
    den = sp.ilcm(*[sp.fraction(c)[1] for c in nv])
    nv = [c * den for c in nv]
    g = sp.igcd(*[int(c) for c in nv])
    nv = [c / g for c in nv]
    d = sum(c * q for c, q in zip(nv, P))
    return nv, d


def check_tp_imp(p):
    F = parse(p["F"])
    P = [mpmath.mpf(sp.Rational(c)) for c in p["pt"]]
    g = sp.lambdify((x, y, z), F, "mpmath")
    if abs(g(*P) - sp.Rational(p["c"])) > 1e-30:
        raise AssertionError("点が曲面上にない")
    grad = [mpmath.diff(g, P, o) for o in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]]
    k = max(grad, key=abs)
    return tuple(float(c / k) for c in grad)


def tp_imp_same(a, b):
    k = max(a, key=abs)
    return tuple_same(tuple(float(c / k) for c in a), b)


@kind("b_tp_imp", check_tp_imp, tp_imp_same)
def tp_imp(p):
    F = parse(p["F"])
    c = sp.Rational(p["c"])
    P = [sp.Rational(q) for q in p["pt"]]
    sub = dict(zip((x, y, z), P))
    if sp.simplify(F.subs(sub) - c) != 0:
        raise AssertionError("not on surface")
    grads = [sp.diff(F, v) for v in (x, y, z)]
    gv = [g.subs(sub) for g in grads]
    nv, d = _int_plane(gv, P)
    lhs = sp.expand(nv[0] * x + nv[1] * y + nv[2] * z)
    fl = {
        "title": p["title"],
        "question": "曲面 $%s=%s$ 上の点 $(%s,%s,%s)$ における接平面の方程式を求めよ。" % (tex(F), tex(c), *map(tex, P)),
        "tool": "陰関数の形 $F(x,y,z)=c$ の曲面では、勾配 $(F_x,F_y,F_z)$ が法線ベクトルになる。法線ベクトルと点から平面の式を作る。",
        "steps": [
            r"$F=%s$ とおくと $F_x=%s,\ F_y=%s,\ F_z=%s$" % (tex(F), *map(tex, grads)),
            r"点 $(%s,%s,%s)$ での法線ベクトル $(%s,%s,%s)$" % (*map(tex, P), *map(tex, gv)),
            "$%s=0$" % point_slope(0, [(gv[0], "x", P[0]), (gv[1], "y", P[1]), (gv[2], "z", P[2])]),
        ],
        "answer": "$%s=%s$" % (tex(lhs), tex(d)),
    }
    return fl, tuple(gv)


def check_tp_par(p):
    f = parse(p["f"])
    pn, qn = sp.Rational(p["pq"][0]), sp.Rational(p["pq"][1])
    # 別ルート: 勾配の方程式を連立して解く
    sol = sp.solve([sp.diff(f, x) - pn, sp.diff(f, y) - qn], [x, y], dict=True)
    if len(sol) != 1:
        raise AssertionError(sol)
    a, b = sol[0][x], sol[0][y]
    pt = (mpmath.mpf(a), mpmath.mpf(b))
    if abs(num_partial(f, (1, 0), pt) - pn) > 1e-20 or abs(num_partial(f, (0, 1), pt) - qn) > 1e-20:
        raise AssertionError("数値微分で傾きが合わない")
    return (a, b, f.subs({x: a, y: b}))


@kind("b_tp_par", check_tp_par, tuple_same)
def tp_par(p):
    f = parse(p["f"])
    pn, qn = sp.Rational(p["pq"][0]), sp.Rational(p["pq"][1])
    fx, fy = sp.diff(f, x), sp.diff(f, y)
    # f = x^2 + k y^2 型: 1次方程式を解く
    a = sp.solve(sp.Eq(fx, pn), x)[0]
    b = sp.solve(sp.Eq(fy, qn), y)[0]
    c = f.subs({x: a, y: b})
    plane = sp.expand(c + pn * (x - a) + qn * (y - b))
    fl = {
        "title": "平面に平行な接平面",
        "question": "曲面 $z=%s$ の接平面のうち、平面 $%s$ に平行なものの接点と方程式を求めよ。" % (
            tex(f), tex(sp.Eq(z, pn * x + qn * y)).replace("=", "=", 1)),
        "tool": "$z=px+qy+c$ の形の平面どうしが平行 ⇔ 傾き $(p,q)$ が等しい。接平面の傾きは $(f_x,f_y)$ なので $f_x=p,\\ f_y=q$ を解いて接点を求める(接平面の式と連立方程式の組み合わせ)。",
        "steps": [
            r"$f_x=%s,\ f_y=%s$" % (tex(fx), tex(fy)),
            r"平行条件 $f_x=%s,\ f_y=%s$ より $x=%s,\ y=%s$" % (tex(pn), tex(qn), tex(a), tex(b)),
            r"$z=f(%s,%s)=%s$ なので接点は $(%s,%s,%s)$" % (tex(a), tex(b), tex(c), tex(a), tex(b), tex(c)),
            "$z=%s$" % point_slope(c, [(pn, "x", a), (qn, "y", b)]),
        ],
        "answer": "接点 $(%s,%s,%s)$、接平面 $z=%s$" % (tex(a), tex(b), tex(c), tex(plane)),
    }
    return fl, (a, b, c)


# ============================================================ 極限(存在する)
def check_lim_exist(p):
    f = parse(p["f"])
    L = parse(p["L"])
    B = parse(p["bound"])  # |f-L| <= B(r) を数値で確かめる
    if sp.limit(B, r_, 0, "+") != 0:
        raise AssertionError("bound does not vanish")
    g = sp.lambdify((x, y), f - L, "mpmath")
    gb = sp.lambdify(r_, B, "mpmath")
    rng = random.Random(1)
    for _ in range(400):
        rr = mpmath.mpf(10) ** (-rng.uniform(1, 8))
        a = mpmath.mpf(rng.uniform(0, 2 * 3.141592653589793))
        X, Y = rr * mpmath.cos(a), rr * mpmath.sin(a)
        if abs(g(X, Y)) > gb(rr) * (1 + mpmath.mpf("1e-20")) + mpmath.mpf("1e-30"):
            raise AssertionError(f"上からの評価が成り立たない at r={rr}")
    for path in [y - 2 * x, y - x**2, x]:  # いくつかの経路でも確認
        sol = sp.solve(path, y if path.has(y) else x)
        if not sol:
            continue
        var = x if path.has(y) else y
        sub = {y: sol[0]} if path.has(y) else {x: sol[0]}
        if sp.limit(f.subs(sub), var, 0) != L:
            raise AssertionError("path limit mismatch")
    return L


@kind("b_lim_exist", check_lim_exist, tuple_same)
def lim_exist(p):
    f, L = parse(p["f"]), parse(p["L"])
    steps = list(p["steps"])
    if p.get("polar"):
        pol = parse(p["polar"])
        diff = sp.simplify(f.subs({x: r_ * sp.cos(th), y: r_ * sp.sin(th)}) - pol)
        if diff != 0:
            raise AssertionError("polar form mismatch")
        steps.insert(0, r"$x=r\cos\theta,\ y=r\sin\theta$ とおくと $f=%s$" % tex(pol))
    fl = {
        "title": p["title"],
        "question": "極限 $\\displaystyle\\lim_{(x,y)\\to(0,0)}%s$ を求めよ。存在することの理由も書くこと。" % tex(f),
        "tool": p["tool"],
        "steps": steps,
        "answer": m(L),
    }
    return fl, L


# ============================================================ 極限(存在しない)
def _path_limit(f, path):
    var, expr = path
    sub = {y: expr} if var == x else {x: expr}
    return sp.simplify(sp.limit(sp.simplify(f.subs(sub)), var, 0))


def check_lim_none(p):
    """経路上の点 (h, g(h)) で h=1e-12 として数値的に値を求め、2経路で違うことを確かめる。"""
    f = parse(p["f"])
    g = sp.lambdify((x, y), f, "mpmath")
    h = mpmath.mpf("1e-12")
    vals = []
    for var, expr, mv in p["check_paths"]:
        v = x if var == "x" else y
        e = sp.lambdify(v, parse(expr).subs(mm, sp.Rational(mv)), "mpmath")
        X, Y = (h, e(h)) if v == x else (e(h), h)
        vals.append(float(g(X, Y)))
    if abs(vals[0] - vals[1]) < 1e-3:
        raise AssertionError("経路による値が同じ")
    return tuple(vals)


@kind("b_lim_none", check_lim_none, tuple_same)
def lim_none(p):
    f = parse(p["f"])
    steps = []
    vals = []
    for var, expr in p["paths"]:
        v = x if var == "x" else y
        e = parse(expr)
        lim = _path_limit(f, (v, e))
        restricted = sp.simplify(f.subs({y: e} if v == x else {x: e}))
        if restricted.has(v):
            steps.append(r"$%s=%s$ に沿って近づけると $f=%s\to %s$" % ("y" if v == x else "x", tex(e), tex(restricted), tex(lim)))
        else:
            steps.append(r"$%s=%s$ に沿って近づけると $f=%s$(一定)" % ("y" if v == x else "x", tex(e), tex(restricted)))
    cv = []
    for var, expr, mv in p["check_paths"]:
        v = x if var == "x" else y
        cv.append(_path_limit(f, (v, parse(expr).subs(mm, sp.Rational(mv)))))
    concl = p["conclude"]
    for i, c in enumerate(cv):
        concl = concl.replace("@%d" % i, tex(c))
    steps.append(concl)
    fl = {
        "title": p["title"],
        "question": "極限 $\\displaystyle\\lim_{(x,y)\\to(0,0)}%s$ は存在しないことを示せ。" % tex(f),
        "tool": p["tool"],
        "steps": steps,
        "answer": p["answer"],
    }
    return fl, tuple(cv)


# ============================================================ 高階偏導関数
def check_high(p):
    f = parse(p["f"])
    fxx, fyx, fyy = sp.diff(f, x, 2), sp.diff(sp.diff(f, y), x), sp.diff(f, y, 2)
    check_against_numeric(f, {(2, 0): fxx, (1, 1): fyx, (0, 2): fyy})
    return (fxx, fyx, fyy)


@kind("b_high", check_high, tuple_same)
def high(p):
    f = parse(p["f"])
    fx, fy = nice(sp.diff(f, x)), nice(sp.diff(f, y))
    fxx, fxy, fyy = nice(sp.diff(fx, x)), nice(sp.diff(fx, y)), nice(sp.diff(fy, y))
    fyx = nice(sp.diff(fy, x))
    steps = [r"$f_x=%s,\ f_y=%s$" % (tex(fx), tex(fy)),
             r"$f_{xx}=(f_x)_x=%s$" % tex(fxx),
             r"$f_{xy}=(f_x)_y=%s$、$f_{yx}=(f_y)_x=%s$(一致する)" % (tex(fxy), tex(fyx)),
             r"$f_{yy}=(f_y)_y=%s$" % tex(fyy)]
    q = "$f(x,y)=%s$ の2階偏導関数 $f_{xx},\\ f_{xy},\\ f_{yy}$ を求めよ。" % tex(f)
    ans = "$f_{xx}=%s,\\quad f_{xy}=%s,\\quad f_{yy}=%s$" % (tex(fxx), tex(fxy), tex(fyy))
    val = (fxx, fxy, fyy)
    if p.get("laplace"):
        lap = sp.simplify(fxx + fyy)
        steps.append(r"$f_{xx}+f_{yy}=%s$" % tex(lap))
        q = "$f(x,y)=%s$ について $f_{xx}+f_{yy}$ を計算せよ。$f_{xx},\\ f_{yy}$ も答えること。" % tex(f)
        ans = "$f_{xx}=%s,\\quad f_{yy}=%s,\\quad f_{xx}+f_{yy}=%s$" % (tex(fxx), tex(fyy), tex(lap))
        steps = [steps[0], steps[1], steps[3], steps[4]]
    fl = {"title": p["title"], "question": q, "tool": p["tool"], "steps": steps, "answer": ans}
    return fl, val


# ============================================================ 全微分
def check_td(p):
    f = parse(p["f"])
    fx, fy = sp.diff(f, x), sp.diff(f, y)
    check_against_numeric(f, {(1, 0): fx, (0, 1): fy})
    return (fx, fy)


@kind("b_td", check_td, tuple_same)
def td(p):
    f, fx, fy = _pd(p)
    fl = {
        "title": p["title"],
        "question": "$z=%s$ の全微分 $dz$ を求めよ。" % tex(f),
        "tool": "全微分は $dz=z_x\\,dx+z_y\\,dy$。偏導関数を2つ求めて並べればよい。",
        "steps": [deriv_step(f, x, fx, "z_x"), deriv_step(f, y, fy, "z_y")],
        "answer": r"$dz=%s\,dx%s\,dy$" % (ptex(fx), ("-" + ptex(-fy)) if fy.could_extract_minus_sign() else "+" + ptex(fy)),
    }
    return fl, (fx, fy)


def check_td_approx(p):
    f = parse(p["f"])
    a, b = (sp.Rational(c) for c in p["pt"])
    da, db = (sp.Rational(c) for c in p["d"])
    pt = (mpmath.mpf(a), mpmath.mpf(b))
    g = sp.lambdify((x, y), f, "mpmath")
    approx = g(*pt) + num_partial(f, (1, 0), pt) * da + num_partial(f, (0, 1), pt) * db
    true = g(pt[0] + da, pt[1] + db)
    if abs(true - approx) > 1e-3:
        raise AssertionError("1次近似が粗すぎる")
    return float(approx)


@kind("b_td_approx", check_td_approx, lambda a, b: abs(float(a) - b) < 1e-12)
def td_approx(p):
    f = parse(p["f"])
    a, b = (sp.Rational(c) for c in p["pt"])
    da, db = (sp.Rational(c) for c in p["d"])
    fx, fy = sp.diff(f, x), sp.diff(f, y)
    f0, fx0, fy0 = (sp.nsimplify(e.subs({x: a, y: b})) for e in (f, fx, fy))
    df = fx0 * da + fy0 * db
    approx = f0 + df
    X, Y = a + da, b + db
    fl = {
        "title": "全微分による近似値",
        "question": "全微分を用いて $%s$ の近似値を求めよ(小数で答えよ)。" % p["qtex"],
        "tool": "$f(x,y)=%s$ とし、計算しやすい点 $(%s,%s)$ のまわりで $f(a+\\Delta x,b+\\Delta y)\\approx f(a,b)+f_x\\Delta x+f_y\\Delta y$ を使う。" % (tex(f), tex(a), tex(b)),
        "steps": [
            r"$f_x=%s,\ f_y=%s$" % (tex(fx), tex(fy)),
            r"$f(%s,%s)=%s,\ f_x(%s,%s)=%s,\ f_y(%s,%s)=%s$" % (tex(a), tex(b), tex(f0), tex(a), tex(b), tex(fx0), tex(a), tex(b), tex(fy0)),
            r"$\Delta x=%s,\ \Delta y=%s$ より $df=%s\cdot %s+%s\cdot %s=%s$" % (
                _dec(da), _dec(db), ptex(fx0), _pdec(da), ptex(fy0), _pdec(db), _dec(df)),
            r"$f(%s,%s)\approx %s%s=%s$" % (_dec(X), _dec(Y), tex(f0), ("+" if df >= 0 else "") + _dec(df), _dec(approx)),
        ],
        "answer": "$%s$" % _dec(approx),
    }
    return fl, approx


def _pdec(q):
    return "(%s)" % _dec(q) if q < 0 else _dec(q)


def _dec(q):
    """有限小数になる有理数を小数表記にする。"""
    q = sp.Rational(q)
    for k in range(0, 10):
        if (q * 10**k).is_integer:
            s = f"{float(q):.{k}f}"
            if sp.Rational(s) != q:
                raise AssertionError("decimal mismatch")
            return s
    raise AssertionError("not a finite decimal")


def check_td_err(p):
    r0, h0, dr, dh = (sp.Rational(c) for c in (p["r"], p["h"], p["dr"], p["dh"]))
    # 別ルート: 4通りの符号の組で V の変化の1次部分を数値微分から求め、最大値をとる
    V = lambda rr, hh: mpmath.pi * rr * rr * hh
    Vr = mpmath.diff(lambda rr: V(rr, mpmath.mpf(h0)), mpmath.mpf(r0))
    Vh = mpmath.diff(lambda hh: V(mpmath.mpf(r0), hh), mpmath.mpf(h0))
    mx = max(abs(Vr * s1 * dr + Vh * s2 * dh) for s1 in (1, -1) for s2 in (1, -1))
    return (float(mx / mpmath.pi), float(mx / V(mpmath.mpf(r0), mpmath.mpf(h0))))


@kind("b_td_err", check_td_err, tuple_same)
def td_err(p):
    r0, h0, dr, dh = (sp.Rational(c) for c in (p["r"], p["h"], p["dr"], p["dh"]))
    rr, hh = sp.symbols("r h", positive=True)
    V = sp.pi * rr**2 * hh
    Vr, Vh = sp.diff(V, rr), sp.diff(V, hh)
    sub = {rr: r0, hh: h0}
    dV = Vr.subs(sub) * dr + Vh.subs(sub) * dh
    V0 = V.subs(sub)
    rel = sp.nsimplify(dV / V0)
    fl = {
        "title": "全微分による誤差の評価",
        "question": "円柱の半径を $r=%s\\ \\mathrm{cm}$、高さを $h=%s\\ \\mathrm{cm}$ と測った。測定誤差がそれぞれ最大 $%s\\ \\mathrm{cm}$, $%s\\ \\mathrm{cm}$ のとき、体積 $V=\\pi r^2 h$ の誤差の最大値(1次近似)と相対誤差を求めよ。" % (
            _dec(r0), _dec(h0), _dec(dr), _dec(dh)),
        "tool": "全微分 $dV=V_r\\,dr+V_h\\,dh$ で誤差を1次近似し、各項の絶対値を足して最大値を出す。相対誤差は $\\dfrac{|dV|}{V}\\le 2\\dfrac{|dr|}{r}+\\dfrac{|dh|}{h}$ でも求まる。",
        "steps": [
            r"$V_r=2\pi rh,\ V_h=\pi r^2$",
            r"$|dV|\le 2\pi\cdot %s\cdot %s\cdot %s+\pi\cdot %s^2\cdot %s=%s$" % (_dec(r0), _dec(h0), _dec(dr), _dec(r0), _dec(dh), tex(dV)),
            r"$V=\pi\cdot %s^2\cdot %s=%s$ より $\dfrac{|dV|}{V}\le %s=%s$" % (_dec(r0), _dec(h0), tex(V0), tex(rel), _dec(rel)),
        ],
        "answer": r"誤差の最大値 $%s\ \mathrm{cm^3}$($\approx %s\ \mathrm{cm^3}$)、相対誤差 $%s$($%s\,\%%$)" % (
            tex(dV), f"{float(dV):.1f}", _dec(rel), _dec(rel * 100)),
    }
    return fl, (dV / sp.pi, rel)


# ============================================================ 出題リスト
def specs(rng):
    L = []
    add = lambda kind_, lv, **p: L.append((kind_, lv, p))

    # --- 偏微分 (8)
    a, b = rng.choice([(3, 2), (4, 3), (2, 5), (5, 2), (3, 4)])
    c = rng.choice([3, 4, 5])
    add("b_pd", 1, f="x**%d*y**%d+%d*x*y" % (a, b, c), title="多項式の偏微分",
        tool="$f_x$ は $y$ を定数とみて $x$ で微分、$f_y$ は $x$ を定数とみて $y$ で微分する。")
    a, b = rng.choice([(2, 3), (3, 2), (2, 5), (4, 3), (5, 2)])
    add("b_pd", 1, f="exp(%d*x)*sin(%d*y)" % (a, b), title="指数×三角の偏微分",
        tool="$x$ で微分するとき $\\sin %dy$ は定数、$y$ で微分するとき $e^{%dx}$ は定数。それぞれ合成関数の微分で中身の係数が前に出る。" % (b, a))
    a = rng.choice([2, 3, 4])
    add("b_pd", 1, f="log(x**2+%d*y**2)" % a, title="対数関数の偏微分",
        tool="$\\log u$ の微分は $\\dfrac{u'}{u}$。中身 $u=x^2+%dy^2$ を $x$, $y$ でそれぞれ偏微分する。" % a)
    a = rng.choice([2, 3, 4])
    add("b_pd", 2, f="exp(x*y**%d)" % a, title="指数の肩に積がある偏微分",
        tool="$e^{u}$ の偏微分は $e^{u}\\cdot u_x$, $e^{u}\\cdot u_y$。肩の $u=xy^%d$ を偏微分したものがかかる。" % a)
    add("b_pd", 2, f="atan(y/x)", title="逆正接の偏微分",
        tool="$(\\arctan u)'=\\dfrac{1}{1+u^2}$ と合成関数の微分を使う。$u=\\dfrac{y}{x}$ を $x$ で微分すると $-\\dfrac{y}{x^2}$ になる。")
    add("b_pd", 2, f="x**y", title="xʸ の偏微分",
        tool="$x$ で微分するときは $y$ が定数なので $x^n$ の微分、$y$ で微分するときは $x$ が定数なので $a^y$ の微分($a^y\\log a$)になる。",
        ftex="x^y\\ (x>0)")
    a = rng.choice([1, 2])
    add("b_pd", 2, f="(x+%d*y)/(x-y)" % a, title="商の偏微分",
        tool="商の微分公式 $\\left(\\dfrac{u}{v}\\right)'=\\dfrac{u'v-uv'}{v^2}$ を $x$, $y$ それぞれについて使う。")
    a, (x0, y0) = rng.choice([(3, ("1", "1")), (8, ("1", "1")), (5, ("2", "1")), (15, ("1", "1")), (24, ("1", "1"))])
    add("b_pd_pt", 1, f="sqrt(%d*x**2+y**2)" % a, pt=[x0, y0], title="点での偏微分係数",
        tool="$\\sqrt{u}$ の微分は $\\dfrac{u'}{2\\sqrt{u}}$。偏導関数を求めてから点の座標を代入する。")

    # --- 連鎖律 (4)
    add("b_chain_t", 1, z="x**2*y", x="cos(t)", y="sin(t)", t0="pi/4", title="1変数への連鎖律")
    a = rng.choice([2, 3, 4])
    add("b_chain_t", 2, z="exp(x)*log(y)", x="%d*t" % a, y="t**2+1", t0="0", title="指数・対数の連鎖律")
    add("b_chain_uv", 2, F="u**2*v", u="x+y", v="x*y", title="2変数への連鎖律")
    add("b_chain_polar", 2, f="x**2-y**2")

    # --- 接平面 (7)
    a, (x0, y0) = rng.choice([(2, ("1", "1")), (3, ("1", "2")), (2, ("2", "1")), (4, ("1", "1")), (3, ("2", "1"))])
    add("b_tp", 1, f="x**2+%d*y**2" % a, pt=[x0, y0], title="接平面(2次式)")
    add("b_tp", 1, f="x**2*y+y**3", pt=["1", "2"], title="接平面(3次式)")
    add("b_tp", 2, f="log(x**2+y**2)", pt=["1", "1"], title="接平面(対数)")
    add("b_tp", 2, f="exp(x)*cos(y)", pt=["0", "0"], title="接平面(指数×三角)")
    P = rng.choice([("1", "2", "2"), ("2", "1", "2"), ("2", "2", "1"), ("-1", "2", "2"), ("2", "-2", "1")])
    add("b_tp_imp", 2, F="x**2+y**2+z**2", c="9", pt=list(P), title="球面の接平面")
    add("b_tp_imp", 2, F="x*y*z", c="6", pt=["1", "2", "3"], title="陰関数表示の曲面の接平面")
    k, (pn, qn) = rng.choice([(2, ("2", "8")), (3, ("4", "6")), (2, ("6", "4")), (2, ("4", "4")), (3, ("2", "12")), (4, ("2", "8"))])
    add("b_tp_par", 3, f="x**2+%d*y**2" % k, pq=[pn, qn])

    # --- 極限が存在する (5)
    a = rng.choice([2, 3, 4])
    add("b_lim_exist", 1, f="%d*x**2*y/(x**2+y**2)" % a, L="0", polar="%d*r*cos(theta)**2*sin(theta)" % a,
        bound="%d*r" % a, title="極座標で極限を求める",
        tool="分母が $x^2+y^2=r^2$ になるので極座標 $x=r\\cos\\theta,\\ y=r\\sin\\theta$ に直し、$\\theta$ によらない評価ではさみうちにする。",
        steps=[r"$|f|=%d r|\cos^2\theta\sin\theta|\le %d r$" % (a, a), r"$r\to 0$ で $%d r\to 0$ なので、はさみうちの原理より極限は $0$" % a])
    add("b_lim_exist", 1, f="(x**3+y**3)/(x**2+y**2)", L="0", polar="r*(cos(theta)**3+sin(theta)**3)",
        bound="2*r", title="極座標とはさみうち",
        tool="極座標に直すと $r$ が1つ残り、残りの $\\theta$ の部分は有界。$|\\cos\\theta|,|\\sin\\theta|\\le 1$ で評価する。",
        steps=[r"$|f|\le r(|\cos\theta|^3+|\sin\theta|^3)\le 2r$", r"$r\to 0$ で $2r\to 0$ なので、はさみうちの原理より極限は $0$"])
    add("b_lim_exist", 2, f="x**2*y**2/(x**2+y**2)", L="0", polar="r**2*cos(theta)**2*sin(theta)**2",
        bound="r**2", title="極座標で 2 次の残り",
        tool="分母が $r^2$、分子が $r^4$ の次数なので極座標で $r^2\\times(\\theta$ の有界な式$)$ になる。",
        steps=[r"$|f|=r^2\cos^2\theta\sin^2\theta\le r^2$", r"$r\to 0$ で $r^2\to 0$ なので極限は $0$"])
    a = rng.choice([2, 3, 4])
    add("b_lim_exist", 2, f="sin(%d*(x**2+y**2))/(x**2+y**2)" % a, L=str(a), bound="%d*r**4/6" % (a**3),
        title="1変数の極限に帰着",
        tool="$x,y$ が $x^2+y^2$ の形でしか現れないので $s=x^2+y^2\\to+0$ と1変数にまとめ、$\\displaystyle\\lim_{u\\to 0}\\dfrac{\\sin u}{u}=1$ を使う。",
        steps=[r"$s=x^2+y^2$ とおくと $(x,y)\to(0,0)$ のとき $s\to +0$",
               r"$f=\dfrac{\sin %ds}{s}=%d\cdot\dfrac{\sin %ds}{%ds}$" % (a, a, a, a),
               r"$\dfrac{\sin %ds}{%ds}\to 1$ より $f\to %d$" % (a, a, a)])
    add("b_lim_exist", 3, f="x**3*y/(x**4+y**2)", L="0", bound="r/2", title="相加相乗平均で評価する極限",
        tool="極座標では分母が $r^4\\cos^4\\theta+r^2\\sin^2\\theta$ となり $\\theta$ の評価が難しい。$x^4+y^2\\ge 2x^2|y|$(相加相乗平均)で分子と比べる。",
        steps=[r"$x^4+y^2\ge 2\sqrt{x^4y^2}=2x^2|y|$",
               r"$|f|=\dfrac{|x|\cdot x^2|y|}{x^4+y^2}\le\dfrac{|x|\cdot x^2|y|}{2x^2|y|}=\dfrac{|x|}{2}$($xy\neq 0$。$xy=0$ なら $f=0$)",
               r"$|x|\to 0$ なので、はさみうちの原理より極限は $0$"])

    # --- 極限が存在しない (5)
    add("b_lim_none", 1, f="x*y/(x**2+y**2)", paths=[["x", "m*x"]], check_paths=[["x", "m*x", "0"], ["x", "m*x", "1"]],
        title="直線に沿った極限が傾きで変わる",
        tool="直線 $y=mx$ に沿って近づけて、極限が $m$ によって変わることを示す(経路依存性)。",
        conclude=r"$m=0$ なら $@0$, $m=1$ なら $@1$ と近づき方で値が異なる",
        answer="存在しない($y=mx$ に沿うと $\\dfrac{m}{1+m^2}$ に近づき、$m$ によって値が変わる)")
    a = rng.choice([2, 3, 4])
    add("b_lim_none", 1, f="(x**2-%d*y**2)/(x**2+y**2)" % a, paths=[["x", "m*x"]],
        check_paths=[["x", "m*x", "0"], ["x", "m*x", "1"]], title="直線に沿った極限(2次の比)",
        tool="分子と分母がどちらも2次なので、直線 $y=mx$ に沿うと $x^2$ が約分されて $m$ だけの式が残る。",
        conclude=r"$m=0$ なら $@0$, $m=1$ なら $@1$ と近づき方で値が異なる",
        answer="存在しない($y=mx$ に沿うと $\\dfrac{1-%dm^2}{1+m^2}$ に近づき、$m$ によって値が変わる)" % a)
    add("b_lim_none", 2, f="x**2*y**2/(x**2*y**2+(x-y)**2)", paths=[["x", "x"], ["x", "0"]],
        check_paths=[["x", "x", "0"], ["x", "0*x", "0"]], title="2つの経路で値が違う",
        tool="分母の $(x-y)^2$ が $y=x$ 上で消えることに注目し、$y=x$ と $y=0$ の2つの経路を比べる。",
        conclude="経路によって極限が $@0$ と $@1$ で異なる", answer="存在しない($y=x$ に沿うと $1$、$y=0$ に沿うと $0$)")
    add("b_lim_none", 3, f="x**2*y/(x**4+y**2)", paths=[["x", "m*x"], ["x", "m*x**2"]],
        check_paths=[["x", "m*x", "1"], ["x", "m*x**2", "1"]], title="直線では同じでも放物線で違う",
        tool="直線 $y=mx$ ではどれも $0$ になってしまう。分母の $x^4$ と $y^2$ の次数をそろえるため放物線 $y=mx^2$ に沿って調べる。",
        conclude=r"直線に沿うとすべて $@0$ だが、放物線 $y=x^2$ に沿うと $@1$ で一致しない",
        answer="存在しない(直線 $y=mx$ ではすべて $0$、放物線 $y=mx^2$ に沿うと $\\dfrac{m}{1+m^2}$)")
    add("b_lim_none", 3, f="x*y**2/(x**2+y**4)", paths=[["y", "m*y"], ["y", "m*y**2"]],
        check_paths=[["y", "m*y", "1"], ["y", "m*y**2", "1"]], title="x=my² に沿った極限",
        tool="分母の $x^2$ と $y^4$ の次数をそろえるため、$x=my^2$ という曲線に沿って近づける。直線だけでは $0$ にしかならない。",
        conclude=r"直線 $x=my$ ではすべて $@0$ だが、$x=y^2$ に沿うと $@1$ で一致しない",
        answer="存在しない(直線 $x=my$ ではすべて $0$、曲線 $x=my^2$ に沿うと $\\dfrac{m}{1+m^2}$)")

    # --- 高階偏導関数 (4)
    a, b = rng.choice([(3, 2), (4, 2), (3, 3), (4, 3), (5, 2)])
    add("b_high", 1, f="x**%d*y**%d" % (a, b), title="2階偏導関数(多項式)",
        tool="まず $f_x, f_y$ を求め、それをもう一度偏微分する。$f_{xy}$ は $f_x$ を $y$ で微分したもの。")
    a, b = rng.choice([(2, 3), (3, 2), (2, 5), (4, 1)])
    add("b_high", 2, f="exp(%d*x)*cos(%d*y)" % (a, b), title="2階偏導関数(指数×三角)",
        tool="指数と三角は微分しても形が変わらない。係数がどう出てくるかに注意して2回偏微分する。")
    add("b_high", 2, f="log(x**2+y**2)", laplace=True, title="ラプラシアンの計算",
        tool="$f_x$ は商の形になるので、2階は商の微分公式を使う。$f_{xx}$ と $f_{yy}$ を足すと打ち消し合う。")
    add("b_high", 3, f="x**y", title="xʸ の2階偏導関数",
        tool="$x$ で微分すると $x^n$ 型、$y$ で微分すると $a^y$ 型になる。$f_{xy}$ では積の微分も必要になる(2つの微分公式の組み合わせ)。")

    # --- 全微分 (4)
    a, b = rng.choice([(2, 3), (3, 2), (2, 4), (4, 1)])
    add("b_td", 1, f="x**%d*y**%d" % (a, b), title="全微分(多項式)")
    add("b_td", 1, f="x/y", title="全微分(商)")
    qx, qy = rng.choice([(("301/100", "398/100"), "\\sqrt{3.01^2+3.98^2}"), (("298/100", "403/100"), "\\sqrt{2.98^2+4.03^2}"), (("302/100", "396/100"), "\\sqrt{3.02^2+3.96^2}"), (("297/100", "401/100"), "\\sqrt{2.97^2+4.01^2}")])
    add("b_td_approx", 2, f="sqrt(x**2+y**2)", pt=["3", "4"], d=[str(sp.Rational(qx[0]) - 3), str(sp.Rational(qx[1]) - 4)], qtex=qy)
    add("b_td_err", 3, r="5", h="10", dr="1/10", dh="1/5")
    return L
