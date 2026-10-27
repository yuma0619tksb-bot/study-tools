"""解析学: 望遠鏡和・収束判定・絶対/条件収束・収束半径・パラメータの場合分け。

各 render 関数は params から問題文・途中式・答えを SymPy で計算し、
(fields, value) を返す。check 関数は value を別ルート(厳密な部分和、
数値評価による判定など)で求め直す。
"""
import sympy as sp

from . import series_tools as st
from .core import N, R, btex, kind, m, n, ptex, tex, tuple_same

SUBJECT = "解析学"
PREFIX = "k"
oo = sp.oo


def S(lo="1"):
    return r"\displaystyle\sum_{n=%s}^{\infty}" % lo


def parse(e):
    return sp.sympify(e, locals={"n": n})


def exact_partial_sums(term, formula, lo, upto=14):
    for K in range(lo, upto):
        lhs = sum(term.subs(n, k) for k in range(lo, K + 1))
        rhs = formula.subs(N, K)
        if sp.simplify(lhs - rhs) != 0:
            raise AssertionError(f"部分和の式が N={K} で合わない: {lhs} != {rhs}")


# ============================================================ 望遠鏡和
def _tel_a(p):
    a = p["a"]
    term = 1 / (n * (n + a))
    formula = sp.Rational(1, a) * (sp.harmonic(a) - sum(1 / (N + k) for k in range(1, a + 1)))
    return term, formula, sp.harmonic(a) / a


def check_tel_a(p):
    term, formula, _ = _tel_a(p)
    exact_partial_sums(term, formula, 1)
    return sp.summation(term, (n, 1, oo))


@kind("k_tel_a", check_tel_a, tuple_same)
def tel_a(p):
    a = p["a"]
    _, _, val = _tel_a(p)
    head = " + ".join(r"\dfrac{1}{%d}" % k if k > 1 else "1" for k in range(1, a + 1))
    tail = " + ".join(r"\dfrac{1}{N+%d}" % k for k in range(1, a + 1))
    f = {
        "title": "部分分数分解で望遠鏡和",
        "question": "級数 $%s \\dfrac{1}{n(n+%d)}$ の和を求めよ。部分和 $S_N$ を求めてから極限をとること。" % (S(), a),
        "tool": "分母が積なので部分分数分解すると、$%d$ つ離れた項どうしが打ち消し合う(望遠鏡和)。部分和を $N$ の式で書いてから $N\\to\\infty$ とする。" % a,
        "steps": [
            r"$\dfrac{1}{n(n+%d)}=\dfrac{1}{%d}\left(\dfrac{1}{n}-\dfrac{1}{n+%d}\right)$" % (a, a, a),
            r"$S_N=\dfrac{1}{%d}\left\{\left(%s\right)-\left(%s\right)\right\}$" % (a, head, tail),
            r"$N\to\infty$ で $\dfrac{1}{N+k}\to 0$ より $S_N\to\dfrac{1}{%d}\left(%s\right)=%s$" % (a, head, tex(val)),
        ],
        "answer": m(val),
    }
    return f, val


def _tel_b(p):
    k, b = p["k"], p["b"]
    term = 1 / ((k * n + b) * (k * n + b + k))
    formula = sp.Rational(1, k) * (sp.Rational(1, k + b) - 1 / (k * N + k + b))
    return term, formula, sp.Rational(1, k * (k + b))


def check_tel_b(p):
    term, formula, _ = _tel_b(p)
    exact_partial_sums(term, formula, 1)
    return sp.summation(term, (n, 1, oo))


@kind("k_tel_b", check_tel_b, tuple_same)
def tel_b(p):
    k, b = p["k"], p["b"]
    _, formula, val = _tel_b(p)
    u, v = tex(k * n + b), tex(k * n + b + k)
    f = {
        "title": "1次式の積の望遠鏡和",
        "question": "級数 $%s \\dfrac{1}{(%s)(%s)}$ の和を求めよ。途中式も書くこと。" % (S(), u, v),
        "tool": "2つの1次式の差が定数 $%d$ なので部分分数分解できる。分解した後の項は次の $n$ の項と打ち消し合う。" % k,
        "steps": [
            r"$\dfrac{1}{(%s)(%s)}=\dfrac{1}{%d}\left(\dfrac{1}{%s}-\dfrac{1}{%s}\right)$" % (u, v, k, u, v),
            r"$S_N=\dfrac{1}{%d}\left(%s-\dfrac{1}{%s}\right)$" % (k, tex(sp.Rational(1, k + b)), tex(k * N + k + b)),
            r"$N\to\infty$ で $S_N\to %s$" % tex(val),
        ],
        "answer": m(val),
    }
    return f, val


def _tel_quad(p):
    c = p["c"]
    term = 1 / (n**2 + (2 * c + 1) * n + c * (c + 1))
    formula = sp.Rational(1, c + 1) - 1 / (N + c + 1)
    return term, formula, sp.Rational(1, c + 1)


def check_tel_quad(p):
    term, formula, _ = _tel_quad(p)
    exact_partial_sums(term, formula, 1)
    return sp.summation(term, (n, 1, oo))


@kind("k_tel_quad", check_tel_quad, tuple_same)
def tel_quad(p):
    c = p["c"]
    term, formula, val = _tel_quad(p)
    den = n**2 + (2 * c + 1) * n + c * (c + 1)
    f = {
        "title": "因数分解してから望遠鏡和",
        "question": "級数 $%s \\dfrac{1}{%s}$ の和を求めよ。途中式も書くこと。" % (S(), tex(den)),
        "tool": "分母の2次式を因数分解すると差が1の1次式の積になるので、部分分数分解して望遠鏡和にする。",
        "steps": [
            "$%s=(n+%d)(n+%d)$" % (tex(den), c, c + 1),
            r"$\dfrac{1}{(n+%d)(n+%d)}=\dfrac{1}{n+%d}-\dfrac{1}{n+%d}$" % (c, c + 1, c, c + 1),
            "$S_N=%s$" % tex(formula),
            r"$N\to\infty$ で $S_N\to %s$" % tex(val),
        ],
        "answer": m(val),
    }
    return f, val


