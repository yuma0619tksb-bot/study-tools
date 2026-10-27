"""物理学概論第二: エントロピー・理想気体の内部エネルギー・カルノーサイクル・等温/断熱変化。

R=8.31 J/(mol·K), 0℃=273.15 K。答えは有効数字3桁。
render は公式(浮動小数)で計算し、check は数値積分・常微分方程式・
サイクルの模擬計算など別の道筋で同じ量を求め直す。
"""
import math

import mpmath

from .core import kind, num_close, sig3

SUBJECT = "物理学概論第二"
PREFIX = "p"

RGAS = 8.31
T0 = 273.15


def K(tc):
    return tc + T0


def s3(v, unit=""):
    return sig3(v, unit)


def s4(v, unit=""):
    return sig3(v, unit, k=4)


def _paren(sv):
    return "(%s)" % sv if sv.startswith("-") else sv


def phys_same(a, b):
    return len(a) == len(b) and all(num_close(p, q, rel=1e-7) for p, q in zip(a, b))


def deg(f):
    return "単原子分子($f=3$)" if f == 3 else "2原子分子($f=5$)"


def tex_num(v):
    """問題文に出す入力値(10^n 表記を許す)。"""
    if isinstance(v, str):
        return v
    if abs(v) >= 1e4:
        e = int(math.floor(math.log10(abs(v))))
        mant = v / 10**e
        ms = ("%g" % mant)
        return r"%s\times 10^{%d}" % (ms, e)
    return "%g" % v


# ============================================================ エントロピー
def check_latent(p):
    m, L, T = p["m"], p["L"], K(p["tc"])
    sgn = -1 if p["dir"] in ("freeze", "condense") else 1
    # 一定温度での可逆な熱のやりとり: dS = dQ/T を Q について積分
    S = mpmath.quad(lambda q: 1 / mpmath.mpf(T), [0, m * L])
    return (float(sgn * S),)


@kind("p_latent", check_latent, phys_same)
def latent(p):
    m, L, tc = p["m"], p["L"], p["tc"]
    T = K(tc)
    sgn = -1 if p["dir"] in ("freeze", "condense") else 1
    Q = m * L
    dS = sgn * Q / T
    word = {"melt": "融解", "freeze": "凝固", "boil": "沸騰(蒸発)", "condense": "凝縮"}[p["dir"]]
    what = {"melt": ("氷", "水"), "freeze": ("水", "氷"), "boil": ("水", "水蒸気"), "condense": ("水蒸気", "水")}[p["dir"]]
    Lname = "融解熱" if p["dir"] in ("melt", "freeze") else "蒸発熱"
    steps = [
        r"$T=%g+273.15=%s\ \mathrm{K}$" % (tc, "%.2f" % T),
        r"%s熱 $Q=mL=%g\times %s=%s\ \mathrm{J}$" % ("吸収する" if sgn > 0 else "放出する", m, tex_num(L), s4(Q)),
        r"$\Delta S=%s\dfrac{Q}{T}=%s\dfrac{%s}{%.2f}=%s$" % ("" if sgn > 0 else "-", "" if sgn > 0 else "-", s4(Q), T, s3(dS, "J/K")),
    ]
    f = {
        "title": "%sのエントロピー変化" % word,
        "question": "$%g\\ \\mathrm{%s}$ の%s($%g$℃)がすべて%s($%g$℃)になった。このときの%sのエントロピー変化 $\\Delta S$ を有効数字3桁で求めよ。%s $L=%s\\ \\mathrm{J/kg}$ とする。" % (
            p["show_m"], p["show_unit"], what[0], tc, what[1], tc, what[0], Lname, tex_num(L)),
        "tool": "相転移の間は温度が一定なので $\\Delta S=\\dfrac{Q}{T}$ がそのまま使える。温度は必ず絶対温度 [K] に直す。%s" % (
            "熱を放出する変化なので $\\Delta S<0$ になる。" if sgn < 0 else ""),
        "steps": steps,
        "answer": "$\\Delta S=%s$" % s3(dS, "J/K"),
    }
    return f, (dS,)


def check_heat(p):
    m, c = p["m"], p["c"]
    T1, T2 = K(p["t1"]), K(p["t2"])
    return (float(mpmath.quad(lambda T: m * c / T, [T1, T2])),)


