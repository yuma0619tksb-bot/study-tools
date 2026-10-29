"""力学(2020 Ⅱ類 杉・明 の第1〜6回の範囲: 強制振動・回転座標・慣性力・2体問題・質点系・連成振動)。

答えは SymPy で式を立てて求め、check では運動方程式を数値積分(mpmath.odefun)したり、
固有値を数値で求めたり、別の座標系で計算し直したりして突き合わせる。
"""
import random

import mpmath
import sympy as sp

from .core import kind, ptex, tex, tuple_same

SUBJECT = "力学"
PREFIX = "r"

mpmath.mp.dps = 30
t = sp.Symbol("t", nonnegative=True)
m, k, g, l, u0, w, w0, v0, F0, f0, a_, M, mu, V, alpha, l0 = sp.symbols(
    "m k g l u_0 omega omega_0 v_0 F_0 f_0 a M mu V alpha l_0", positive=True)

# 数値検算に使う「それらしい」値(ω と ω0 がぶつからないように選ぶ)
NUM = {m: sp.Rational(13, 10), k: sp.Rational(27, 10), g: sp.Rational(98, 10), l: sp.Rational(7, 10),
       u0: sp.Rational(3, 10), w: sp.Rational(17, 10), v0: sp.Rational(9, 10), F0: sp.Rational(11, 10),
       a_: sp.Rational(6, 10), M: sp.Rational(8, 10), V: sp.Rational(5, 10), l0: sp.Rational(4, 10), alpha: sp.Rational(15, 10)}
TS = [sp.Rational(3, 10), sp.Rational(11, 10), sp.Rational(23, 10), sp.Rational(37, 10)]


def ode_compare(rhs, y0, exact, subs, what):
    """y' = rhs(t, y) を数値積分し、exact(t) の各成分と比べる。rhs と exact は SymPy 式から作る。"""
    n = len(y0)
    ys = sp.symbols(f"y0:{n}")
    f = sp.lambdify((t, *ys), [sp.sympify(e).subs(subs) for e in rhs(ys)], "mpmath")
    sol = mpmath.odefun(lambda tt, yy: f(tt, *yy), 0, [mpmath.mpf(sp.N(sp.sympify(v).subs(subs), 30)) for v in y0])
    ex = [sp.lambdify(t, e.subs(subs), "mpmath") for e in exact]
    for tt in TS:
        got = sol(mpmath.mpf(tt))
        for i, e in enumerate(ex):
            a, b = got[i], e(mpmath.mpf(tt))
            if abs(a - b) > 1e-12 * max(1, abs(b)):
                raise AssertionError(f"{what}: 数値積分と式が t={tt} で合わない ({a} vs {b})")


def coef(c, sym):
    """c*sym を「係数 記号」の形の TeX に(係数1なら記号だけ)。"""
    c = sp.nsimplify(c)
    return tex(sym) if c == 1 else f"{tex(c)}{tex(sym)}"


# ============================================================ 第1回 強制振動
def _forced(p):
    A, B = p["kmul"], p["mmul"]
    W0sq = A * k / (B * m)
    xs = W0sq * u0 / (W0sq - w**2) * (sp.sin(w * t) - w / sp.sqrt(W0sq) * sp.sin(sp.sqrt(W0sq) * t))
    return A, B, W0sq, xs


def check_forced(p):
    A, B, W0sq, xs = _forced(p)
    # 運動方程式 B m x'' = -A k (x - u0 sin ωt) をそのまま数値積分する
    ode_compare(lambda y: [y[1], -A * k / (B * m) * (y[0] - u0 * sp.sin(w * t))], [0, 0], [xs], NUM, "forced")
    return xs


@kind("r_forced", check_forced, tuple_same)
def forced(p):
    A, B, W0sq, xs = _forced(p)
    ans = (w0**2 * u0 / (w0**2 - w**2) * (sp.sin(w * t) - w / w0 * sp.sin(w0 * t))).subs(w0, sp.sqrt(W0sq))
    kk, mm = coef(A, k), coef(B, m)
    f = {
        "title": "支点を振動させたばね振り子",
        "question": (f"ばね定数 ${kk}$ のばねの一端に質量 ${mm}$ のおもりを付けて吊るし、つり合った状態にある。"
                     f"時刻 $t=0$ 以降、上端の支点を $u(t)=u_0\\sin\\omega t$ で上下に振動させた。"
                     "つり合いの位置からのおもりの変位を $x(t)$(上向き正)として、$t\\ge 0$ での $x(t)$ を求めよ。"
                     "ただし $t=0$ でおもりは静止しており、$\\omega$ は固有角振動数と異なるとする。粘性抵抗は無視する。"),
        "tool": "ばねの伸びは「おもりの変位 − 支点の変位」なので、復元力は $-k'(x-u)$。運動方程式を $\\ddot x+\\omega_0^2x=f_0\\sin\\omega t$ の形にし、"
                "一般解 = 斉次方程式の一般解 + 定常解($A\\sin\\omega t$)として、最後に初期条件で定数を決める。",
        "steps": [
            f"${mm}\\ddot x=-{kk}(x-u_0\\sin\\omega t)$",
            f"$\\omega_0^2=\\dfrac{{{kk}}}{{{mm}}}$ とおくと $\\ddot x+\\omega_0^2x=\\omega_0^2u_0\\sin\\omega t$",
            r"定常解 $A\sin\omega t$ を代入: $(\omega_0^2-\omega^2)A=\omega_0^2u_0$ より $A=\dfrac{\omega_0^2u_0}{\omega_0^2-\omega^2}$",
            r"一般解 $x=C_3\sin\omega_0t+C_4\cos\omega_0t+A\sin\omega t$。$x(0)=0$ より $C_4=0$、$\dot x(0)=0$ より $C_3=-\dfrac{\omega}{\omega_0}A$",
        ],
        "answer": "$x(t)=%s$(ただし $\\omega_0^2=\\dfrac{%s}{%s}$)" % (
            r"\dfrac{\omega_0^2u_0}{\omega_0^2-\omega^2}\left(\sin\omega t-\dfrac{\omega}{\omega_0}\sin\omega_0 t\right)", kk, mm),
    }
    return f, ans


def check_forced_cos(p):
    W0sq = k / m
    xs = F0 / (m * (W0sq - w**2)) * (sp.cos(w * t) - sp.cos(sp.sqrt(W0sq) * t))
    ode_compare(lambda y: [y[1], -k / m * y[0] + F0 / m * sp.cos(w * t)], [0, 0], [xs], NUM, "forced_cos")
    return xs