def check_tel_c(p):
    term = 1 / (n * (n + 1) * (n + 2))
    formula = sp.Rational(1, 2) * (sp.Rational(1, 2) - 1 / ((N + 1) * (N + 2)))
    exact_partial_sums(term, formula, 1)
    return sp.summation(term, (n, 1, oo))


@kind("k_tel_c", check_tel_c, tuple_same)
def tel_c(p):
    val = sp.Rational(1, 4)
    f = {
        "title": "3つの積の望遠鏡和",
        "question": "級数 $%s \\dfrac{1}{n(n+1)(n+2)}$ の和を求めよ。途中式も書くこと。" % S(),
        "tool": "3つの積は「隣り合う2つの積」の差に分解できる。$\\dfrac{1}{n(n+1)}-\\dfrac{1}{(n+1)(n+2)}$ を計算すると分子が $2$ になることを使う。",
        "steps": [
            r"$\dfrac{1}{n(n+1)}-\dfrac{1}{(n+1)(n+2)}=\dfrac{2}{n(n+1)(n+2)}$",
            r"$\dfrac{1}{n(n+1)(n+2)}=\dfrac{1}{2}\left(\dfrac{1}{n(n+1)}-\dfrac{1}{(n+1)(n+2)}\right)$",
            r"$S_N=\dfrac{1}{2}\left(\dfrac{1}{2}-\dfrac{1}{(N+1)(N+2)}\right)$",
            r"$N\to\infty$ で $S_N\to\dfrac{1}{4}$",
        ],
        "answer": m(val),
    }
    return f, val


def check_log_div(p):
    prod = sp.simplify(sp.product((n + 1) / n, (n, 1, N)))
    if sp.simplify(prod - (N + 1)) != 0:
        raise AssertionError(prod)
    if sp.limit(sp.log(N + 1), N, oo) != oo:
        raise AssertionError("not divergent")
    return "発散"


@kind("k_log_div", check_log_div)
def log_div(p):
    f = {
        "title": "対数の望遠鏡和(発散)",
        "question": "級数 $%s \\log\\left(1+\\dfrac{1}{n}\\right)$ は収束するか。部分和 $S_N$ を求めて判定せよ。" % S(),
        "tool": "$\\log$ の中を $\\dfrac{n+1}{n}$ と通分すると $\\log(n+1)-\\log n$ という差になり、部分和が打ち消し合う。一般項 $\\to 0$ だけでは収束と言えない例である。",
        "steps": [
            r"$\log\left(1+\dfrac{1}{n}\right)=\log(n+1)-\log n$",
            r"$S_N=\log(N+1)-\log 1=\log(N+1)$",
            r"$N\to\infty$ で $\log(N+1)\to\infty$",
        ],
        "answer": "発散する($S_N=\\log(N+1)\\to\\infty$)",
    }
    return f, "発散"


def check_log_prod(p):
    prod = sp.simplify(sp.product(1 - 1 / n**2, (n, 2, N)))
    if sp.simplify(prod - (N + 1) / (2 * N)) != 0:
        raise AssertionError(prod)
    return sp.log(sp.limit(prod, N, oo))


@kind("k_log_prod", check_log_prod, tuple_same)
def log_prod(p):
    val = -sp.log(2)
    f = {
        "title": "対数の望遠鏡和(収束)",
        "question": "級数 $%s \\log\\left(1-\\dfrac{1}{n^2}\\right)$ の和を求めよ。途中式も書くこと。" % S("2"),
        "tool": "$1-\\dfrac{1}{n^2}=\\dfrac{(n-1)(n+1)}{n^2}$ と因数分解し、$\\log$ を差に分けると $\\log\\dfrac{n-1}{n}-\\log\\dfrac{n}{n+1}$ の形の望遠鏡和になる。",
        "steps": [
            r"$\log\left(1-\dfrac{1}{n^2}\right)=\log\dfrac{n-1}{n}-\log\dfrac{n}{n+1}$",
            r"$S_N=\displaystyle\sum_{n=2}^{N}\left(\log\dfrac{n-1}{n}-\log\dfrac{n}{n+1}\right)=\log\dfrac{1}{2}-\log\dfrac{N}{N+1}$",
            r"$N\to\infty$ で $\log\dfrac{N}{N+1}\to 0$ より $S_N\to-\log 2$",
        ],
        "answer": m(val),
    }
    return f, val


def check_fact_tel(p):
    term = n / sp.factorial(n + 1)
    exact_partial_sums(term, 1 - 1 / sp.factorial(N + 1), 1)
    return sp.summation(term, (n, 1, oo))


@kind("k_fact_tel", check_fact_tel, tuple_same)
def fact_tel(p):
    f = {
        "title": "階乗の望遠鏡和",
        "question": "級数 $%s \\dfrac{n}{(n+1)!}$ の和を求めよ。途中式も書くこと。" % S(),
        "tool": "分子を $n=(n+1)-1$ と書き換えると $\\dfrac{1}{n!}-\\dfrac{1}{(n+1)!}$ の差になり、部分分数分解と同じく望遠鏡和にできる。",
        "steps": [
            r"$\dfrac{n}{(n+1)!}=\dfrac{(n+1)-1}{(n+1)!}=\dfrac{1}{n!}-\dfrac{1}{(n+1)!}$",
            r"$S_N=\dfrac{1}{1!}-\dfrac{1}{(N+1)!}$",
            r"$N\to\infty$ で $S_N\to 1$",
        ],
        "answer": "$1$",
    }
    return f, sp.Integer(1)


# ============================================================ 収束判定
def verdict(conv):
    return "収束" if conv else "発散"


def check_by_classify(p):
    return verdict(st.classify_positive(parse(p["expr"])))