@kind("p_heat", check_heat, phys_same)
def heat(p):
    m, c, t1, t2 = p["m"], p["c"], p["t1"], p["t2"]
    T1, T2 = K(t1), K(t2)
    dS = m * c * math.log(T2 / T1)
    word = "温めた" if t2 > t1 else "冷やした"
    f = {
        "title": "加熱のエントロピー変化" if t2 > t1 else "冷却のエントロピー変化",
        "question": "質量 $%g\\ \\mathrm{kg}$ の水を $%g$℃ から $%g$℃ までゆっくり%s。水のエントロピー変化を有効数字3桁で求めよ。水の比熱 $c=%s\\ \\mathrm{J/(kg\\cdot K)}$ とする。" % (
            m, t1, t2, word, tex_num(c)),
        "tool": "温度が変わるので $\\Delta S=Q/T$ は使えない。$dS=\\dfrac{dQ}{T}=\\dfrac{mc\\,dT}{T}$ を積分して $\\Delta S=mc\\log\\dfrac{T_2}{T_1}$ を使う。",
        "steps": [
            r"$T_1=%.2f\ \mathrm{K},\ T_2=%.2f\ \mathrm{K}$" % (T1, T2),
            r"$\Delta S=\displaystyle\int_{T_1}^{T_2}\dfrac{mc}{T}\,dT=mc\log\dfrac{T_2}{T_1}$",
            r"$=%g\times %s\times\log\dfrac{%.2f}{%.2f}=%s\times %s$" % (m, tex_num(c), T2, T1, s4(m * c), _paren(s4(math.log(T2 / T1)))),
            r"$\Delta S=%s$" % s3(dS, "J/K"),
        ],
        "answer": "$\\Delta S=%s$" % s3(dS, "J/K"),
    }
    return f, (dS,)


def check_ice_water(p):
    m, ci, cw, L = p["m"], p["ci"], p["cw"], p["L"]
    a = mpmath.quad(lambda T: m * ci / T, [K(p["t1"]), T0])
    b = m * L / T0
    c = mpmath.quad(lambda T: m * cw / T, [T0, K(p["t2"])])
    return (float(a), float(b), float(c), float(a + b + c))


@kind("p_ice_water", check_ice_water, phys_same)
def ice_water(p):
    m, ci, cw, L, t1, t2 = p["m"], p["ci"], p["cw"], p["L"], p["t1"], p["t2"]
    T1, T2 = K(t1), K(t2)
    s1 = m * ci * math.log(T0 / T1)
    s2 = m * L / T0
    s3_ = m * cw * math.log(T2 / T0)
    tot = s1 + s2 + s3_
    f = {
        "title": "氷から水への全エントロピー変化",
        "question": "$%g$℃ の氷 $%g\\ \\mathrm{kg}$ をゆっくり加熱して $%g$℃ の水にした。エントロピー変化の合計を有効数字3桁で求めよ。氷の比熱 $%s$、水の比熱 $%s\\ \\mathrm{J/(kg\\cdot K)}$、融解熱 $%s\\ \\mathrm{J/kg}$ とする。" % (
            t1, m, t2, tex_num(ci), tex_num(cw), tex_num(L)),
        "tool": "「氷の温度上昇」「0℃での融解」「水の温度上昇」の3段階に分ける。温度が変わる段階は $mc\\log\\dfrac{T_2}{T_1}$、融解は $\\dfrac{mL}{T}$ を使い、最後に足す(2つの公式の組み合わせ)。",
        "steps": [
            r"氷の加熱: $\Delta S_1=%g\times %s\times\log\dfrac{273.15}{%.2f}=%s\ \mathrm{J/K}$" % (m, tex_num(ci), T1, s4(s1)),
            r"融解: $\Delta S_2=\dfrac{%g\times %s}{273.15}=%s\ \mathrm{J/K}$" % (m, tex_num(L), s4(s2)),
            r"水の加熱: $\Delta S_3=%g\times %s\times\log\dfrac{%.2f}{273.15}=%s\ \mathrm{J/K}$" % (m, tex_num(cw), T2, s4(s3_)),
            r"$\Delta S=\Delta S_1+\Delta S_2+\Delta S_3=%s$" % s3(tot, "J/K"),
        ],
        "answer": "$\\Delta S=%s$" % s3(tot, "J/K"),
    }
    return f, (s1, s2, s3_, tot)


def check_mix(p):
    m1, t1, m2, t2, c = p["m1"], p["t1"], p["m2"], p["t2"], p["c"]
    T1, T2 = K(t1), K(t2)
    Tf = mpmath.findroot(lambda T: m1 * c * (T - T1) + m2 * c * (T - T2), (T1 + T2) / 2)
    a = mpmath.quad(lambda T: m1 * c / T, [T1, Tf])
    b = mpmath.quad(lambda T: m2 * c / T, [T2, Tf])
    return (float(Tf), float(a), float(b), float(a + b))