@kind("r_forced_cos", check_forced_cos, tuple_same)
def forced_cos(p):
    ans = (F0 / (m * (w0**2 - w**2)) * (sp.cos(w * t) - sp.cos(w0 * t))).subs(w0, sp.sqrt(k / m))
    f = {
        "title": "外力 F₀cosωt による強制振動",
        "question": "なめらかな水平面上で、ばね定数 $k$ のばねにつながれた質量 $m$ の物体が、つり合いの位置に静止している。"
                    "$t=0$ から物体に外力 $F_0\\cos\\omega t$ を加え続けた。$\\omega_0=\\sqrt{k/m}\\ (\\neq\\omega)$ として、変位 $x(t)$ を求めよ。",
        "tool": "外力が $\\cos$ なので定常解も $A\\cos\\omega t$ と置く。一般解を作ってから $x(0)=0,\\ \\dot x(0)=0$ で定数を決める(第1回の手順と同じで、置く関数だけ変わる)。",
        "steps": [
            r"$m\ddot x=-kx+F_0\cos\omega t$ より $\ddot x+\omega_0^2x=\dfrac{F_0}{m}\cos\omega t$",
            r"定常解 $A\cos\omega t$: $A=\dfrac{F_0}{m(\omega_0^2-\omega^2)}$",
            r"一般解 $x=C_1\cos\omega_0t+C_2\sin\omega_0t+A\cos\omega t$",
            r"$x(0)=0$ より $C_1=-A$、$\dot x(0)=0$ より $C_2=0$",
        ],
        "answer": r"$x(t)=\dfrac{F_0}{m(\omega_0^2-\omega^2)}\left(\cos\omega t-\cos\omega_0 t\right)$",
    }
    return f, ans


def check_resonance(p):
    xs = f0 / (2 * w0**2) * (sp.sin(w0 * t) - w0 * t * sp.cos(w0 * t))
    sub = {**NUM, w0: sp.Rational(17, 10), f0: sp.Rational(7, 10)}
    ode_compare(lambda y: [y[1], -w0**2 * y[0] + f0 * sp.sin(w0 * t)], [0, 0], [xs], sub, "resonance")
    return xs


@kind("r_resonance", check_resonance, tuple_same)
def resonance(p):
    ans = f0 / (2 * w0**2) * (sp.sin(w0 * t) - w0 * t * sp.cos(w0 * t))
    f = {
        "title": "共振(ω=ω₀)のときの解",
        "question": "$\\ddot x+\\omega_0^2x=f_0\\sin\\omega_0 t$($\\omega=\\omega_0$、共振)を、$x(0)=0,\\ \\dot x(0)=0$ のもとで解け。"
                    "また、$t$ が大きいとき振幅がどうなるかを答えよ。",
        "tool": "$\\omega=\\omega_0$ では $A\\sin\\omega t$ が斉次方程式の解になってしまい、$A=\\dfrac{f_0}{\\omega_0^2-\\omega^2}$ が使えない(場合分け)。"
                "そこで定常解を $x_p=Bt\\cos\\omega_0 t$ と置き直す(2つのことの組み合わせ)。",
        "steps": [
            r"$x_p=Bt\cos\omega_0t$ を代入: $\ddot x_p+\omega_0^2x_p=-2B\omega_0\sin\omega_0t$ なので $B=-\dfrac{f_0}{2\omega_0}$",
            r"一般解 $x=C_1\cos\omega_0t+C_2\sin\omega_0t-\dfrac{f_0}{2\omega_0}t\cos\omega_0t$",
            r"$x(0)=0$ より $C_1=0$、$\dot x(0)=C_2\omega_0-\dfrac{f_0}{2\omega_0}=0$ より $C_2=\dfrac{f_0}{2\omega_0^2}$",
        ],
        "answer": r"$x(t)=\dfrac{f_0}{2\omega_0^2}\left(\sin\omega_0t-\omega_0t\cos\omega_0t\right)$。$t\cos\omega_0 t$ の項があるので、振幅は時間に比例して大きくなり続ける",
    }
    return f, ans


DAMP = {"under": (1, 2, 5), "critical": (1, 4, 4), "over": (1, 5, 4)}
# 教科書の形での表示(render で計算結果と一致することを確かめてから使う)
DAMP_TEX = {
    "under": (sp.exp(-t) * (sp.cos(2 * t) + sp.sin(2 * t) / 2), r"e^{-t}\left(\cos 2t+\dfrac{1}{2}\sin 2t\right)"),
    "critical": ((1 + 2 * t) * sp.exp(-2 * t), r"(1+2t)e^{-2t}"),
    "over": (sp.Rational(4, 3) * sp.exp(-t) - sp.Rational(1, 3) * sp.exp(-4 * t), r"\dfrac{4}{3}e^{-t}-\dfrac{1}{3}e^{-4t}"),
}


def _damped(p):
    mm, c, kk = DAMP[p["case"]]
    lam = sp.Symbol("lambda")
    roots = sp.solve(mm * lam**2 + c * lam + kk, lam)
    x = sp.Function("x")
    sol = sp.dsolve(sp.Eq(mm * x(t).diff(t, 2) + c * x(t).diff(t) + kk * x(t), 0), x(t), ics={x(0): 1, x(t).diff(t).subs(t, 0): 0}).rhs
    return mm, c, kk, roots, sp.simplify(sol)


def check_damped(p):
    mm, c, kk = DAMP[p["case"]]
    _, _, _, _, sol = _damped(p)
    ode_compare(lambda y: [y[1], (-c * y[1] - kk * y[0]) / mm], [1, 0], [sol], {}, "damped")
    disc = c * c - 4 * mm * kk
    return ("減衰振動" if disc < 0 else "臨界減衰" if disc == 0 else "過減衰", sol)