def _ratio_limit(expr):
    r = sp.simplify(sp.combsimp(expr.subs(n, n + 1) / expr))
    L = sp.limit(r, n, oo)
    # 数値でも確認(SymPy の極限を鵜呑みにしない)
    if abs(st.ratio_at(expr) - float(L)) > 1e-4:
        raise AssertionError(f"比の極限が数値と合わない: {expr}: {L}")
    return r, L


@kind("k_ratio", check_by_classify)
def ratio(p):
    expr = parse(p["expr"])
    r, L = _ratio_limit(expr)
    conv = L < 1
    f = {
        "title": p["title"],
        "question": "級数 $%s %s$ の収束・発散を判定せよ。途中式も書くこと。" % (S(), tex(expr)),
        "tool": p["tool"],
        "steps": [
            r"$a_n=%s$ とおくと $\dfrac{a_{n+1}}{a_n}=%s$" % (tex(expr), tex(r)),
            r"$n\to\infty$ で $\dfrac{a_{n+1}}{a_n}\to %s$" % tex(L),
            "$%s %s 1$ なのでダランベールの判定法より%sする" % (tex(L), "<" if conv else ">", verdict(conv)),
        ],
        "answer": verdict(conv) + "する",
    }
    return f, verdict(conv)


def check_ratio_e(p):
    out = []
    for a in p["as"]:
        out.append((a, verdict(st.classify_positive(a**n * sp.factorial(n) / n**n))))
    return tuple(out)


@kind("k_ratio_e", check_ratio_e)
def ratio_e(p):
    a_ = sp.Symbol("a", positive=True)
    expr = a_**n * sp.factorial(n) / n**n
    r = sp.simplify(sp.combsimp(expr.subs(n, n + 1) / expr))
    if sp.simplify(r - a_ * (n / (n + 1)) ** n) != 0:
        raise AssertionError("ratio_e: 比の式が合わない")
    L = sp.limit(a_ * (n / (n + 1)) ** n, n, oo)
    res = []
    for a in p["as"]:
        Lv = L.subs(a_, a)
        if abs(st.ratio_at(expr.subs(a_, a)) - float(Lv)) > 1e-4:
            raise AssertionError("ratio_e numeric mismatch")
        res.append((a, verdict(Lv < 1)))
    a1, a2 = p["as"]
    f = {
        "title": "比の極限に e が出る判定",
        "question": "級数 $%s \\dfrac{a^n\\, n!}{n^n}$ $(a>0)$ について、$a=%d$ のときと $a=%d$ のときそれぞれ収束・発散を判定せよ。" % (S(), a1, a2),
        "tool": "階乗と $n^n$ を含むので比をとる(ダランベール)。比の極限に $\\left(1+\\dfrac{1}{n}\\right)^n\\to e$ が現れ、$a$ と $e$ の大小で場合分けになる。",
        "steps": [
            r"$\dfrac{a_{n+1}}{a_n}=\dfrac{a^{n+1}(n+1)!}{(n+1)^{n+1}}\cdot\dfrac{n^n}{a^n\,n!}=\dfrac{a\,n^n}{(n+1)^n}=a\left(\dfrac{n}{n+1}\right)^n$",
            r"$\left(\dfrac{n}{n+1}\right)^n=\dfrac{1}{\left(1+\frac{1}{n}\right)^n}\to\dfrac{1}{e}$ より $\dfrac{a_{n+1}}{a_n}\to\dfrac{a}{e}$",
            r"$a=%d$: $\dfrac{%d}{e}%s1$ で%s / $a=%d$: $\dfrac{%d}{e}%s1$ で%s" % (
                a1, a1, "<" if res[0][1] == "収束" else ">", res[0][1],
                a2, a2, "<" if res[1][1] == "収束" else ">", res[1][1]),
        ],
        "answer": "$a=%d$ のとき%sし、$a=%d$ のとき%sする" % (a1, res[0][1], a2, res[1][1]),
    }
    return f, tuple(res)


@kind("k_root", check_by_classify)
def root(p):
    expr = parse(p["expr"])
    base = parse(p["base"])  # a_n^{1/n}
    if sp.simplify(base**n - expr) != 0 and sp.simplify(sp.powsimp(base**n, force=True) - expr) != 0:
        raise AssertionError("base mismatch")
    L = sp.limit(base, n, oo)
    if abs(st.root_at(expr, 10**6) - float(L)) > 1e-4:
        raise AssertionError(f"根の極限が数値と合わない: {expr}")
    conv = L < 1
    steps = [r"$\sqrt[n]{a_n}=%s$" % tex(base)]
    if p.get("extra"):
        steps.append(p["extra"])
    steps += [
        r"$n\to\infty$ で $\sqrt[n]{a_n}\to %s$" % tex(L),
        "$%s %s 1$ なのでコーシーの判定法(根判定法)より%sする" % (tex(L), "<" if conv else ">", verdict(conv)),
    ]
    f = {
        "title": p["title"],
        "question": "級数 $%s %s$ の収束・発散を判定せよ。途中式も書くこと。" % (S(), tex(expr)),
        "tool": p["tool"],
        "steps": steps,
        "answer": verdict(conv) + "する",
    }
    return f, verdict(conv)


@kind("k_comp", check_by_classify)
def comp(p):
    expr = parse(p["expr"])
    pp = R(p["p"])
    L = sp.limit(expr * n**pp, n, oo)
    if not (L.is_positive and L.is_finite):
        raise AssertionError("limit comparison failed")
    if abs(st.value_at(expr * n**pp, 10**9) - float(L)) > 1e-3 * float(L):
        raise AssertionError("limit numeric mismatch")
    conv = pp > 1
    steps = []
    if p.get("extra"):
        steps.append(p["extra"])
    steps += [
        r"$b_n=\dfrac{1}{%s}$ とすると $\dfrac{a_n}{b_n}=%s\cdot %s\to %s$ $(0<%s<\infty)$" % (
            tex(n**pp), ptex(expr), tex(n**pp), tex(L), tex(L)),
        r"$\displaystyle\sum\dfrac{1}{%s}$ は $p=%s%s1$ の $p$ 級数なので%sする" % (
            tex(n**pp), tex(pp), ">" if conv else r"\le ", verdict(conv)),
        "極限比較判定法より、もとの級数も%sする" % verdict(conv),
    ]
    f = {
        "title": p["title"],
        "question": "級数 $%s %s$ の収束・発散を判定せよ。途中式も書くこと。" % (S(), ptex(expr)),
        "tool": p["tool"],
        "steps": steps,
        "answer": verdict(conv) + "する",
    }
    return f, verdict(conv)