@kind("p_mix", check_mix, phys_same)
def mix(p):
    m1, t1, m2, t2, c = p["m1"], p["t1"], p["m2"], p["t2"], p["c"]
    T1, T2 = K(t1), K(t2)
    Tf = (m1 * T1 + m2 * T2) / (m1 + m2)
    a = m1 * c * math.log(Tf / T1)
    b = m2 * c * math.log(Tf / T2)
    f = {
        "title": "水の混合によるエントロピー増加",
        "question": "$%g$℃ の水 $%g\\ \\mathrm{kg}$ と $%g$℃ の水 $%g\\ \\mathrm{kg}$ を断熱容器の中で混ぜた。全体のエントロピー変化を有効数字3桁で求めよ。水の比熱 $%s\\ \\mathrm{J/(kg\\cdot K)}$ とする。" % (
            t1, m1, t2, m2, tex_num(c)),
        "tool": "まず熱量の保存(高温側が失う熱 = 低温側が得る熱)で最終温度を求める。そのあと高温側・低温側それぞれ $mc\\log\\dfrac{T_f}{T}$ を計算して足す(熱量保存とエントロピーの組み合わせ)。",
        "steps": [
            r"熱量保存 $m_1c(T_f-T_1)+m_2c(T_f-T_2)=0$ より $T_f=\dfrac{m_1T_1+m_2T_2}{m_1+m_2}=%s\ \mathrm{K}$" % ("%.2f" % Tf),
            r"高温の水: $\Delta S_1=%g\times %s\times\log\dfrac{%.2f}{%.2f}=%s\ \mathrm{J/K}$" % (m1, tex_num(c), Tf, T1, s4(a)),
            r"低温の水: $\Delta S_2=%g\times %s\times\log\dfrac{%.2f}{%.2f}=%s\ \mathrm{J/K}$" % (m2, tex_num(c), Tf, T2, s4(b)),
            r"$\Delta S=\Delta S_1+\Delta S_2=%s>0$(不可逆変化なので増加)" % s3(a + b, "J/K"),
        ],
        "answer": "$\\Delta S=%s$" % s3(a + b, "J/K"),
    }
    return f, (Tf, a, b, a + b)


# ============================================================ 内部エネルギー
def check_U(p):
    n, f_, T = p["n"], p["f"], p["T"]
    # 自由度1つあたり (1/2) nRT のエネルギー等分配を足し上げる
    U = sum(0.5 * n * RGAS * T for _ in range(f_))
    return (U,)


@kind("p_U", check_U, phys_same)
def U_(p):
    n, f_, T = p["n"], p["f"], p["T"]
    U = f_ / 2 * n * RGAS * T
    f = {
        "title": "理想気体の内部エネルギー",
        "question": "%sの理想気体 $%g\\ \\mathrm{mol}$ が温度 $%g\\ \\mathrm{K}$ にある。内部エネルギー $U$ を有効数字3桁で求めよ。$R=8.31\\ \\mathrm{J/(mol\\cdot K)}$ とする。" % (deg(f_), n, T),
        "tool": "エネルギー等分配則より、自由度1つあたり $\\dfrac{1}{2}RT$ (1 mol あたり)。理想気体の内部エネルギーは $U=\\dfrac{f}{2}nRT$。",
        "steps": [
            r"$U=\dfrac{f}{2}nRT$ で $f=%d$" % f_,
            r"$U=\dfrac{%d}{2}\times %g\times 8.31\times %g=%s$" % (f_, n, T, s3(U, "J")),
        ],
        "answer": "$U=%s$" % s3(U, "J"),
    }
    return f, (U,)


def check_isochoric(p):
    n, f_, dT = p["n"], p["f"], p["dT"]
    Cv = f_ / 2 * RGAS
    return (float(mpmath.quad(lambda T: n * Cv, [300, 300 + dT])),)


@kind("p_isochoric", check_isochoric, phys_same)
def isochoric(p):
    n, f_, dT = p["n"], p["f"], p["dT"]
    Q = f_ / 2 * n * RGAS * dT
    f = {
        "title": "定積変化で必要な熱",
        "question": "%sの理想気体 $%g\\ \\mathrm{mol}$ を体積一定のまま温度を $%g\\ \\mathrm{K}$ 上げた。気体が吸収した熱量 $Q$ を有効数字3桁で求めよ。$R=8.31\\ \\mathrm{J/(mol\\cdot K)}$ とする。" % (deg(f_), n, dT),
        "tool": "体積一定なので気体は仕事をしない($W=0$)。熱力学第1法則 $Q=\\Delta U+W$ より $Q=\\Delta U=\\dfrac{f}{2}nR\\Delta T$。",
        "steps": [
            r"定積なので $W=0$、$Q=\Delta U$",
            r"$\Delta U=\dfrac{%d}{2}nR\Delta T=\dfrac{%d}{2}\times %g\times 8.31\times %g$" % (f_, f_, n, dT),
            r"$Q=%s$" % s3(Q, "J"),
        ],
        "answer": "$Q=%s$" % s3(Q, "J"),
    }
    return f, (Q,)