@kind("r_damped", check_damped, tuple_same)
def damped(p):
    mm, c, kk, roots, sol = _damped(p)
    disc = c * c - 4 * mm * kk
    name = "減衰振動" if disc < 0 else "臨界減衰" if disc == 0 else "過減衰"
    rt = ", ".join(tex(r) for r in roots)
    f = {
        "title": f"粘性抵抗のある振動({name})",
        "question": f"質量 ${mm}\\ \\mathrm{{kg}}$ の物体がばね定数 ${kk}\\ \\mathrm{{N/m}}$ のばねにつながれ、速度に比例する抵抗力 $-{c}\\dot x$ を受けて運動する。"
                    "$x(0)=1,\\ \\dot x(0)=0$ のとき、運動の種類(減衰振動・臨界減衰・過減衰)を判定し、$x(t)$ を求めよ。",
        "tool": "$x=e^{\\lambda t}$ を代入した特性方程式の判別式の符号で場合分けする。重解なら $(C_1+C_2t)e^{\\lambda t}$、複素数解なら $e^{-\\gamma t}(C_1\\cos+C_2\\sin)$ の形。",
        "steps": [
            f"${mm if mm != 1 else ''}\\ddot x+{c}\\dot x+{kk}x=0$。特性方程式 ${mm if mm != 1 else ''}\\lambda^2+{c}\\lambda+{kk}=0$",
            f"判別式 ${c}^2-4\\cdot{mm}\\cdot{kk}={disc}{'<0' if disc < 0 else '' if disc == 0 else '>0'}$ より{name}。$\\lambda={rt}$",
            "初期条件 $x(0)=1,\\ \\dot x(0)=0$ で定数を決める",
        ],
        "answer": f"{name}、$x(t)={DAMP_TEX[p['case']][1]}$",
    }
    if sp.simplify(DAMP_TEX[p["case"]][0] - sol) != 0:
        raise AssertionError("damped: 表示用の式が解と一致しない")
    return f, (name, sol)


# ============================================================ 第2回 回転する円管
def check_tube(p):
    if p["start"] == "speed":
        ex = v0 / w0 * sp.sinh(w0 * t); y0 = [0, v0]
    else:
        ex = a_ * sp.cosh(w0 * t); y0 = [a_, 0]
    sub = {**NUM, w0: sp.Rational(13, 10)}
    # 回転座標での運動方程式 r'' = ω0² r(遠心力だけが動径方向に働く)を数値積分
    ode_compare(lambda y: [y[1], w0**2 * y[0]], y0, [ex], sub, "tube")
    return ex


@kind("r_tube", check_tube, tuple_same)
def tube(p):
    if p["start"] == "speed":
        ans = v0 / w0 * sp.sinh(w0 * t)
        q_ic = "$t=0$ に $O$ から $v_0$ の速さで管内に入れた"
        ic = r"$r(0)=0,\ \dot r(0)=v_0$ より $C_1+C_2=0,\ \omega_0(C_1-C_2)=v_0$"
        title = "回転する円管内の質点"
        lv_tool = ""
    else:
        ans = a_ * sp.cosh(w0 * t)
        q_ic = "$t=0$ に $O$ から距離 $a$ の位置で、管に対して静かに放した"
        ic = r"$r(0)=a,\ \dot r(0)=0$ より $C_1=C_2=\dfrac{a}{2}$"
        title = "回転する円管内の質点(途中から放す)"
        lv_tool = "初期条件が変わるだけで、運動方程式は同じ。"
    f = {
        "title": title,
        "question": f"水平面内で、一端 $O$ のまわりに一定の角速度 $\\omega_0$ で回る細い円管の中を、質量 $3m$ の質点がなめらかに動く。{q_ic}。"
                    "質点の $O$ からの距離 $r$ を時刻 $t$ の関数として表せ。",
        "tool": "管と一緒に回る座標で考えると、動径方向に働く力は遠心力 $3mr\\omega_0^2$ だけ(管の壁からの力は管に垂直)。"
                "動径方向の運動方程式 $\\ddot r=\\omega_0^2r$ を解く。" + lv_tool,
        "steps": [
            r"動径方向: $3m\ddot r=3mr\omega_0^2$ より $\ddot r=\omega_0^2 r$",
            r"一般解 $r=C_1e^{\omega_0t}+C_2e^{-\omega_0t}$",
            ic,
        ],
        "answer": f"$r(t)={tex(ans)}$",
    }
    return f, ans


def check_tube_work(p):
    r = v0 / w0 * sp.sinh(w0 * t)
    # 慣性系で直接: 位置 (r cos ω0 t, r sin ω0 t)。トルク = r × F、F = 3m × 加速度
    X, Y = r * sp.cos(w0 * t), r * sp.sin(w0 * t)
    N = 3 * m * (X * Y.diff(t, 2) - Y * X.diff(t, 2))
    Wk = sp.integrate(sp.expand(sp.simplify(N * w0).rewrite(sp.exp)), (t, 0, t))
    K = sp.Rational(3, 2) * m * (X.diff(t) ** 2 + Y.diff(t) ** 2) - sp.Rational(3, 2) * m * v0**2
    L = 3 * m * (X * Y.diff(t) - Y * X.diff(t))
    return (sp.simplify(L), sp.simplify(N), sp.simplify(Wk.rewrite(sp.sinh)), sp.simplify(K))


@kind("r_tube_work", check_tube_work, tuple_same)
def tube_work(p):
    r = v0 / w0 * sp.sinh(w0 * t)
    L = 3 * m * r**2 * w0
    N = sp.simplify(L.diff(t))
    Wk = sp.simplify(sp.integrate(N * w0, (t, 0, t)))
    K = sp.simplify(sp.Rational(3, 2) * m * (r.diff(t) ** 2 + r**2 * w0**2) - sp.Rational(3, 2) * m * v0**2)
    f = {
        "title": "円管を回すトルクと仕事",
        "question": "前問(角速度 $\\omega_0$ の円管に、質量 $3m$ の質点を $O$ から速さ $v_0$ で入れた。$r(t)=\\dfrac{v_0}{\\omega_0}\\sinh\\omega_0t$)の続き。"
                    "質点の $O$ のまわりの角運動量 $L(t)$、円管を一定の角速度で回し続けるのに必要なトルク $N(t)$ を求めよ。"
                    "さらに、$t=0$ から $t$ までにトルクがした仕事が、質点の運動エネルギーの増加に等しいことを示せ。",
        "tool": "角運動量は $L=3mr^2\\omega_0$($\\omega_0$ 一定)。トルクは $N=\\dfrac{dL}{dt}$、仕事は $\\displaystyle\\int N\\omega_0\\,dt$。運動エネルギーは動径方向と回転方向の速度の2乗の和で書く。",
        "steps": [
            f"$L=3mr^2\\omega_0={tex(sp.simplify(L))}$",
            f"$N=\\dfrac{{dL}}{{dt}}={tex(N)}$",
            r"$W=\displaystyle\int_0^t N\omega_0\,dt=" + tex(Wk) + "$",
            r"$\Delta K=\dfrac{3}{2}m(\dot r^2+r^2\omega_0^2)-\dfrac{3}{2}mv_0^2=" + tex(K) + r"$ で $W$ と一致",
        ],
        "answer": f"$L={tex(sp.simplify(L))},\\quad N={tex(N)},\\quad W=\\Delta K={tex(K)}$",
    }
    return f, (sp.simplify(L), N, Wk, K)