# ============================================================ 絶対収束・条件収束
def check_alt(p):
    return st.classify_alternating(parse(p["b"]))


@kind("k_alt", check_alt)
def alt(p):
    b = parse(p["b"])
    sign = "(-1)^{n-1}" if p.get("shift") else "(-1)^n"
    lim_b = sp.limit(b, n, oo)
    steps = []
    if lim_b != 0:
        res = "発散"
        steps = [
            r"$|a_n|=%s\to %s\neq 0$" % (tex(b), tex(lim_b)),
            "一般項 $a_n$ が $0$ に収束しない($n$ の偶奇で $\\pm %s$ に近づく)" % tex(lim_b),
            "収束の必要条件 $a_n\\to 0$ を満たさないので発散する",
        ]
    else:
        pp = R(p["p"])
        L = sp.limit(b * n**pp, n, oo)
        if pp != 0 and not (L.is_positive and L.is_finite):
            raise AssertionError("alt comparison failed")
        if pp > 1:
            res = "絶対収束"
            steps = [
                r"$|a_n|=%s$ で、$|a_n|\cdot %s\to %s$" % (tex(b), tex(n**pp), tex(L)),
                r"$\displaystyle\sum\dfrac{1}{%s}$ は $p=%s>1$ で収束するので、極限比較判定法より $\displaystyle\sum|a_n|$ は収束" % (tex(n**pp), tex(pp)),
                "よって絶対収束する(絶対収束する級数は収束する)",
            ]
        else:
            res = "条件収束"
            if pp == 0:
                cmp_step = p["abs_step"]
            else:
                cmp_step = r"$|a_n|=%s$ で $|a_n|\cdot %s\to %s$。$p=%s\le 1$ の $p$ 級数と比べて $\displaystyle\sum|a_n|$ は発散" % (
                    tex(b), tex(n**pp), tex(L), tex(pp))
            steps = [
                cmp_step,
                p["mono"] + r"、かつ $%s\to 0$" % tex(b),
                "ライプニッツの判定法より $\\displaystyle\\sum a_n$ は収束する",
                "収束するが絶対収束しないので条件収束",
            ]
    f = {
        "title": p["title"],
        "question": "級数 $%s %s%s$ は絶対収束・条件収束・発散のどれか。理由も書くこと。" % (
            S(), sign, tex(b) if b.is_Pow or b.is_Function else r"\, " + tex(b)),
        "tool": p["tool"],
        "steps": steps,
        "answer": res + ("する" if res != "発散" else "する"),
    }
    return f, res


ALT_P_SAMPLES = ["-1", "0", "1/3", "1/2", "1", "3/2", "2", "3"]


def alt_p_rule(pp):
    if pp > 1:
        return "絶対収束"
    if pp > 0:
        return "条件収束"
    return "発散"


def check_alt_param(p):
    out = []
    for s in ALT_P_SAMPLES:
        pp = sp.Rational(s)
        out.append((s, st.classify_alternating(1 / n**pp)))
    return tuple(out)


@kind("k_alt_param", check_alt_param)
def alt_param(p):
    vals = tuple((s, alt_p_rule(sp.Rational(s))) for s in ALT_P_SAMPLES)
    f = {
        "title": "交代 p 級数の場合分け",
        "question": "実数 $p$ に対して、級数 $%s \\dfrac{(-1)^{n}}{n^p}$ が絶対収束・条件収束・発散のどれになるかを $p$ の値で場合分けして答えよ。" % S(),
        "tool": "絶対値をとると $p$ 級数 $\\sum\\dfrac{1}{n^p}$ になる。$p\\le 1$ のときはライプニッツの判定法が使えるか(単調減少して $0$ に収束するか)を調べ、$p\\le 0$ では一般項が $0$ に収束しないことに注意する。",
        "steps": [
            r"$p>1$: $\displaystyle\sum\left|\dfrac{(-1)^n}{n^p}\right|=\sum\dfrac{1}{n^p}$ は収束 → 絶対収束",
            r"$0<p\le 1$: $\displaystyle\sum\dfrac{1}{n^p}$ は発散。一方 $\dfrac{1}{n^p}$ は単調減少して $0$ に収束するのでライプニッツの判定法より収束 → 条件収束",
            r"$p\le 0$: $\left|\dfrac{(-1)^n}{n^p}\right|=n^{-p}\ge 1$ で一般項が $0$ に収束しない → 発散",
        ],
        "answer": "$p>1$ で絶対収束、$0<p\\le 1$ で条件収束、$p\\le 0$ で発散",
    }
    return f, vals


# ============================================================ 収束半径
def _rad_core(p):
    c = parse(p["c"])
    k, j = p["k"], p.get("j", 0)
    r = sp.simplify(sp.combsimp(sp.Abs(c.subs(n, n + 1) / c)))
    rho = sp.limit(r, n, oo)
    Rt = oo if rho == 0 else (0 if rho == oo else 1 / rho)
    Rx = Rt if Rt in (0, oo) else sp.nsimplify(sp.root(Rt, k))
    return c, k, j, r, rho, Rt, sp.radsimp(Rx)