def check_isobaric(p):
    n, f_, T1, dT = p["n"], p["f"], p["T1"], p["dT"]
    P = 1.0e5  # 圧力の値によらないことを利用して、具体的な体積で計算する
    V1, V2 = n * RGAS * T1 / P, n * RGAS * (T1 + dT) / P
    W = float(mpmath.quad(lambda V: P, [V1, V2]))
    dU = f_ / 2 * n * RGAS * dT
    Q = n * (f_ / 2 + 1) * RGAS * dT  # C_p = C_v + R
    return (dU, W, Q)


@kind("p_isobaric", check_isobaric, phys_same)
def isobaric(p):
    n, f_, T1, dT = p["n"], p["f"], p["T1"], p["dT"]
    dU = f_ / 2 * n * RGAS * dT
    W = n * RGAS * dT
    Q = dU + W
    f = {
        "title": "定圧変化と第1法則",
        "question": "%sの理想気体 $%g\\ \\mathrm{mol}$ を圧力一定のまま $%g\\ \\mathrm{K}$ から $%g\\ \\mathrm{K}$ まで加熱した。内部エネルギーの変化 $\\Delta U$、気体がした仕事 $W$、吸収した熱量 $Q$ をそれぞれ有効数字3桁で求めよ。$R=8.31\\ \\mathrm{J/(mol\\cdot K)}$ とする。" % (
            deg(f_), n, T1, T1 + dT),
        "tool": "$\\Delta U=\\dfrac{f}{2}nR\\Delta T$ は過程によらない。定圧では $W=p\\Delta V=nR\\Delta T$(状態方程式)。最後に第1法則 $Q=\\Delta U+W$ でまとめる(3つの関係の組み合わせ)。",
        "steps": [
            r"$\Delta T=%g\ \mathrm{K}$" % dT,
            r"$\Delta U=\dfrac{%d}{2}\times %g\times 8.31\times %g=%s\ \mathrm{J}$" % (f_, n, dT, s4(dU)),
            r"$W=p\Delta V=nR\Delta T=%g\times 8.31\times %g=%s\ \mathrm{J}$" % (n, dT, s4(W)),
            r"$Q=\Delta U+W=%s\ \mathrm{J}$" % s4(Q),
        ],
        "answer": "$\\Delta U=%s$, $W=%s$, $Q=%s$" % (s3(dU, "J"), s3(W, "J"), s3(Q, "J")),
    }
    return f, (dU, W, Q)


# ============================================================ カルノーサイクル
def carnot_sim(TH, TC, QH=None, f_=5, n=1.0, V1=1.0e-3, ratio=2.0):
    """理想気体のカルノーサイクルを4つの過程に分けて計算する(検算用)。"""
    g = (f_ + 2) / f_
    V2 = V1 * ratio
    V3 = V2 * (TH / TC) ** (1 / (g - 1))
    V4 = V1 * (TH / TC) ** (1 / (g - 1))
    qh = float(mpmath.quad(lambda V: n * RGAS * TH / V, [V1, V2]))  # 等温膨張で吸収
    qc = float(mpmath.quad(lambda V: n * RGAS * TC / V, [V4, V3]))  # 等温圧縮で放出
    scale = 1.0 if QH is None else QH / qh
    return qh * scale, qc * scale


def check_carnot(p):
    TH, TC = p["TH"] + (T0 if p["unit"] == "C" else 0), p["TC"] + (T0 if p["unit"] == "C" else 0)
    mode = p["mode"]
    if mode == "eff":
        qh, qc = carnot_sim(TH, TC)
        return (1 - qc / qh,)
    if mode == "QH":
        qh, qc = carnot_sim(TH, TC, QH=p["Q"])
        return (1 - qc / qh, qh - qc, qc)
    if mode == "W":
        qh1, qc1 = carnot_sim(TH, TC)
        scale = p["Q"] / (qh1 - qc1)
        return (1 - qc1 / qh1, qh1 * scale, qc1 * scale)
    raise ValueError(mode)