# ============================================================ 第3回 慣性力
def check_elevator(p):
    kk = p["kmul"] * k
    up = sp.solve(sp.Eq(kk * sp.Symbol("x") - m * g, m * alpha), sp.Symbol("x"))[0]  # 慣性系: 上向きに加速
    dn = sp.solve(sp.Eq(kk * sp.Symbol("x") - m * g, -m * alpha), sp.Symbol("x"))[0]
    return sp.simplify(up - dn)


@kind("r_elevator", check_elevator, tuple_same)
def elevator(p):
    kk = coef(p["kmul"], k)
    ans = 2 * m * alpha / (p["kmul"] * k)
    f = {
        "title": "エレベーター内のばね(慣性力)",
        "question": f"エレベーターの中で、ばね定数 ${kk}$ のばねに質量 $m$ のおもりを吊るした。エレベーターが一定の加速度 $\\alpha$ で上昇しながら加速しているときと、"
                    "下向きに加速度 $\\alpha$ で加速しているときとで、ばねの伸びはどれだけ違うか。おもりはエレベーター内で静止しているとする。",
        "tool": "エレベーターと一緒に動く座標では、加速度と逆向きに慣性力 $-m\\vec\\alpha$ が働く。上向き加速なら下向きに $m\\alpha$ が加わり、見かけの重力が $m(g\\pm\\alpha)$ になる。",
        "steps": [
            f"上向き加速: ${kk}x_1=m(g+\\alpha)$",
            f"下向き加速: ${kk}x_2=m(g-\\alpha)$",
            f"$x_1-x_2=\\dfrac{{2m\\alpha}}{{{kk}}}={tex(ans)}$",
        ],
        "answer": f"上向き加速のときの方が ${tex(ans)}$ だけ長く伸びる",
    }
    return f, ans


def check_turntable(p):
    mu_, r_ = sp.Rational(p["mu"]), sp.Rational(p["r"])
    # 慣性系: 静止摩擦力が向心力 m r ω² をまかなえる最大の ω を二分法で
    lo, hi = 0.0, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if float(r_) * mid**2 <= float(mu_) * 9.8:
            lo = mid
        else:
            hi = mid
    return lo


@kind("r_turntable", check_turntable, lambda a, b: abs(float(a) - b) < 1e-9)
def turntable(p):
    mu_, r_ = sp.Rational(p["mu"]), sp.Rational(p["r"])
    wmax = sp.sqrt(mu_ * sp.Rational(98, 10) / r_)
    val = float(wmax)
    f = {
        "title": "回転円盤上の物体(遠心力と摩擦)",
        "question": f"水平に回転する円盤の上、中心から ${float(r_):g}\\ \\mathrm{{m}}$ の位置に小物体を置いた。静止摩擦係数を ${float(mu_):g}$、$g=9.8\\ \\mathrm{{m/s^2}}$ とするとき、"
                    "物体が円盤上ですべらないための円盤の角速度の最大値を有効数字3桁で求めよ。",
        "tool": "円盤と一緒に回る座標では、物体に遠心力 $mr\\omega^2$ が外向きに働き、それを静止摩擦力が支える。最大摩擦力 $\\mu mg$ と等しくなるときが限界。",
        "steps": [
            r"つり合い: $mr\omega^2=f\le\mu mg$",
            r"$\omega\le\sqrt{\dfrac{\mu g}{r}}=\sqrt{\dfrac{%g\times 9.8}{%g}}$" % (float(mu_), float(r_)),
        ],
        "answer": "$\\omega_{\\max}=%s\\ \\mathrm{rad/s}$" % f"{val:.3g}",
    }
    return f, val


def check_disk_walk(p):
    om, vv, rr = sp.symbols("omega v r", positive=True)
    # 慣性系での位置: 円盤座標 (2r - vt, 0) を角 ωt だけ回す。加速度×m を円盤座標に戻すと必要な力
    xp = 2 * rr - vv * t
    X, Y = xp * sp.cos(om * t), xp * sp.sin(om * t)
    ax, ay = X.diff(t, 2), Y.diff(t, 2)
    Fx = sp.simplify(m * (ax * sp.cos(om * t) + ay * sp.sin(om * t)))
    Fy = sp.simplify(m * (-ax * sp.sin(om * t) + ay * sp.cos(om * t)))
    return (Fx, Fy)


@kind("r_disk_walk", check_disk_walk, tuple_same)
def disk_walk(p):
    om, vv, rr = sp.symbols("omega v r", positive=True)
    xp = 2 * rr - vv * t
    Fcf = (m * om**2 * xp, 0)  # 遠心力
    Fco = (0, 2 * m * om * vv)  # コリオリ力 -2m ω×v' (v'=(-v,0), ω=ωz)
    F = (sp.expand(-Fcf[0] - Fco[0]), sp.expand(-Fcf[1] - Fco[1]))
    f = {
        "title": "回転円盤上を歩く人に必要な力(遠心力とコリオリ力)",
        "question": "角速度 $\\omega$(上から見て反時計回り)で回る円盤上で、質量 $m$ の人が、円盤に固定した座標の点 $P(2r,0)$ を $t=0$ に出発し、"
                    "円盤座標で一定の速度 $\\vec v=(-v,0)$ で中心に向かって歩く。この運動をするために、各時刻 $t$ に人が受けなければならない力(床からの摩擦力など)を円盤座標の成分で求めよ。",
        "tool": "円盤座標では加速度が $0$ なので、「実際の力 + 遠心力 + コリオリ力 $=0$」。遠心力は $m\\omega^2\\vec r'$、コリオリ力は $-2m\\vec\\omega\\times\\vec v'$。2つの慣性力の向きを外積で確かめるのがポイント(組み合わせ)。",
        "steps": [
            r"位置 $\vec r'=(2r-vt,\ 0)$、速度 $\vec v'=(-v,\ 0)$、加速度 $\vec a'=\vec 0$",
            r"遠心力 $m\omega^2\vec r'=(m\omega^2(2r-vt),\ 0)$",
            r"コリオリ力 $-2m\vec\omega\times\vec v'=-2m\omega\hat z\times(-v\hat x)=(0,\ 2m\omega v)$",
            r"$\vec F+(\text{遠心力})+(\text{コリオリ力})=\vec 0$",
        ],
        "answer": f"$\\vec F=\\left({tex(F[0])},\\ {tex(F[1])}\\right)$(中心向きに大きさ $m\\omega^2(2r-vt)$、$y$ 軸の負の向きに大きさ $2m\\omega v$)",
    }
    return f, F