def check_radius(p):
    c = parse(p["c"])
    k = p["k"]
    rr = 1 / st.root_at(c, 10**6)  # 根判定(コーシー・アダマール)を数値で
    rq = 1 / st.ratio_at(c, 10**8)  # 比を数値で
    if abs(rr - rq) > 1e-3 * max(rr, rq):
        raise AssertionError(f"根と比で半径が食い違う {rr} {rq}")
    res = [rq ** (1.0 / k)]
    if p.get("endpoints"):
        Rt = sp.nsimplify(rq, tolerance=1e-6)
        t_term = sp.simplify(c * Rt**n)
        alternating = bool(sp.simplify(t_term.subs(n, 2) / t_term.subs(n, 3)) < 0)
        b = sp.simplify(sp.Abs(t_term))
        cls = st.classify_alternating(b) if alternating else ("絶対収束" if st.classify_positive(b) else "発散")
        res.append("発散" if cls == "発散" else "収束")
    return tuple(res)


def radius_same(a, b):
    if len(a) != len(b):
        return False
    if a[0] == oo or b[0] == oo:
        ok = a[0] == b[0]
    else:
        ok = abs(float(a[0]) - float(b[0])) < 1e-6 * max(1, float(a[0]))
    return ok and tuple(a[1:]) == tuple(b[1:])


def _series_tex(p):
    c = parse(p["c"])
    k, j = p["k"], p.get("j", 0)
    ctr = p.get("center", 0)
    u = "x" if ctr == 0 else "(x-%d)" % ctr
    pw = tex(k * n + j)
    lo = str(p.get("lo", 0))
    return r"%s %s\,%s^{%s}" % (S(lo), ptex(c), u, pw)


@kind("k_radius", check_radius, radius_same)
def radius(p):
    c, k, j, r, rho, Rt, Rx = _rad_core(p)
    if abs(st.ratio_at(c, 10**8) - float(rho)) > 1e-4:
        raise AssertionError("ratio numeric mismatch")
    ctr = p.get("center", 0)
    u = "x" if ctr == 0 else "(x-%d)" % ctr
    var = "x" if ctr == 0 else "x-%d" % ctr
    series = _series_tex(p)
    steps = []
    if k == 1:
        steps.append(r"$c_n=%s$ とおくと $\left|\dfrac{c_{n+1}}{c_n}\right|=%s$" % (tex(c), tex(r)))
        if p.get("extra"):
            steps.append(p["extra"])
        steps.append(r"$n\to\infty$ で $\to %s$" % tex(rho))
        steps.append(r"収束半径は極限の逆数なので $R=%s$" % tex(Rx))
    else:
        if j == 0:
            steps.append(r"$t=%s^{%d}$ とおくと $\displaystyle\sum %s\,t^n$($t$ の整級数)" % (u, k, ptex(c)))
        else:
            steps.append(r"$%s^{%s}=%s\cdot(%s^{%d})^n$ なので $t=%s^{%d}$ とおき $\displaystyle\sum %s\,t^n$ の収束半径を調べる" % (
                u, tex(k * n + j), u if j == 1 else "%s^{%d}" % (u, j), u, k, u, k, ptex(c)))
        if c.is_Add:
            Mx = max(c.args, key=lambda q: q.base)
            M = Mx.base
            num = sp.Add(*[q.base * sp.Pow(q.base / M, n, evaluate=False) if q.base != M else M for q in c.args], evaluate=False)
            den = sp.Add(*[sp.Pow(q.base / M, n, evaluate=False) if q.base != M else sp.Integer(1) for q in c.args], evaluate=False)
            if sp.simplify(sp.Abs(num / den) - r) != 0:
                raise AssertionError("radius sum display mismatch")
            rtex = r"\dfrac{%s}{%s}=\dfrac{%s}{%s}" % (
                tex(sp.Add(*[sp.Pow(q.base, n + 1, evaluate=False) for q in c.args], evaluate=False)), tex(c),
                tex(num), tex(den))
            steps.append(r"$\left|\dfrac{c_{n+1}}{c_n}\right|=%s$($%s^n$ で分母分子を割った)" % (rtex, tex(M)))
            steps.append(r"$\left(%s\right)^n\to 0$ より $\to %s$。$t$ についての収束半径は $%s$" % (
                tex(min(c.args, key=lambda q: q.base).base / M), tex(rho), tex(Rt)))
        elif r.has(n):
            steps.append(r"$\left|\dfrac{c_{n+1}}{c_n}\right|=%s\to %s$ より、$t$ についての収束半径は $%s$" % (
                tex(r), tex(rho), tex(Rt)))
        else:
            steps.append(r"$\left|\dfrac{c_{n+1}}{c_n}\right|=%s$(一定)より、$t$ についての収束半径は $%s$" % (
                tex(r), tex(Rt)))
        steps.append(r"$|t|<%s \iff |%s|^{%d}<%s \iff |%s|<%s$" % (tex(Rt), var, k, tex(Rt), var, tex(Rx)))
    val = [Rx]
    ans = "$R=%s$" % tex(Rx)
    if p.get("endpoints"):
        t_term = sp.simplify(c * Rt**n)
        alternating = bool(sp.simplify(t_term.subs(n, 2) / t_term.subs(n, 3)) < 0)
        b = sp.simplify(sp.Abs(t_term))
        pp = R(p["p_end"])
        if alternating:
            raise NotImplementedError
        conv = pp > 1 and sp.limit(b * n**pp, n, oo).is_finite
        if pp == 0:
            conv = False
        lo_, hi_ = ctr - Rx, ctr + Rx
        if pp == 0:
            why = r"$%s=\pm %s$ では $%s^{%s}=%s^n$ となり、級数は $%s %s$。一般項が $0$ に収束しないので発散" % (
                var, tex(Rx), u, tex(k * n), btex(Rt), S(str(p.get("lo", 0))), tex(t_term))
        else:
            why = r"$%s=\pm %s$ では $%s^{%s}=%s^n$ となり、級数は $%s %s$。$p=%s$ の $p$ 級数なので%s" % (
                var, tex(Rx), u, tex(k * n), btex(Rt), S(str(p.get("lo", 0))), tex(t_term), tex(pp),
                "収束" if conv else "発散")
        steps.append(why)
        if conv:
            ans += "、収束域は $%s\\le x\\le %s$" % (tex(lo_), tex(hi_))
        else:
            ans += "、収束域は $%s< x< %s$" % (tex(lo_), tex(hi_))
        val.append("収束" if conv else "発散")
    q = "整級数 $%s$ の収束半径を求めよ。" % series
    if p.get("endpoints"):
        q = "整級数 $%s$ の収束半径 $R$ を求め、さらに端点での収束・発散を調べて収束域(収束する $x$ の範囲)を答えよ。" % series
    f = {
        "title": p["title"],
        "question": q + "途中式も書くこと。",
        "tool": p["tool"],
        "steps": steps,
        "answer": ans,
    }
    return f, tuple(val)