@kind("p_carnot", check_carnot, phys_same)
def carnot(p):
    off = T0 if p["unit"] == "C" else 0
    TH, TC = p["TH"] + off, p["TC"] + off
    eta = 1 - TC / TH
    temps = "高温熱源 $%g$℃、低温熱源 $%g$℃" % (p["TH"], p["TC"]) if off else "高温熱源 $%g\\ \\mathrm{K}$、低温熱源 $%g\\ \\mathrm{K}$" % (p["TH"], p["TC"])
    steps = []
    if off:
        steps.append(r"$T_H=%.2f\ \mathrm{K},\ T_C=%.2f\ \mathrm{K}$" % (TH, TC))
    steps.append(r"$\eta=1-\dfrac{T_C}{T_H}=1-\dfrac{%g}{%g}=%s$" % (TC, TH, s4(eta)))
    mode = p["mode"]
    if mode == "eff":
        q = "%sの間で動くカルノー機関の効率 $\\eta$ を有効数字3桁で求めよ。" % temps
        ans = "$\\eta=%s$($%s\\,\\%%$)" % (s3(eta), s3(eta * 100))
        val = (eta,)
        tool = "カルノー機関の効率は熱源の絶対温度だけで決まり $\\eta=1-\\dfrac{T_C}{T_H}$。"
        title = "カルノー機関の効率"
    elif mode == "QH":
        QH = p["Q"]
        W = eta * QH
        QC = QH - W
        q = "%sの間で動くカルノー機関が、1サイクルで高温熱源から $%s\\ \\mathrm{J}$ の熱を吸収する。1サイクルでする仕事 $W$ と低温熱源に捨てる熱 $Q_C$ を有効数字3桁で求めよ。" % (temps, tex_num(QH))
        steps += [r"$W=\eta Q_H=%s\times %s=%s\ \mathrm{J}$" % (s4(eta), tex_num(QH), s4(W)),
                  r"$Q_C=Q_H-W=%s\ \mathrm{J}$" % s4(QC)]
        ans = "$W=%s$, $Q_C=%s$" % (s3(W, "J"), s3(QC, "J"))
        val = (eta, W, QC)
        tool = "まず温度から効率 $\\eta=1-\\dfrac{T_C}{T_H}$ を求め、$W=\\eta Q_H$。エネルギー保存 $Q_H=W+Q_C$ から $Q_C$ を出す。"
        title = "カルノー機関の仕事と排熱"
    else:
        W = p["Q"]
        QH = W / eta
        QC = QH - W
        q = "%sの間で動くカルノー機関に、1サイクルあたり $%s\\ \\mathrm{J}$ の仕事をさせたい。高温熱源から吸収する熱 $Q_H$ と低温熱源に捨てる熱 $Q_C$ を有効数字3桁で求めよ。" % (temps, tex_num(W))
        steps += [r"$Q_H=\dfrac{W}{\eta}=\dfrac{%s}{%s}=%s\ \mathrm{J}$" % (tex_num(W), s4(eta), s4(QH)),
                  r"$Q_C=Q_H-W=%s\ \mathrm{J}$" % s4(QC)]
        ans = "$Q_H=%s$, $Q_C=%s$" % (s3(QH, "J"), s3(QC, "J"))
        val = (eta, QH, QC)
        tool = "効率の定義 $\\eta=\\dfrac{W}{Q_H}$ を逆に使って $Q_H=\\dfrac{W}{\\eta}$。$Q_C$ はエネルギー保存から。"
        title = "仕事から吸収熱を逆算"
    f = {"title": title, "question": q, "tool": tool, "steps": steps, "answer": ans}
    return f, val


def check_carnot_raise(p):
    TC = p["TC"] + T0
    out = []
    for eta in (p["eta1"], p["eta2"]):
        # 模擬サイクルの効率が目標になる T_H を数値的に解く
        TH = mpmath.findroot(lambda T: (lambda q: 1 - q[1] / q[0])(carnot_sim(float(T), TC)) - eta, TC * 1.5, tol=1e-18)
        out.append(float(TH))
    return (out[0], out[1], out[1] - out[0])


@kind("p_carnot_raise", check_carnot_raise, lambda a, b: all(num_close(p, q, rel=1e-6) for p, q in zip(a, b)))
def carnot_raise(p):
    TC = p["TC"] + T0
    e1, e2 = p["eta1"], p["eta2"]
    TH1, TH2 = TC / (1 - e1), TC / (1 - e2)
    f = {
        "title": "効率を上げるための高温熱源の温度",
        "question": "低温熱源の温度が $%g$℃ のカルノー機関がある。効率を $%g\\,\\%%$ から $%g\\,\\%%$ に上げるには、高温熱源の温度を何 K 上げればよいか。有効数字3桁で答えよ。" % (
            p["TC"], e1 * 100, e2 * 100),
        "tool": "$\\eta=1-\\dfrac{T_C}{T_H}$ を $T_H$ について解くと $T_H=\\dfrac{T_C}{1-\\eta}$。2つの効率それぞれで $T_H$ を出して差をとる(式変形と場合の比較)。",
        "steps": [
            r"$T_C=%.2f\ \mathrm{K}$、$T_H=\dfrac{T_C}{1-\eta}$" % TC,
            r"$\eta=%g$: $T_H=\dfrac{%.2f}{%g}=%s\ \mathrm{K}$" % (e1, TC, 1 - e1, s4(TH1)),
            r"$\eta=%g$: $T_H=\dfrac{%.2f}{%g}=%s\ \mathrm{K}$" % (e2, TC, 1 - e2, s4(TH2)),
            r"差 $%s\ \mathrm{K}$" % s4(TH2 - TH1),
        ],
        "answer": "$%s$ 上げればよい" % s3(TH2 - TH1, "K"),
    }
    return f, (TH1, TH2, TH2 - TH1)