# ============================================================ 第4回 2体問題・換算質量
def check_reduced(p):
    m1, m2 = p["a"] * m, p["b"] * m
    # 2体の運動方程式から相対座標の式を作り、係数を読む
    r = sp.Symbol("rddot")
    F = sp.Symbol("F")
    # m1 x1'' = F, m2 x2'' = -F → r'' = x1''-x2'' = F/m1 + F/m2 → μ = F/r''
    return sp.simplify(F / (F / m1 + F / m2))


@kind("r_reduced", check_reduced, tuple_same)
def reduced(p):
    a, b = p["a"], p["b"]
    ans = sp.Rational(a * b, a + b) * m
    f = {
        "title": "換算質量",
        "question": f"質量 ${coef(a, m)}$ と ${coef(b, m)}$ の2つの質点が、互いの間に働く力だけで運動している。相対運動の運動方程式に現れる換算質量 $\\mu$ を求めよ。",
        "tool": "2体の運動方程式から相対座標 $\\vec r=\\vec r_1-\\vec r_2$ の式を作ると $\\mu\\ddot{\\vec r}=\\vec F$、$\\dfrac{1}{\\mu}=\\dfrac{1}{m_1}+\\dfrac{1}{m_2}$。",
        "steps": [r"$m_1\ddot{\vec r}_1=\vec F,\ m_2\ddot{\vec r}_2=-\vec F$ より $\ddot{\vec r}=\left(\dfrac{1}{m_1}+\dfrac{1}{m_2}\right)\vec F$",
                  f"$\\mu=\\dfrac{{m_1m_2}}{{m_1+m_2}}=\\dfrac{{{coef(a, m)}\\cdot {coef(b, m)}}}{{{coef(a + b, m)}}}$"],
        "answer": f"$\\mu={tex(ans)}$",
    }
    return f, ans


def check_twobody_rot(p):
    a, b, c = p["a"], p["b"], sp.Rational(p["c"])
    # 重心まわりに、質量 a m の質点だけを見る: 回転半径 r·b/(a+b)、向心力 = ばねの力 k(r-l0)
    r = c * l0
    om = sp.Symbol("Om", positive=True)
    sol = sp.solve(sp.Eq(a * m * (r * b / (a + b)) * om**2, k * (r - l0)), om)
    return sp.simplify(sol[0])


@kind("r_twobody_rot", check_twobody_rot, tuple_same)
def twobody_rot(p):
    a, b, c = p["a"], p["b"], sp.Rational(p["c"])
    mu_ = sp.Rational(a * b, a + b) * m
    w2 = sp.simplify(k * (c - 1) / (mu_ * c))
    ans = sp.sqrt(w2)
    f = {
        "title": "ばねでつながった2質点の回転",
        "question": f"自然長 $l_0$、ばね定数 $k$ のばねの両端に質量 ${coef(a, m)}$ と ${coef(b, m)}$ の質点がつながれ、なめらかな水平面上で重心 $G$ のまわりを一定の角速度 $\\omega$ で回っている。"
                    f"ばねの長さが ${tex(c * l0)}$ に保たれているとき、$\\omega$ を求めよ。換算質量を使って解き、重心のまわりで片方の質点だけを考えても同じ結果になることを確かめよ。",
        "tool": "相対運動は換算質量 $\\mu$ の1体問題になるので、$\\mu r\\omega^2=k(r-l_0)$(向心力=ばねの力)。確かめは、重心からの距離 $\\dfrac{m_2}{m_1+m_2}r$ を回る $m_1$ の運動方程式で。",
        "steps": [
            f"$\\mu=\\dfrac{{{coef(a, m)}\\cdot {coef(b, m)}}}{{{coef(a + b, m)}}}={tex(mu_)}$",
            f"$\\mu r\\omega^2=k(r-l_0)$ に $r={tex(c * l0)}$ を代入",
            f"確かめ: ${coef(a, m)}$ は重心から $\\dfrac{{{b}}}{{{a + b}}}r$ を回るので ${coef(a, m)}\\cdot\\dfrac{{{b}}}{{{a + b}}}r\\omega^2=k(r-l_0)$ で同じ式",
        ],
        "answer": f"$\\omega=\\sqrt{{{tex(w2)}}}$",
    }
    return f, ans


def check_twobody_vib(p):
    a, b = p["a"], p["b"]
    Mx = sp.diag(a * m, b * m)
    K = sp.Matrix([[k, -k], [-k, k]])
    ev = (Mx.inv() * K).eigenvals()
    nz = [e for e in ev if sp.simplify(e) != 0]
    return sp.simplify(sp.sqrt(nz[0]))


@kind("r_twobody_vib", check_twobody_vib, tuple_same)
def twobody_vib(p):
    a, b = p["a"], p["b"]
    mu_ = sp.Rational(a * b, a + b) * m
    ans = sp.sqrt(sp.simplify(k / mu_))
    f = {
        "title": "ばねでつながった2物体の振動",
        "question": f"なめらかな水平面上で、ばね定数 $k$ のばねの両端に質量 ${coef(a, m)}$ と ${coef(b, m)}$ の物体がつながれている。両方を引き離して静かに放したとき、ばねの伸縮の角振動数を求めよ。",
        "tool": "ばねの伸び $x=x_1-x_2-l_0$ の運動方程式は換算質量 $\\mu$ を使って $\\mu\\ddot x=-kx$ になる(重心は静止したまま)。",
        "steps": [f"$\\mu={tex(mu_)}$", r"$\mu\ddot x=-kx$ より $\omega=\sqrt{k/\mu}$"],
        "answer": f"$\\omega=\\sqrt{{{tex(sp.simplify(k / mu_))}}}$",
    }
    return f, ans