# ============================================================ パラメータの場合分け
def _param_check(expr_fn, samples):
    return tuple((s, verdict(st.classify_positive(expr_fn(sp.Rational(s))))) for s in samples)


AN_SAMPLES = ["1/3", "1/2", "1", "3/2", "2"]


def check_param_an(p):
    return _param_check(lambda a: a**n / n, AN_SAMPLES)


@kind("k_param_an", check_param_an)
def param_an(p):
    vals = tuple((s, verdict(sp.Rational(s) < 1)) for s in AN_SAMPLES)
    f = {
        "title": "aⁿ/n の場合分け",
        "question": "$a>0$ とする。級数 $%s \\dfrac{a^n}{n}$ が収束するような $a$ の範囲を求めよ。" % S(),
        "tool": "比をとると極限が $a$ になるので $a<1$, $a>1$ はダランベールで決まる。比の極限が $1$ になる $a=1$ は判定法が使えないので、代入して直接調べる(場合分け)。",
        "steps": [
            r"$\dfrac{a_{n+1}}{a_n}=\dfrac{a^{n+1}}{n+1}\cdot\dfrac{n}{a^n}=\dfrac{an}{n+1}\to a$",
            r"$0<a<1$ なら収束、$a>1$ なら発散(ダランベール)",
            r"$a=1$ のとき $\displaystyle\sum\dfrac{1}{n}$(調和級数)で発散",
        ],
        "answer": "$0<a<1$",
    }
    return f, vals


NP_SAMPLES = ["0", "1", "3/2", "2", "5/2", "3"]


def check_param_np(p):
    return _param_check(lambda q: n**q / (n**3 + 1), NP_SAMPLES)


@kind("k_param_np", check_param_np)
def param_np(p):
    vals = tuple((s, verdict(sp.Rational(s) < 2)) for s in NP_SAMPLES)
    f = {
        "title": "p 級数との比較で場合分け",
        "question": "実数 $p$ に対して、級数 $%s \\dfrac{n^p}{n^3+1}$ が収束するための $p$ の条件を求めよ。" % S(),
        "tool": "一般項は $n$ が大きいとき $\\dfrac{n^p}{n^3}=\\dfrac{1}{n^{3-p}}$ のようにふるまうので、$p$ 級数との極限比較で $3-p>1$ かどうかに帰着させる。",
        "steps": [
            r"$b_n=\dfrac{1}{n^{3-p}}$ とすると $\dfrac{a_n}{b_n}=\dfrac{n^3}{n^3+1}\to 1$",
            r"極限比較判定法より $\displaystyle\sum a_n$ と $\displaystyle\sum\dfrac{1}{n^{3-p}}$ は収束・発散が一致",
            r"$p$ 級数は $3-p>1$ のとき収束、$3-p\le 1$ のとき発散",
        ],
        "answer": "$p<2$",
    }
    return f, vals


A2N_SAMPLES = ["1/3", "1/2", "1", "2", "3"]


def check_param_a2n(p):
    return _param_check(lambda a: a**n / (1 + a ** (2 * n)), A2N_SAMPLES)


@kind("k_param_a2n", check_param_a2n)
def param_a2n(p):
    vals = tuple((s, verdict(sp.Rational(s) != 1)) for s in A2N_SAMPLES)
    f = {
        "title": "a の大小で3通りに場合分け",
        "question": "$a>0$ とする。級数 $%s \\dfrac{a^n}{1+a^{2n}}$ の収束・発散を $a$ の値で場合分けして判定せよ。" % S(),
        "tool": "$a<1$ と $a>1$ で分母の主要項が $1$ と $a^{2n}$ に入れ替わるので場合分けし、それぞれ等比級数と比較する。$a=1$ は直接代入する。",
        "steps": [
            r"$0<a<1$: $0<\dfrac{a^n}{1+a^{2n}}\le a^n$、$\displaystyle\sum a^n$ は公比 $a<1$ の等比級数で収束 → 収束",
            r"$a>1$: $\dfrac{a^n}{1+a^{2n}}\le\dfrac{a^n}{a^{2n}}=\left(\dfrac{1}{a}\right)^n$、公比 $\dfrac{1}{a}<1$ で収束 → 収束",
            r"$a=1$: 一般項 $=\dfrac{1}{2}\not\to 0$ → 発散",
        ],
        "answer": "$a\\neq 1$ のとき収束、$a=1$ のとき発散",
    }
    return f, vals