# ============================================================ 等温変化
def check_iso(p):
    n, T, r = p["n"], p["T"], p["ratio"]
    V1 = 1.0e-2
    W = float(mpmath.quad(lambda V: n * RGAS * T / V, [V1, V1 * r]))
    return (W, W, W / T)


@kind("p_iso", check_iso, phys_same)
def iso(p):
    n, T, r = p["n"], p["T"], p["ratio"]
    W = n * RGAS * T * math.log(r)
    Q = W
    dS = Q / T
    if p["ask"] == "work":
        q = "理想気体 $%g\\ \\mathrm{mol}$ を温度 $%g\\ \\mathrm{K}$ に保ったまま、体積を $%g$ 倍にゆっくり膨張させた。気体がした仕事 $W$ と吸収した熱 $Q$ を有効数字3桁で求めよ。$R=8.31\\ \\mathrm{J/(mol\\cdot K)}$ とする。" % (n, T, r)
        ans = "$W=%s$, $Q=%s$" % (s3(W, "J"), s3(Q, "J"))
        title = "等温膨張の仕事と熱"
        steps = [
            r"$W=\displaystyle\int_{V_1}^{V_2}p\,dV=\int_{V_1}^{V_2}\dfrac{nRT}{V}dV=nRT\log\dfrac{V_2}{V_1}$",
            r"$W=%g\times 8.31\times %g\times\log %g=%s\ \mathrm{J}$" % (n, T, r, s4(W)),
            r"等温なので $\Delta U=0$、第1法則より $Q=W$",
        ]
        tool = "等温変化では $p=\\dfrac{nRT}{V}$ を積分して仕事を出す。理想気体の内部エネルギーは温度だけで決まるので $\\Delta U=0$、よって $Q=W$。"
    else:
        p1, p2 = p["p1"], p["p2"]
        q = "理想気体 $%g\\ \\mathrm{mol}$ を温度 $%g\\ \\mathrm{K}$ に保ったまま、圧力 $%s\\ \\mathrm{Pa}$ から $%s\\ \\mathrm{Pa}$ までゆっくり圧縮した。気体が吸収した熱 $Q$ とエントロピー変化 $\\Delta S$ を有効数字3桁で求めよ。$R=8.31\\ \\mathrm{J/(mol\\cdot K)}$ とする。" % (
            n, T, tex_num(p1), tex_num(p2))
        ans = "$Q=%s$, $\\Delta S=%s$" % (s3(Q, "J"), s3(dS, "J/K"))
        title = "等温圧縮の熱とエントロピー"
        steps = [
            r"等温なので $pV=$ 一定、$\dfrac{V_2}{V_1}=\dfrac{p_1}{p_2}=%g$" % r,
            r"$Q=W=nRT\log\dfrac{V_2}{V_1}=%g\times 8.31\times %g\times\log %g=%s\ \mathrm{J}$" % (n, T, r, s4(Q)),
            r"$\Delta S=\dfrac{Q}{T}=nR\log\dfrac{V_2}{V_1}=%s\ \mathrm{J/K}$" % s4(dS),
        ]
        tool = "等温ではボイルの法則 $p_1V_1=p_2V_2$ で体積比に直し、$Q=W=nRT\\log\\dfrac{V_2}{V_1}$。温度一定なので $\\Delta S=\\dfrac{Q}{T}$ が使える。圧縮では $Q<0$, $\\Delta S<0$。"
    f = {"title": title, "question": q, "tool": tool, "steps": steps, "answer": ans}
    return f, (W, Q, dS)


# ============================================================ 断熱変化
def check_adia(p):
    """第1法則 C_v dT = -p dV = -(nRT/V) dV を常微分方程式として数値的に解く(検算用)。

    u = |log(V/V1)| を独立変数にとる(V = V1 e^{σu}, σ=±1)と
    dT/du = -σ (R/C_v) T となり、圧縮でも u が増える向きに解ける。
    """
    f_, n, T1, r = p["f"], p["n"], p["T1"], p["ratio"]
    Cv = f_ / 2 * RGAS
    sigma = 1 if r > 1 else -1
    sol = mpmath.odefun(lambda u, T: -sigma * (RGAS / Cv) * T, 0, mpmath.mpf(T1))
    uend = abs(mpmath.log(r))
    T2 = sol(uend)
    if p["ask"] == "T":
        return (float(T2),)
    if p["ask"] == "p":
        pr = (T2 / r) / T1  # p = nRT/V の比
        return (float(p["p1"] * pr),)
    # 気体がされた仕事 W = -∫p dV = -σ nR ∫ T du
    Won = -sigma * n * RGAS * mpmath.quad(sol, [0, uend])
    return (float(T2), float(Won))