# ============================================================ 第5回 質点系
def _system(p):
    s = p["s"]
    ms = [3 * m, 2 * m, 2 * m]
    rs = [sp.Matrix([0, 0]), sp.Matrix([s * a_, 0]), sp.Matrix([0, s * a_])]
    vs = [sp.Matrix([0, 0]), sp.Matrix([0, s * V]), sp.Matrix([-s * V, 0])]
    return ms, rs, vs


def check_system(p):
    ms, rs, vs = _system(p)
    Mt = sum(ms)
    K = sum(sp.Rational(1, 2) * mi * (vi.dot(vi)) for mi, vi in zip(ms, vs))
    L = sum(mi * (ri[0] * vi[1] - ri[1] * vi[0]) for mi, ri, vi in zip(ms, rs, vs))
    VG = sum((mi * vi for mi, vi in zip(ms, vs)), sp.zeros(2, 1)) / Mt
    return (tuple(sp.simplify(c) for c in VG), sp.simplify(K), sp.simplify(L))


@kind("r_system", check_system, tuple_same)
def system(p):
    s = p["s"]
    ms, rs, vs = _system(p)
    Mt = sum(ms)
    RG = sum((mi * ri for mi, ri in zip(ms, rs)), sp.zeros(2, 1)) / Mt
    VG = sum((mi * vi for mi, vi in zip(ms, vs)), sp.zeros(2, 1)) / Mt
    KG = sp.Rational(1, 2) * Mt * VG.dot(VG)
    Krel = sum(sp.Rational(1, 2) * mi * ((vi - VG).dot(vi - VG)) for mi, vi in zip(ms, vs))
    LG = Mt * (RG[0] * VG[1] - RG[1] * VG[0])
    Lrel = sum(mi * ((ri - RG)[0] * (vi - VG)[1] - (ri - RG)[1] * (vi - VG)[0]) for mi, ri, vi in zip(ms, rs, vs))
    vec = lambda v: f"\\left({tex(sp.simplify(v[0]))},\\ {tex(sp.simplify(v[1]))}\\right)"
    K = sp.simplify(KG + Krel)
    L = sp.simplify(LG + Lrel)
    f = {
        "title": "3つの質点の重心運動と相対運動",
        "question": f"質量 $3m$ の質点1と、質量 $2m$ の質点2・3が $xy$ 面内を運動している。ある瞬間、質点1・2・3はそれぞれ $(0,0)$、$({tex(s * a_)},0)$、$(0,{tex(s * a_)})$ にあり、"
                    f"速度は $(0,0)$、$(0,{tex(s * V)})$、$({tex(-s * V)},0)$ であった。(1) 重心速度を求めよ。(2) 全運動エネルギーを、各質点の和と「重心運動+相対運動」の両方で求めて等しいことを示せ。"
                    "(3) 原点のまわりの全角運動量を同様に2通りで求めよ。",
        "tool": "重心 $\\vec R=\\dfrac{\\sum m_i\\vec r_i}{M}$、$\\vec V_G=\\dfrac{\\sum m_i\\vec v_i}{M}$。相対速度 $\\vec v_i-\\vec V_G$ を使うと $K=\\dfrac{1}{2}MV_G^2+\\sum\\dfrac{1}{2}m_i|\\vec v_i-\\vec V_G|^2$、$\\vec L=\\vec R\\times M\\vec V_G+\\sum(\\vec r_i-\\vec R)\\times m_i(\\vec v_i-\\vec V_G)$。",
        "steps": [
            f"$M=7m$、$\\vec R={vec(RG)}$、$\\vec V_G={vec(VG)}$",
            f"各質点の和: $K=\\dfrac{{1}}{{2}}(2m)({tex(s * V)})^2\\times 2={tex(K)}$",
            f"分離: $\\dfrac{{1}}{{2}}MV_G^2={tex(sp.simplify(KG))}$、相対運動 ${tex(sp.simplify(Krel))}$、和 ${tex(K)}$",
            f"角運動量: 和で ${tex(L)}$、分離で ${tex(sp.simplify(LG))}+({tex(sp.simplify(Lrel))})={tex(L)}$",
        ],
        "answer": f"$\\vec V_G={vec(VG)}$、$K={tex(K)}$、$L_z={tex(L)}$(どちらの求め方でも一致)",
    }
    return f, (tuple(sp.simplify(c) for c in VG), K, L)


def check_collision(p):
    a, b, e = p["a"], p["b"], sp.Rational(p["e"])
    v = sp.Symbol("v", positive=True)
    x1, x2 = sp.symbols("x1 x2")
    sol = sp.solve([sp.Eq(a * m * v, a * m * x1 + b * m * x2), sp.Eq(x2 - x1, e * v)], [x1, x2])
    K0 = sp.Rational(1, 2) * a * m * v**2
    K1 = sp.Rational(1, 2) * a * m * sol[x1] ** 2 + sp.Rational(1, 2) * b * m * sol[x2] ** 2
    return (sp.simplify(sol[x1]), sp.simplify(sol[x2]), sp.simplify(K1 - K0))


@kind("r_collision", check_collision, tuple_same)
def collision(p):
    a, b, e = p["a"], p["b"], sp.Rational(p["e"])
    v = sp.Symbol("v", positive=True)
    m1, m2 = a * m, b * m
    v1 = sp.simplify((m1 - e * m2) / (m1 + m2) * v)
    v2 = sp.simplify((1 + e) * m1 / (m1 + m2) * v)
    mu_ = m1 * m2 / (m1 + m2)
    dK = sp.simplify(-sp.Rational(1, 2) * mu_ * (1 - e**2) * v**2)
    f = {
        "title": p.get("title", "2物体の衝突"),
        "question": f"なめらかな直線上で、速度 $v$ で進む質量 ${coef(a, m)}$ の物体が、静止している質量 ${coef(b, m)}$ の物体に正面衝突した。反発係数を ${tex(e)}$ とするとき、"
                    "衝突後のそれぞれの速度と、衝突で失われた運動エネルギーを求めよ。",
        "tool": "運動量保存 $m_1v=m_1v_1'+m_2v_2'$ と反発係数の式 $v_2'-v_1'=e(v-0)$ を連立する。失われるエネルギーは重心運動の分が変わらないので、相対運動の分 $\\dfrac{1}{2}\\mu(1-e^2)v^2$ になる(第5回の分離の考え方)。",
        "steps": [
            f"${coef(a, m)}v={coef(a, m)}v_1'+{coef(b, m)}v_2'$、$v_2'-v_1'={tex(e)}v$",
            f"$v_1'={tex(v1)}$、$v_2'={tex(v2)}$",
            f"換算質量 $\\mu={tex(sp.simplify(mu_))}$ より $\\Delta K=-\\dfrac{{1}}{{2}}\\mu(1-e^2)v^2$",
        ],
        "answer": f"$v_1'={tex(v1)},\\quad v_2'={tex(v2)}$、失われた運動エネルギー ${tex(-dK)}$",
    }
    return f, (v1, v2, dK)


