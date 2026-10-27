"""級数の判定を「解答とは別ルート」で行う検算用ツール(数値計算 + SymPy)。

SymPy の Sum.is_convergent や階乗を含む極限は誤答することがある
(例: (n!/n^n)^(1/n) の極限を 0 と返す)ので、ここでは
  * 比 a_{n+1}/a_n を大きな n で高精度に数値評価する
  * 1/n の冪との比(p 級数との比較)を数値評価する
という素朴な方法で判定し、解答側の SymPy 計算と突き合わせる。
"""
import mpmath
import sympy as sp

from .core import n

mpmath.mp.dps = 60


def _f(expr):
    return sp.lambdify(n, expr, "mpmath")


def ratio_at(expr, big=10**7):
    f = _f(expr)
    a, b = mpmath.mpf(big), mpmath.mpf(big + 1)
    return float(abs(f(b) / f(a)))


def root_at(expr, big=10**7):
    f = _f(expr)
    v = abs(f(mpmath.mpf(big)))
    return float(mpmath.e ** (mpmath.log(v) / big))


def power_exponent(expr, big=10**12):
    """b(n) ~ C n^{-p} とみたときの p(数値)。log b(2M)/b(M) / log 2 で推定。"""
    f = _f(expr)
    M = mpmath.mpf(big)
    return float(-mpmath.log(abs(f(2 * M) / f(M))) / mpmath.log(2))


def value_at(expr, big=10**12):
    return float(_f(expr)(mpmath.mpf(big)))


def eventually_decreasing(expr, start=50, stop=10**6):
    f = _f(expr)
    pts = [start]
    while pts[-1] < stop:
        pts.append(pts[-1] * 3)
    vals = [f(mpmath.mpf(k)) for k in pts]
    vals2 = [f(mpmath.mpf(k + 1)) for k in pts]
    return all(b < a for a, b in zip(vals, vals2))


def classify_positive(b):
    """正項級数 Σ b(n) の収束(True)/発散(False)を数値的に判定。"""
    r = ratio_at(b)
    if r < 1 - 1e-4:
        return True
    if r > 1 + 1e-4:
        return False
    # 比が 1 → 多項式オーダー。p 級数と比べる
    p = power_exponent(b)
    if p < 0.95:
        return False  # n^{-0.95} より遅く減る → Σ1/n^{0.95} と比較して発散
    if p > 1.05:
        return True
    if abs(p - 1) > 1e-3:
        raise AssertionError(f"指数が判定できない: {b} ~ n^-{p}")
    return False  # b ~ C/n(調和級数と比較)


def classify_alternating(b):
    """Σ (-1)^n b(n)(b>0)を '絶対収束' / '条件収束' / '発散' に分類。"""
    r = ratio_at(b)
    if r > 1 + 1e-4:
        return "発散"
    lim = sp.limit(b, n, sp.oo)
    shrinking = value_at(b, 10**12) < 0.9 * value_at(b, 10**6)
    if (lim == 0) != shrinking:
        raise AssertionError(f"一般項の極限の判定が食い違う: {b}")
    if lim != 0:
        return "発散"  # 一般項が 0 に収束しない
    if classify_positive(b):
        return "絶対収束"
    if not eventually_decreasing(b):
        raise AssertionError(f"単調減少が確認できない: {b}")
    return "条件収束"