@kind("p_adia", check_adia, lambda a, b: all(num_close(p, q, rel=1e-6) for p, q in zip(a, b)))
def adia(p):
    f_, n, T1, r = p["f"], p["n"], p["T1"], p["ratio"]
    g = (f_ + 2) / f_
    gtex = "\\dfrac{5}{3}" if f_ == 3 else "\\dfrac{7}{5}"
    T2 = T1 * (1 / r) ** (g - 1)
    pr = (1 / r) ** g
    Won = f_ / 2 * n * RGAS * (T2 - T1)
    ask = p["ask"]
    vol = "体積が $%g$ 倍になるまで膨張させた" % r if r > 1 else "体積が $\\dfrac{1}{%g}$ になるまで圧縮した" % (1 / r)
    base = "%sの理想気体 $%g\\ \\mathrm{mol}$(温度 $%g\\ \\mathrm{K}$)を断熱的にゆっくり%s。" % (deg(f_), n, T1, vol)
    steps = [r"$\gamma=\dfrac{f+2}{f}=%s$" % gtex]
    if ask == "T":
        q = base + "変化後の温度 $T_2$ を有効数字3桁で求めよ。"
        steps += [r"$TV^{\gamma-1}=$ 一定より $T_2=T_1\left(\dfrac{V_1}{V_2}\right)^{\gamma-1}$",
                  r"$T_2=%g\times\left(%s\right)^{%s}=%s\ \mathrm{K}$" % (T1, _ratio_tex(1 / r), "2/3" if f_ == 3 else "2/5", s4(T2))]
        ans = "$T_2=%s$" % s3(T2, "K")
        val = (T2,)
        tool = "断熱準静的変化ではポアソンの式 $TV^{\\gamma-1}=$ 一定 が成り立つ。比熱比は $\\gamma=\\dfrac{f+2}{f}$。"
        title = "断熱変化後の温度"
    elif ask == "p":
        P1 = p["p1"]
        q = base.replace("(温度 $%g\\ \\mathrm{K}$)" % T1, "(圧力 $%s\\ \\mathrm{Pa}$)" % tex_num(P1)) + "変化後の圧力 $p_2$ を有効数字3桁で求めよ。"
        steps += [r"$pV^{\gamma}=$ 一定より $p_2=p_1\left(\dfrac{V_1}{V_2}\right)^{\gamma}$",
                  r"$p_2=%s\times %s^{%s}=%s\ \mathrm{Pa}$" % (tex_num(P1), _ratio_tex(1 / r), "5/3" if f_ == 3 else "7/5", s4(P1 * pr))]
        ans = "$p_2=%s$" % s3(P1 * pr, "Pa")
        val = (P1 * pr,)
        tool = "断熱準静的変化ではポアソンの式 $pV^{\\gamma}=$ 一定。2原子分子なので $\\gamma=\\dfrac{7}{5}$。" if f_ == 5 else "断熱準静的変化ではポアソンの式 $pV^{\\gamma}=$ 一定。単原子分子なので $\\gamma=\\dfrac{5}{3}$。"
        title = "断熱圧縮後の圧力"
    else:
        q = base + "変化後の温度 $T_2$ と、この間に気体がされた仕事 $W$ を有効数字3桁で求めよ。$R=8.31\\ \\mathrm{J/(mol\\cdot K)}$ とする。"
        steps += [r"$T_2=T_1\left(\dfrac{V_1}{V_2}\right)^{\gamma-1}=%g\times %s^{%s}=%s\ \mathrm{K}$" % (T1, _ratio_tex(1 / r), "2/3" if f_ == 3 else "2/5", s4(T2)),
                  r"断熱なので $Q=0$、第1法則より $W=\Delta U=\dfrac{%d}{2}nR(T_2-T_1)$" % f_,
                  r"$W=\dfrac{%d}{2}\times %g\times 8.31\times(%s-%g)=%s\ \mathrm{J}$" % (f_, n, s4(T2), T1, s4(Won))]
        ans = "$T_2=%s$, $W=%s$" % (s3(T2, "K"), s3(Won, "J"))
        val = (T2, Won)
        tool = "ポアソンの式 $TV^{\\gamma-1}=$ 一定 で温度を出し、断熱 $Q=0$ なので第1法則から「された仕事 $=\\Delta U$」として求める(2つの関係の組み合わせ)。"
        title = "断熱圧縮の温度と仕事"
    f = {"title": title, "question": q, "tool": tool, "steps": steps, "answer": ans}
    return f, val


def _ratio_tex(v):
    if v >= 1:
        return "%g" % v
    return "\\dfrac{1}{%g}" % (1 / v)