# ============================================================ 第6回 連成振動
def _eig_check(Mx, K, expect, what):
    """M^{-1}K の固有値を数値で求め、expect(ω² の式の並び)と比べる。"""
    sub = {m: sp.Rational(13, 10), k: sp.Rational(27, 10), g: sp.Rational(98, 10), l: sp.Rational(7, 10), sp.Symbol("kp", positive=True): sp.Rational(19, 10)}
    A = (Mx.inv() * K).subs(sub)
    ev = sorted(float(e) for e in mpmath.eig(mpmath.matrix([[float(x) for x in A.row(i)] for i in range(A.rows)]))[0])
    ex = sorted(float(e.subs(sub)) for e in expect)
    for a, b in zip(ev, ex):
        if abs(a - b) > 1e-9 * max(1, abs(b)):
            raise AssertionError(f"{what}: 固有値が合わない {ev} vs {ex}")
    return tuple(sorted(expect, key=lambda e: float(e.subs(sub))))


def check_pend(p):
    Mx = sp.diag(m, m)
    K = sp.Matrix([[m * g / l + k, -k], [-k, m * g / l + k]])
    return _eig_check(Mx, K, [g / l, g / l + 2 * k / m], "pend")


@kind("r_pend", check_pend, tuple_same)
def pend(p):
    w1sq, w2sq = g / l, g / l + 2 * k / m
    f = {
        "title": "ばねでつないだ2つの振り子(基準振動)",
        "question": "長さ $l$ の糸に質量 $m$ の質点を付けた振り子2つを、ばね定数 $k$ のばねでつないだ(静止状態でばねは自然長)。微小振動で、各質点の静止位置からの右向きのずれを $x_1,x_2$ とする。"
                    "(1) 運動方程式を立てよ。(2) $x_1=C_1\\sin(\\omega t+\\alpha),\\ x_2=C_2\\sin(\\omega t+\\alpha)$ とおいて基準振動の角振動数と $C_2/C_1$ を求めよ。",
        "tool": "微小振動では重力の復元力が $-\\dfrac{mg}{l}x$、ばねの力はのび $x_1-x_2$ に比例。解を代入すると $C_1,C_2$ の連立1次方程式になり、$C_1=C_2=0$ 以外の解をもつ条件(係数行列式 $=0$)から $\\omega$ が決まる。",
        "steps": [
            r"$m\ddot x_1=-\dfrac{mg}{l}x_1-k(x_1-x_2)$、$m\ddot x_2=-\dfrac{mg}{l}x_2+k(x_1-x_2)$",
            r"代入: $\left(\dfrac{g}{l}+\dfrac{k}{m}-\omega^2\right)C_1-\dfrac{k}{m}C_2=0$ など",
            r"行列式 $=0$: $\left(\dfrac{g}{l}+\dfrac{k}{m}-\omega^2\right)^2=\left(\dfrac{k}{m}\right)^2$",
        ],
        "answer": r"$\omega_1=\sqrt{\dfrac{g}{l}}$($C_2/C_1=1$、同じ向きにそろって振れる)、$\omega_2=\sqrt{\dfrac{g}{l}+\dfrac{2k}{m}}$($C_2/C_1=-1$、逆向きに振れる)",
    }
    return f, (w1sq, w2sq)


def check_springs3(p):
    kp = sp.Symbol("kp", positive=True)
    Mx = sp.diag(m, m)
    K = sp.Matrix([[k + kp, -kp], [-kp, k + kp]])
    return _eig_check(Mx, K, [k / m, (k + 2 * kp) / m], "springs3")


@kind("r_springs3", check_springs3, tuple_same)
def springs3(p):
    f = {
        "title": "3本のばねでつないだ2物体の連成振動",
        "question": "なめらかな水平面上で、壁―ばね $k$ ―質量 $m$ ―ばね $k'$ ―質量 $m$ ―ばね $k$ ―壁 の順につながれている(静止状態で全ばねは自然長)。基準振動の角振動数と、それぞれの振動の様子を答えよ。",
        "tool": "前問(振り子)と同じ手順。重力の項がばね $k$ に置き換わっただけ。$x_1=x_2$(同位相)と $x_1=-x_2$(逆位相)の2つが基準振動になる。",
        "steps": [
            r"$m\ddot x_1=-kx_1-k'(x_1-x_2)$、$m\ddot x_2=-kx_2+k'(x_1-x_2)$",
            r"行列式 $=0$: $\left(\dfrac{k+k'}{m}-\omega^2\right)^2=\left(\dfrac{k'}{m}\right)^2$",
        ],
        "answer": r"$\omega_1=\sqrt{\dfrac{k}{m}}$(同じ向きに動き、真ん中のばねは伸び縮みしない)、$\omega_2=\sqrt{\dfrac{k+2k'}{m}}$(逆向きに動く)",
    }
    kp = sp.Symbol("kp", positive=True)
    return f, (k / m, (k + 2 * kp) / m)


def check_unequal(p):
    Mx = sp.diag(m, 2 * m)
    K = sp.Matrix([[2 * k, -k], [-k, 2 * k]])
    return _eig_check(Mx, K, [(3 - sp.sqrt(3)) / 2 * k / m, (3 + sp.sqrt(3)) / 2 * k / m], "unequal")