# ============================================================ 出題リスト
def specs(rng):
    """(kind, level, params) のリスト。rng は数値の選択にだけ使う。"""
    L = []
    add = lambda kind_, lv, **p: L.append((kind_, lv, p))

    # --- 望遠鏡和 (7)
    add("k_tel_a", 1, a=rng.choice([2, 3]))
    add("k_tel_b", 1, **rng.choice([{"k": 2, "b": -1}, {"k": 3, "b": -2}]))
    add("k_tel_quad", 2, c=rng.choice([2, 3]))
    add("k_tel_c", 2)
    add("k_log_div", 2)
    add("k_log_prod", 3)
    add("k_fact_tel", 3)

    # --- 収束判定 (9)
    kk, aa = rng.choice([2, 3]), rng.choice([2, 3])
    add("k_ratio", 1, expr="n**%d/%d**n" % (kk, aa), title="比判定法(多項式÷指数)",
        tool="$n^%d$ と $%d^n$ の比較なので比をとると多項式部分は $1$ に近づき、指数部分の比 $\\dfrac{1}{%d}$ だけが残る(ダランベールの判定法)。" % (kk, aa, aa))
    add("k_ratio", 2, expr="factorial(n)**2/factorial(2*n)", title="比判定法(階乗)",
        tool="階乗を含む一般項は比をとると約分で多項式の比になる(ダランベールの判定法)。$(2n+2)!=(2n+2)(2n+1)(2n)!$ に注意する。")
    cc = rng.choice([5, 6])
    add("k_ratio", 2, expr="%d**n*factorial(n)**2/factorial(2*n)" % cc, title="比判定法(階乗と指数)",
        tool="階乗と指数の積なので比をとる(ダランベール)。比の極限が $1$ より大きいか小さいかで判定する。")
    add("k_ratio_e", 3, **{"as": [2, 3]})
    a1, c1 = rng.choice([(2, 3), (3, 4), (3, 5)])
    add("k_root", 1, expr="((%d*n+1)/(%d*n+2))**n" % (a1, c1), base="(%d*n+1)/(%d*n+2)" % (a1, c1),
        title="根判定法(n 乗の形)", tool="一般項が丸ごと $n$ 乗なので $n$ 乗根をとると括弧の中だけが残る(コーシーの根判定法)。")
    a2 = rng.choice([1, 2])
    add("k_root", 2, expr="(n/(n+%d))**(n**2)" % a2, base="(n/(n+%d))**n" % a2,
        title="根判定法と e の極限",
        tool="指数が $n^2$ なので $n$ 乗根をとると $\\left(\\dfrac{n}{n+%d}\\right)^n$ が残る。これは $\\left(1+\\dfrac{%d}{n}\\right)^{-n}$ と見て $e$ の極限を使う。" % (a2, a2),
        extra=r"$\left(\dfrac{n}{n+%d}\right)^n=\dfrac{1}{\left(1+\frac{%d}{n}\right)^n}$" % (a2, a2))
    b1, b2 = rng.choice([(1, 2), (2, 1), (3, 1)])
    add("k_comp", 1, expr="(n+%d)/(n**3+%d)" % (b1, b2), p="2", title="p 級数との極限比較",
        tool="分子は1次、分母は3次なので一般項は $\\dfrac{1}{n^2}$ と同じオーダー。$p$ 級数 $\\sum\\dfrac{1}{n^2}$ と極限比較する。")
    b3 = rng.choice([2, 3])
    add("k_comp", 2, expr="1/sqrt(n**2+%d*n)" % b3, p="1", title="極限比較で発散",
        tool="根号の中は2次式なので一般項は $\\dfrac{1}{n}$ と同じオーダー。調和級数($p=1$)と極限比較する。")
    b4 = rng.choice([2, 3])
    add("k_comp", 2, expr="sqrt(n)/(n**2+%d)" % b4, p="3/2", title="分数乗の p 級数と比較",
        tool="分子が $n^{1/2}$、分母が $n^2$ なので一般項は $\\dfrac{1}{n^{3/2}}$ のオーダー。$p=\\dfrac{3}{2}$ の $p$ 級数と極限比較する。")
    b5 = rng.choice([2, 3])
    add("k_comp", 3, expr="1-cos(%d/n)" % b5, p="2", title="テイラー展開と極限比較",
        tool="$n\\to\\infty$ で $\\dfrac{%d}{n}\\to 0$ なので $1-\\cos\\theta\\approx\\dfrac{\\theta^2}{2}$ を使うと一般項は $\\dfrac{1}{n^2}$ のオーダーとわかる。これと極限比較する。" % b5,
        extra=r"$1-\cos\theta=\dfrac{\theta^2}{2}+O(\theta^4)$ に $\theta=\dfrac{%d}{n}$ を代入すると $1-\cos\dfrac{%d}{n}\approx\dfrac{%d}{n^2}$" % (b5, b5, b5 * b5 // 2) if b5 % 2 == 0 else
        r"$1-\cos\theta=\dfrac{\theta^2}{2}+O(\theta^4)$ に $\theta=\dfrac{%d}{n}$ を代入すると $1-\cos\dfrac{%d}{n}\approx\dfrac{%d}{2n^2}$" % (b5, b5, b5 * b5))

    # --- 絶対収束・条件収束 (6)
    add("k_alt", 1, b="1/n**(1/3)", p="1/3", shift=True, title="交代 p 級数",
        tool="絶対値をとると $p=\\dfrac{1}{3}$ の $p$ 級数。絶対収束しないときはライプニッツの判定法で収束を確かめる。",
        mono=r"$\sqrt[3]{n}$ は単調増加なので $\dfrac{1}{\sqrt[3]{n}}$ は単調減少")
    e2 = rng.choice([1, 2])
    add("k_alt", 1, b="n/(n**3+%d)" % e2, p="2", title="絶対収束の判定",
        tool="まず絶対値の級数を調べる。分子1次・分母3次で $\\dfrac{1}{n^2}$ のオーダーなので $p$ 級数と比較できる。", mono="")
    e3 = rng.choice([2, 3])
    n0 = int(sp.floor(sp.sqrt(e3))) + 1
    add("k_alt", 2, b="n/(n**2+%d)" % e3, p="1", title="条件収束の判定",
        tool="絶対値は $\\dfrac{1}{n}$ のオーダーで発散するので絶対収束しない。そこでライプニッツの判定法($|a_n|$ が単調減少して $0$ に収束)を確かめる。",
        mono=r"$g(x)=\dfrac{x}{x^2+%d}$ は $g'(x)=\dfrac{%d-x^2}{(x^2+%d)^2}<0$ $(x>\sqrt{%d})$ なので $n\ge %d$ で単調減少" % (e3, e3, e3, e3, n0))
    e4 = rng.choice([2, 3])
    add("k_alt", 2, b="n/(%d*n+1)" % e4, title="一般項が 0 に行かない交代級数",
        tool="交代級数でもまず一般項 $\\to 0$ を確認する。$0$ に収束しなければその時点で発散と決まる(ライプニッツは使えない)。")
    add("k_alt", 2, b="1/log(n+1)", p="0", title="対数を含む条件収束",
        tool="$\\log(n+1)<n+1$ を使うと絶対値の級数は調和級数より大きく発散する。一方 $\\dfrac{1}{\\log(n+1)}$ は単調減少して $0$ に収束するのでライプニッツが使える。",
        abs_step=r"$\log(n+1)<n+1$ より $|a_n|=\dfrac{1}{\log(n+1)}>\dfrac{1}{n+1}$。$\displaystyle\sum\dfrac{1}{n+1}$ は発散するので比較判定法より $\displaystyle\sum|a_n|$ は発散",
        mono=r"$\log(n+1)$ は単調増加なので $\dfrac{1}{\log(n+1)}$ は単調減少")
    add("k_alt_param", 3)

    # --- 収束半径 (12): x^{2n}, x^{2n+1} 型を 9 題
    t2 = "$x^{2n}$ の係数しかなく奇数次の係数が $0$ なので、係数の比の公式はそのまま使えない。$t=x^2$ と置いて $t$ の整級数の収束半径を求めてから $x$ に戻す(または項どうしの比をとる)。"
    a = rng.choice([2, 3, 5])
    add("k_radius", 1, c="%d**n" % a, k=2, title="x²ⁿ 型の収束半径", tool=t2)
    a = rng.choice([5, 7])
    add("k_radius", 1, c="1/%d**n" % a, k=2, title="x²ⁿ 型の収束半径(割る形)", tool=t2)
    a = rng.choice([4, 9])
    add("k_radius", 1, c="%d**n" % a, k=2, j=1, title="x²ⁿ⁺¹ 型の収束半径",
        tool="偶数次の係数が $0$ なので係数の比の公式はそのまま使えない。$x^{2n+1}=x\\cdot(x^2)^n$ と分けて $t=x^2$ と置く(または項どうしの比をとる)。")
    a = rng.choice([3, 5])
    add("k_radius", 2, c="n/%d**n" % a, k=2, title="n がかかった x²ⁿ 型", tool=t2)
    a = rng.choice([2, 3])
    add("k_radius", 2, c="(-1)**n*%d**n/(n+1)" % a, k=2, j=1, title="符号つき x²ⁿ⁺¹ 型",
        tool="係数の符号 $(-1)^n$ は比の絶対値をとれば消える。$x^{2n+1}=x(x^2)^n$ として $t=x^2$ の整級数の収束半径を求める(偶数次の係数が $0$ なので公式を直接は使えない)。")
    a = rng.choice([8, 27])
    add("k_radius", 2, c="%d**n" % a, k=3, title="x³ⁿ 型の収束半径",
        tool="$x^{3n}$ の項しかないので $t=x^3$ と置く。$|t|<R_t\\iff|x|<\\sqrt[3]{R_t}$ で戻す。")
    a = rng.choice([3, 5])
    add("k_radius", 3, c="%d**n/n" % a, k=2, lo=1, endpoints=True, p_end="1", title="x²ⁿ 型の収束域(端点で発散)",
        tool="$t=x^2$ と置いて収束半径を出し、端点 $x=\\pm R$ では $x^{2n}=R^{2n}$ を代入した級数を $p$ 級数として別に調べる(比判定法は端点では使えない)。")
    a = rng.choice([4, 9])
    add("k_radius", 3, c="%d**n/n**2" % a, k=2, lo=1, endpoints=True, p_end="2", title="x²ⁿ 型の収束域(端点で収束)",
        tool="$t=x^2$ と置いて収束半径を出し、端点では代入した級数を $p$ 級数として調べる。$p=2>1$ なら端点も含む。")
    a, b = rng.choice([(2, 3), (2, 5), (3, 4)])
    add("k_radius", 3, c="%d**n+%d**n" % (a, b), k=2, title="係数が和の x²ⁿ 型",
        tool="係数 $%d^n+%d^n$ は $n$ が大きいと大きい方の $%d^n$ が支配する。$t=x^2$ と置き、比の極限を $%d^n$ でくくって求める。" % (a, b, max(a, b), max(a, b)))
    a, ctr = rng.choice([(4, 1), (9, 2)])
    add("k_radius", 3, c="1/%d**n" % a, k=2, center=ctr, endpoints=True, p_end="0", title="中心がずれた (x−c)²ⁿ 型",
        tool="$u=x-%d$, $t=u^2$ と2回置き換える。端点では各項が $1$ になり一般項が $0$ に収束しないことを使う。" % ctr)
    a = rng.choice([2, 3])
    add("k_radius", 1, c="n**2/%d**n" % a, k=1, title="基本の収束半径",
        tool="すべての次数の係数がそろっているので、係数の比 $\\left|\\dfrac{c_{n+1}}{c_n}\\right|$ の極限の逆数が収束半径になる。")
    add("k_radius", 3, c="factorial(n)/n**n", k=1, lo=1,
        extra=r"$\left(\dfrac{n}{n+1}\right)^n=\dfrac{1}{\left(1+\frac{1}{n}\right)^n}\to\dfrac{1}{e}$", title="係数の比に e が出る収束半径",
        tool="係数に階乗と $n^n$ があるので比をとる。比の極限に $\\left(1+\\dfrac{1}{n}\\right)^n\\to e$ が出てくることがポイント。")

    # --- パラメータの場合分け (3)
    add("k_param_an", 3)
    add("k_param_np", 3)
    add("k_param_a2n", 3)
    return L