# ============================================================ 出題リスト
def specs(rng):
    L = []
    add = lambda kind_, lv, **p: L.append((kind_, lv, p))
    LF, LV, CW, CI = 3.34e5, 2.26e6, 4.19e3, 2.1e3

    # --- エントロピー (8)
    m = rng.choice([0.5, 0.25, 2.0, 1.5, 0.8])
    add("p_latent", 1, m=m, L=LF, tc=0, dir="melt", show_m=m, show_unit="kg")
    g = rng.choice([200, 300, 150, 400])
    add("p_latent", 1, m=g / 1000, L=LF, tc=0, dir="melt", show_m=g, show_unit="g")
    m = rng.choice([1.0, 0.5, 0.2, 2.0])
    add("p_latent", 1, m=m, L=LV, tc=100, dir="boil", show_m=m, show_unit="kg")
    m = rng.choice([0.3, 0.4, 0.6, 1.2])
    add("p_latent", 2, m=m, L=LF, tc=0, dir="freeze", show_m=m, show_unit="kg")
    t1, t2 = rng.choice([(20, 80), (10, 60), (25, 75), (15, 45), (30, 90)])
    add("p_heat", 1, m=1.0, c=CW, t1=t1, t2=t2)
    t1, t2 = rng.choice([(90, 30), (80, 20), (70, 10), (95, 25)])
    add("p_heat", 2, m=0.5, c=CW, t1=t1, t2=t2)
    m, t1, t2 = rng.choice([(0.2, -10, 20), (0.5, -20, 10), (0.1, -5, 30), (0.3, -15, 25)])
    add("p_ice_water", 3, m=m, ci=CI, cw=CW, L=LF, t1=t1, t2=t2)
    m1, t1, m2, t2 = rng.choice([(1.0, 80, 1.0, 20), (2.0, 90, 1.0, 30), (0.5, 70, 1.5, 10), (1.0, 60, 3.0, 20)])
    add("p_mix", 3, m1=m1, t1=t1, m2=m2, t2=t2, c=CW)

    # --- 内部エネルギー (3)
    n, T = rng.choice([(2, 300), (3, 400), (1, 250), (4, 350)])
    add("p_U", 1, n=n, f=3, T=T)
    n, dT = rng.choice([(2, 50), (1, 100), (3, 40), (2, 80)])
    add("p_isochoric", 2, n=n, f=5, dT=dT)
    n, T1, dT = rng.choice([(2, 300, 100), (1, 250, 50), (3, 300, 60), (2, 400, 100)])
    add("p_isobaric", 3, n=n, f=3, T1=T1, dT=dT)

    # --- カルノー (5)
    TH, TC = rng.choice([(500, 300), (600, 300), (800, 400), (700, 350), (900, 300)])
    add("p_carnot", 1, TH=TH, TC=TC, unit="K", mode="eff")
    TH, TC = rng.choice([(227, 27), (327, 27), (127, 27), (527, 127)])
    add("p_carnot", 1, TH=TH, TC=TC, unit="C", mode="eff")
    TH, TC, Q = rng.choice([(400, 20, 1.0e4), (300, 27, 5.0e3), (500, 100, 2.0e4)])
    add("p_carnot", 2, TH=TH, TC=TC, unit="C", mode="QH", Q=Q)
    TH, TC, Q = rng.choice([(500, 300, 2.0e3), (600, 400, 1.0e3), (800, 300, 5.0e3)])
    add("p_carnot", 2, TH=TH, TC=TC, unit="K", mode="W", Q=Q)
    TC, e1, e2 = rng.choice([(27, 0.25, 0.40), (17, 0.20, 0.50), (7, 0.30, 0.40)])
    add("p_carnot_raise", 3, TC=TC, eta1=e1, eta2=e2)

    # --- 等温・断熱 (6)
    n, T, r = rng.choice([(1, 300, 2), (2, 300, 3), (1, 400, 4), (3, 350, 2)])
    add("p_iso", 1, n=n, T=T, ratio=r, ask="work")
    n, T, p1, p2 = rng.choice([(1, 300, 1.0e5, 4.0e5), (2, 350, 1.0e5, 2.0e5), (1, 400, 2.0e5, 5.0e5)])
    add("p_iso", 2, n=n, T=T, ratio=p1 / p2, ask="entropy", p1=p1, p2=p2)
    f_, T1, r = rng.choice([(3, 300, 2.0), (3, 400, 8.0), (5, 300, 2.0), (3, 500, 4.0)])
    add("p_adia", 2, f=f_, n=1, T1=T1, ratio=r, ask="T")
    f_, r = rng.choice([(5, 0.5), (3, 0.5), (5, 0.25)])
    add("p_adia", 2, f=f_, n=1, T1=300, ratio=r, ask="p", p1=1.0e5)
    f_, T1, r = rng.choice([(5, 300, 0.1), (3, 300, 0.125), (5, 280, 0.2)])
    add("p_adia", 3, f=f_, n=1, T1=T1, ratio=r, ask="TW")
    return L