@kind("r_unequal", check_unequal, tuple_same)
def unequal(p):
    lo, hi = (3 - sp.sqrt(3)) / 2 * k / m, (3 + sp.sqrt(3)) / 2 * k / m
    f = {
        "title": "質量が違う2物体の連成振動",
        "question": "なめらかな水平面上で、壁―ばね $k$ ―質量 $m$ ―ばね $k$ ―質量 $2m$ ―ばね $k$ ―壁 とつながれている。基準振動の角振動数 $\\omega$ と、それぞれの振幅比 $C_2/C_1$ を求めよ。",
        "tool": "質量が違うと同位相・逆位相の対称な解にはならないので、行列式 $=0$ の2次方程式をきちんと解く。$\\omega^2$ を求めてから振幅比を連立方程式の1本目に戻して出す。",
        "steps": [
            r"$m\ddot x_1=-2kx_1+kx_2$、$2m\ddot x_2=kx_1-2kx_2$",
            r"$s=k/m$ とおくと $(2s-\omega^2)(s-\omega^2)-\dfrac{s^2}{2}=0$、つまり $\omega^4-3s\omega^2+\dfrac{3}{2}s^2=0$",
            r"$\omega^2=\dfrac{3\pm\sqrt3}{2}\,\dfrac{k}{m}$。1本目から $\dfrac{C_2}{C_1}=\dfrac{2s-\omega^2}{s}=\dfrac{1\mp\sqrt3}{2}$",
        ],
        "answer": r"$\omega^2=\dfrac{3-\sqrt3}{2}\dfrac{k}{m}$ のとき $C_2/C_1=\dfrac{1+\sqrt3}{2}$(同じ向き)、$\omega^2=\dfrac{3+\sqrt3}{2}\dfrac{k}{m}$ のとき $C_2/C_1=\dfrac{1-\sqrt3}{2}$(逆向き)",
    }
    return f, (lo, hi)


def check_beats(p):
    w1, w2 = sp.sqrt(g / l), sp.sqrt(g / l + 2 * k / m)
    x1 = a_ / 2 * (sp.cos(w1 * t) + sp.cos(w2 * t))
    x2 = a_ / 2 * (sp.cos(w1 * t) - sp.cos(w2 * t))
    ode_compare(lambda y: [y[2], y[3], -g / l * y[0] - k / m * (y[0] - y[1]), -g / l * y[1] + k / m * (y[0] - y[1])],
                [a_, 0, 0, 0], [x1, x2], NUM, "beats")
    return (x1, x2)


@kind("r_beats", check_beats, tuple_same)
def beats(p):
    w1, w2 = sp.sqrt(g / l), sp.sqrt(g / l + 2 * k / m)
    x1 = a_ / 2 * (sp.cos(w1 * t) + sp.cos(w2 * t))
    x2 = a_ / 2 * (sp.cos(w1 * t) - sp.cos(w2 * t))
    f = {
        "title": "連成振り子の一般解とうなり",
        "question": "ばね $k$ でつないだ2つの振り子(長さ $l$、質量 $m$)で、$t=0$ に質点1だけを $a$ ずらして静かに放した($x_1(0)=a,\\ x_2(0)=0$、速度はともに $0$)。"
                    "$x_1(t),\\ x_2(t)$ を求め、ばねが弱いとき($k$ が小さいとき)どのような運動になるかを説明せよ。",
        "tool": "一般解は2つの基準振動の重ね合わせ。初期条件で4つの定数を決める。和積の公式で $\\cos$ の和を積にすると、振幅がゆっくり変わる「うなり」が見える(基準振動と初期条件の組み合わせ)。",
        "steps": [
            r"一般解 $x_1=A\cos\omega_1t+B\cos\omega_2t$、$x_2=A\cos\omega_1t-B\cos\omega_2t$(速度0なので sin の項はない)",
            r"$x_1(0)=A+B=a$、$x_2(0)=A-B=0$ より $A=B=\dfrac{a}{2}$",
            r"$x_1=a\cos\dfrac{\omega_2-\omega_1}{2}t\cos\dfrac{\omega_2+\omega_1}{2}t$、$x_2=a\sin\dfrac{\omega_2-\omega_1}{2}t\sin\dfrac{\omega_2+\omega_1}{2}t$",
        ],
        "answer": r"$x_1=\dfrac{a}{2}(\cos\omega_1t+\cos\omega_2t),\ x_2=\dfrac{a}{2}(\cos\omega_1t-\cos\omega_2t)$($\omega_1=\sqrt{g/l},\ \omega_2=\sqrt{g/l+2k/m}$)。$k$ が小さいと $\omega_1\approx\omega_2$ で、振動のエネルギーが2つの振り子の間をゆっくり行き来する(うなり)",
    }
    return f, (x1, x2)


# ============================================================ 出題リスト
def specs(rng):
    L = []
    add = lambda kind_, lv, **p: L.append((kind_, lv, p))
    # 第1回 強制振動・減衰
    add("r_forced", 1, kmul=4, mmul=3)
    km, mm = rng.choice([(2, 1), (3, 2), (5, 2), (2, 3)])
    add("r_forced", 1, kmul=km, mmul=mm)
    add("r_forced_cos", 2)
    add("r_resonance", 3)
    add("r_damped", 1, case="under")
    add("r_damped", 2, case="critical")
    add("r_damped", 2, case="over")
    # 第2回 回転する円管
    add("r_tube", 1, start="speed")
    add("r_tube", 2, start="rest")
    add("r_tube_work", 3)
    # 第3回 慣性力
    add("r_elevator", 1, kmul=rng.choice([3, 2, 4]))
    mu_, r_ = rng.choice([("2/5", "1/2"), ("3/10", "2/5"), ("1/2", "3/10")])
    add("r_turntable", 1, mu=mu_, r=r_)
    add("r_disk_walk", 3)
    # 第4回 2体問題
    a, b = rng.choice([(1, 3), (2, 3), (1, 2)])
    add("r_reduced", 1, a=a, b=b)
    add("r_twobody_rot", 2, a=1, b=3, c="5/4")
    a, b, c = rng.choice([(1, 2, "3/2"), (2, 3, "4/3"), (1, 1, "2")])
    add("r_twobody_rot", 2, a=a, b=b, c=c)
    a, b = rng.choice([(1, 3), (2, 3), (1, 4)])
    add("r_twobody_vib", 1, a=a, b=b)
    # 第5回 質点系
    add("r_system", 2, s=3)
    add("r_system", 2, s=rng.choice([1, 2]))
    a, b, e = rng.choice([(1, 2, "1/2"), (2, 1, "1/3"), (1, 3, "1/2")])
    add("r_collision", 1, a=a, b=b, e=e)
    a, b, e = rng.choice([(3, 1, "1/2"), (2, 3, "1/4"), (1, 1, "1/3")])
    add("r_collision", 2, a=a, b=b, e=e, title="反発係数と失われる運動エネルギー")
    # 第6回 連成振動
    add("r_pend", 1)
    add("r_springs3", 2)
    add("r_unequal", 3)
    add("r_beats", 3)
    return L
