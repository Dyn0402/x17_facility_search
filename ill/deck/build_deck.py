"""Build the ILL X17 feasibility slide deck from the sim outputs.

Writes the Slides-artifact files to deck/build/project/ (deck.json + one
section per slide) and a standalone slidedoc page (tooltips, contents, Details)
to out/feasibility_deck.html (for dylan-neff.web.cern.ch/notes).  Inputs:
sim/analysis_v3/ (spectra, xtra_artifact.json from sim/lxplus/xtra_artifact.py,
acc_sources_G1.json from sim/lxplus/acc_sources.py) and out/cell_depth.csv.

    python ill/deck/build_deck.py
"""
import json, math, os, sys
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, os.path.expanduser(os.environ.get(
    "SLIDEDOC_DIR", "~/PycharmProjects/dylan-cern-site/scripts")))
import slidedoc as sd
from slidedoc import term, tipattr

HERE = Path(__file__).resolve().parent
ILL = HERE.parent
OUT = HERE / "build" / "project"
SL = OUT / "slides"
SL.mkdir(parents=True, exist_ok=True)
X = json.load(open(ILL / "sim/analysis_v3/xtra_artifact.json"))
depth = pd.read_csv(ILL / "out/cell_depth.csv")
spT = pd.read_csv(ILL / "sim/analysis_v3/v3_timing/spectrum_G1.csv")
spB = pd.read_csv(ILL / "sim/analysis_v3/v3_base/spectrum_G1.csv")
BINS = np.arange(40.0, 181.0, 4.0)
CEN = 0.5 * (BINS[1:] + BINS[:-1])

# ---- palette / type -------------------------------------------------------
BG, BG2, CARD = "#f5f3ee", "#ebe8e1", "#fffdf9"
INK, MUT, RULE = "#1c2230", "#5a6170", "#d8d3c8"
DARK, DINK, DMUT = "#151a24", "#eef0f3", "#a3abb9"
BLUE, ORANGE = "#1f5fa8", "#c8601a"
C = dict(x17=BLUE, ipc="#7d8796", g="#7a52b8", acc="#c99318", cos="#c63d4f")
SANS = "'IBM Plex Sans', Helvetica, Arial, sans-serif"
MONO = SANS   # Plex Mono lacks superscript digits
SVGF = "Helvetica, Arial, sans-serif"

SEC = {}     # id -> (body, notes, dark, foot), for the slidedoc page

def sec(id_, body, notes, dark=False, foot=None):
    SEC[id_] = (body, notes, dark, foot)
    bg, fg = (DARK, DINK) if dark else (BG, INK)
    pad = "112px 128px 160px" if foot else "112px 128px 128px"
    f = (f'<p style="position:absolute;left:128px;bottom:64px;width:1664px;font-size:24px;color:{DMUT if dark else MUT}">{foot}</p>'
         if foot else "")
    return (f'<section id="{id_}" data-transition="fade" style="background:{bg};color:{fg};font-family:{SANS};'
            f'padding:{pad};display:flex;flex-direction:column;gap:32px">\n{body}\n{f}\n<aside>{notes}</aside>\n</section>\n')

def title(t, sub=None):
    s = f'<h2 style="font-size:60px;font-weight:600;line-height:1.1;letter-spacing:-1px">{t}</h2>'
    if sub:
        s += f'\n<p style="font-size:30px;color:{MUT};line-height:1.3">{sub}</p>'
    return f'<div style="display:flex;flex-direction:column;gap:12px">{s}</div>'

def sci(v, d=1):
    if v == 0:
        return "0"
    e = int(math.floor(math.log10(abs(v))))
    m = v / 10 ** e
    if round(m, d) >= 10:
        m /= 10; e += 1
    sup = str(e).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))
    return f"{m:.{d}f}×10{sup}"

def card(inner, w=None, bg=CARD, pad=32):
    ws = f"width:{w}px;" if w else "flex:1;"
    return (f'<div style="{ws}display:flex;flex-direction:column;gap:12px;background:{bg};padding:{pad}px;'
            f'border:1px solid {RULE};border-radius:16px">{inner}</div>')

def svg(w, h, inner, label):
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" aria-label="{label}">{inner}</svg>'

def T(x, y, s, size=22, fill=MUT, anchor="middle", weight=400, rot=None):
    r = f' transform="rotate({rot} {x} {y})"' if rot is not None else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{SVGF}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}"{r}>{s}</text>')

def axes(x0, y0, w, h, xt, yt, xl, yl, xmap, ymap, grid=True):
    """xt/yt: list of (value, label)."""
    o = []
    for v, lab in yt:
        y = ymap(v)
        if grid:
            o.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0+w}" y2="{y:.1f}" stroke="{RULE}" stroke-width="1"/>')
        o.append(T(x0 - 10, y + 7, lab, 21, anchor="end"))
    for v, lab in xt:
        x = xmap(v)
        o.append(f'<line x1="{x:.1f}" y1="{y0+h}" x2="{x:.1f}" y2="{y0+h+8}" stroke="{MUT}" stroke-width="1.5"/>')
        o.append(T(x, y0 + h + 32, lab, 21))
    o.append(f'<line x1="{x0}" y1="{y0+h}" x2="{x0+w}" y2="{y0+h}" stroke="{MUT}" stroke-width="1.5"/>')
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+h}" stroke="{MUT}" stroke-width="1.5"/>')
    if xl:
        o.append(T(x0 + w / 2, y0 + h + 66, xl, 22, fill=INK))
    if yl:
        o.append(T(x0 - 72, y0 + h / 2, yl, 22, fill=INK, rot=-90))
    return "".join(o)

def poly(xs, ys, col, sw=3.5, dash=None, fill=None):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    d = f' stroke-dasharray="{dash}"' if dash else ""
    if fill:
        return f'<polygon points="{pts}" fill="{fill}" stroke="none"/>'
    return f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"{d}/>'

def step_xy(edges, vals):
    xs, ys = [], []
    for i, v in enumerate(vals):
        xs += [edges[i], edges[i + 1]]; ys += [v, v]
    return xs, ys

def legend_row(items, size=24):
    s = "".join(f'<div style="display:flex;align-items:center;gap:10px"><div style="width:28px;height:8px;background:{c};border-radius:4px"></div>'
                f'<p style="font-size:{size}px;color:{INK}">{n}</p></div>' for n, c in items)
    return f'<div style="display:flex;flex-wrap:wrap;gap:28px;align-items:center">{s}</div>'

slides = {}

# ---- recurring terms (tooltips) --------------------------------------------
T_G1 = term("G1", "Cell G1: 1 bar ³He, radius 40 mm, 12 µm mylar skin, 0.5 mm Be window, 8 mm Al upstream end cap.")
T_SIPM2 = term("sipm2", "Trigger menu: ≥ 0.5 MIP (0.24 MeV) in the SiPM bars of both lepton arms, plus a Micromegas gap hit in each.")
T_ESUM = term("Esum > 13 MeV", "Scintillator energy (SiPM bars + plastic + LS) summed over the two lepton arms. "
              "13 MeV is 3.5σ above the hardest single-capture line (¹⁴N, 10.83 MeV).")
T_2TAU = term("2τ", "Coincidence window for two unrelated singles. Baseline 5 ns; 1.2 ns with 200 ps per arm.")
T_IPC = term("IPC", "Internal pair creation in ³He(n,γ)⁴He, M1 + E0 multipoles (Born level). The continuum under the X17.")

# =========================================================================== 1 cover
R_BASE, R_GOOD, R_FLOOR = 5.2e-2, 8.4e-3, 4.4e-3
TIP_BASE = ("3σ reach 5.2×10⁻², G1, sipm2, Esum > 13 MeV, best rate 1.9×10¹⁰ n/s (beam max).\n"
            "Per cycle: 1.15×10⁶ cosmics, 87 000 accidentals, 14 600 IPC.")
TIP_GOOD = ("3σ reach 8.4×10⁻³ at 0.9×10¹⁰ n/s: σt 0.2 ns per arm, |Δt| < 0.6 ns, 2τ = 1.2 ns, "
            "muon veto inefficiency 10⁻².\nPer cycle: 9 700 IPC, 5 100 accidentals, 360 cosmics.")
TIP_FLOOR = "Fisher σ(μ) with only IPC M1 + E0 in the fit: the 50-day statistics floor (∝ 1/√cycles)."
def bignum(v, lab, col, note, tip=None):
    return (f'<div{tipattr(tip)} style="flex:1;display:flex;flex-direction:column;gap:12px;border-top:4px solid {col};padding:28px 0 0 0">'
            f'<p style="font-family:{MONO};font-size:72px;font-weight:600;color:{col}">{v}</p>'
            f'<p style="font-size:30px;color:{DINK};line-height:1.3">{lab}</p>'
            f'<p style="font-size:24px;color:{DMUT};line-height:1.35">{note}</p></div>')
body = f'''<p style="font-size:26px;letter-spacing:3px;text-transform:uppercase;color:{DMUT}">ILL PF1B · Geant4 campaign G1–G6 · 2 Oct 2026</p>
<h1 style="font-size:88px;font-weight:600;line-height:1.08;letter-spacing:-2px;width:1500px">X17 at the ILL is feasible, but only with 200 ps timing and a cosmic veto</h1>
<div style="flex:1"></div>
<p style="font-size:28px;color:{DMUT}">3σ reach in X17 / IPC(M1), one 50-day cycle. The reference ratio is 2.5×10⁻².</p>
<div style="display:flex;gap:64px">
{bignum("5.2×10⁻²", "Today's design", "#e07a86", "σt 0.5 ns, no veto. Cosmics dominate; the reference ratio would be ~1.5σ.", TIP_BASE)}
{bignum("8.4×10⁻³", "200 ps + μ veto 10⁻²", "#6aa6e8", "Same cell (G1), ~10¹⁰ n/s. The reference ratio becomes a 6–9σ effect.", TIP_GOOD)}
{bignum("4.4×10⁻³", "Pure IPC statistics", "#b9c1cc", "The floor if every non-IPC background vanished.", TIP_FLOOR)}
</div>
<p style="font-size:28px;color:#6aa6e8;line-height:1.35;border-left:4px solid #6aa6e8;padding-left:20px"><b>Update 7 Oct:</b> with ≤ 3° Micromegas segments, n_TOF's ~5 ns hardware with no panel and a CFRP end cap reaches 1.2×10⁻². 200 ps and the panel become optional (n_TOF hardware slide).</p>'''
slides["cover"] = sec("cover", body, "Bottom line of the overnight campaign (FEASIBILITY_SIM.md). The limit is cosmic rays, not neutron backgrounds, lepton scattering or raw statistics. G1 = 1 bar, R 40 mm, 12 µm mylar cell; Esum > 13 MeV, sipm2 trigger menu.", dark=True)

# =========================================================================== reach, explained
A_PAIR = 0.2014 / 55.0          # IPC M1 pairs per ³He(n,γ) photon (Born, 20.58 MeV): 3.66e-3
NG_PER_N = 55e-6 / 5333.0       # ³He(n,γ) per absorbed neutron
_d = pd.read_csv(ILL / "sim/analysis_v3/cons/ringCFRP_3_30_np.csv")
DES = _d[(_d.hw == "nTOF 5 ns, no veto, strict") & (~_d.endcap_off)].iloc[0]
R_DES = float(DES.reach3)
n_x = DES.X17 * R_DES
bk = [("X17 at the reach", n_x, BLUE), ("IPC pairs (M1 + E0)", DES.M1 + DES.E0, C["ipc"]),
      ("Accidental pairs", DES.ACC, C["acc"]), ("Cosmic μ", DES.COS, C["cos"])]
mx = max(v for _, v, _ in bk)
bars = "".join(f'''<div style="display:flex;align-items:center;gap:16px;height:52px">
<p style="width:280px;flex-shrink:0;font-size:25px;text-align:right">{n}</p>
<div style="width:{max(4, 420 * v / mx):.0f}px;height:34px;background:{c};border-radius:5px"></div>
<p style="font-family:{MONO};font-size:25px;white-space:nowrap">{v:,.0f}</p></div>''' for n, v, c in bk)
step = lambda k, t: (f'<div style="display:flex;gap:18px;align-items:baseline"><p style="font-family:{MONO};font-size:30px;font-weight:600;color:{BLUE};width:34px;flex-shrink:0">{k}</p>'
                     f'<p style="font-size:26px;line-height:1.38">{t}</p></div>')
body = title("“Reach” = the weakest X17 signal one cycle can see at 3σ",
             "It is a ratio, measured against the ordinary e⁺e⁻ pairs from the same nuclear transition.")
body += f'''<div style="display:flex;gap:56px">
<div style="flex:1;display:flex;flex-direction:column;gap:20px">
{step("1", f"A thermal neutron captured on ³He makes the 20.58 MeV photon once per {sci(1/NG_PER_N)} captures. One photon in {1/A_PAIR:.0f} is replaced by an e⁺e⁻ pair: <b>internal pair conversion (IPC, M1)</b>.")}
{step("2", "If the X17 exists, the same transition sometimes emits an X17 that decays to e⁺e⁻ at ~140°. <b>X17/IPC(M1)</b> = X17 per ordinary M1 pair.")}
{step("3", f"<b>3σ reach {sci(R_DES)}</b>: if nature's ratio is above this, one 50-day cycle shows a ≥3σ excess in the opening-angle fit. Below it, the cycle sees nothing.")}
{step("4", f"In branching-ratio units, ×{sci(A_PAIR, 2)}: Γ<sub>X</sub>/Γ<sub>γ</sub> = <b>{sci(R_DES * A_PAIR)}</b>, i.e. one X17 per {1/(R_DES*A_PAIR):,.0f} ordinary photons.")}
</div>
{card(f"""<p style="font-size:26px;font-weight:600">One cycle at the reach (n_TOF hardware + CFRP, no panel)</p>
<p style="font-size:22px;color:{MUT}">Detected events after all cuts, opening angle 60–180°, {sci(DES.best_R)} n/s, live {DES.live:.2f}</p>
{bars}
<p style="font-size:24px;line-height:1.35">{n_x:.0f} X17 among ~{(DES.M1 + DES.E0 + DES.ACC + DES.COS) / 1e3:.0f}k background events still gives 3σ, because the X17 piles up in a narrow angular peak while the background is spread out.</p>""", w=820)}
</div>
{sd.callout("Scaling: when background dominates, the reach goes as 1/√(exposure). Halving it needs 4× the beam time, or 4× less background under the peak.", BLUE, 25)}'''
slides["reach_what"] = sec("reach_what", body,
    "The reach is 3σ(μ) from an Asimov Fisher matrix over opening-angle bins 60–180° (sim_feasibility.reach). μ scales an X17 template normalised to X17/IPC(M1) = 1. "
    "M1, E0 and ³He(n,γ) float; accidentals, cosmics and wall are fixed (no shape systematics). The best beam rate is chosen per design. "
    f"Pair conversion: 0.2014 µb of M1 pairs per 55 µb (n,γ) = {A_PAIR:.3e} (Born, sept26 ipc_born). Per absorbed neutron the M1 pair yield is {NG_PER_N * A_PAIR:.2e}. "
    "X17 is attached to M1 only, because V/A/P bosons cannot come from the 0⁺ (¹S₀) entrance channel. "
    f"X17 acceptance × efficiency is ~{DES.X17 / DES.M1:.0f}× that of M1 pairs, because most IPC pairs have small opening angles and fail the two-arm topology.")

# ---- versus ATOMKI
lo_, hi_ = -3.3, -0.9
X0, W = 120, 1500
xm = lambda v: X0 + W * (math.log10(v) - lo_) / (hi_ - lo_)
be8 = 6e-6 / A_PAIR; c12 = 3.6e-6 / A_PAIR
pts = [(be8, "ATOMKI ⁸Be (M1)", ORANGE, -1, f"⁸Be 18.15 MeV 1⁺→0⁺ M1: Γ_X/Γ_γ = 6(1)×10⁻⁶. Same Γ_X/Γ_γ in ³He ⇒ X17/IPC(M1) = {sci(be8)}. (Direct X17/IPC in ⁸Be: 6×10⁻⁶ / 3.9×10⁻³ = 1.5×10⁻³.)"),
       (c12, "ATOMKI ¹²C (E1)", ORANGE, 1, f"¹²C 17.23 MeV E1: Γ_X/Γ_γ = 3.6(3)×10⁻⁶ ⇒ {sci(c12)} at equal Γ_X/Γ_γ. Different multipolarity."),
       (R_FLOOR, "statistics floor", "#7d8796", 1, "Pure IPC statistics, every other background removed (200 ps design rate)."),
       (R_GOOD, "200 ps + panel", "#7d8796", -1, "The original 2 Oct requirement."),
       (R_DES, "n_TOF hw + CFRP", BLUE, 1, "This week's design: 5 ns, per-arm trigger, ≤3° MM segments, collinearity 20°, CFRP end cap, no panel."),
       (2.5e-2, "rate-table reference", MUT, -1, "The normalisation used so far (Dec 2025 rate table). Not a prediction."),
       (5.3e-2, "n_TOF hw, no segments", C["cos"], 1, "n_TOF hardware + panel, no Micromegas condition.")]
o = []
yA = 210
o.append(f'<rect x="{xm(7.5e-4):.0f}" y="{yA-14}" width="{xm(2.2e-3)-xm(7.5e-4):.0f}" height="28" fill="{ORANGE}" opacity="0.12"/>')
o.append(f'<line x1="{X0}" y1="{yA}" x2="{X0+W}" y2="{yA}" stroke="{MUT}" stroke-width="2"/>')
for e in (-3, -2, -1):
    for m in range(1, 10):
        v = m * 10 ** e
        if lo_ <= math.log10(v) <= hi_:
            big = m == 1
            o.append(f'<line x1="{xm(v):.1f}" y1="{yA}" x2="{xm(v):.1f}" y2="{yA + (14 if big else 7)}" stroke="{MUT}" stroke-width="{2 if big else 1}"/>')
            if big or m in (2, 5):
                o.append(T(xm(v), yA + 40, sci(v, 0) if not big else f"10{str(e).translate(str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹'))}", 20))
                o.append(T(xm(v), yA + 66, sci(v * A_PAIR, 0), 18, fill="#9aa1ad"))
o.append(T(X0 + W, yA + 96, "upper row: X17/IPC(M1)   ·   lower row: Γ(X17)/Γ(γ) = X17/IPC × 3.66×10⁻³", 19, anchor="end"))
for v, lab, col, side, tp in pts:
    x = xm(v); yy = yA - 70 if side < 0 else yA - 135
    o.append(f'<g{tipattr(tp)}><line x1="{x:.1f}" y1="{yy+8}" x2="{x:.1f}" y2="{yA-8}" stroke="{col}" stroke-width="2" stroke-dasharray="4 4"/>'
             f'<circle cx="{x:.1f}" cy="{yA}" r="10" fill="{col}"/>'
             + T(x, yy - 18, lab, 22, fill=col, weight=600) + T(x, yy + 6, sci(v), 20, fill=col) + "</g>")

scale_svg = svg(1664, 320, "".join(o), "Reach compared with ATOMKI on a log scale")
rows_ = [("⁸Be 18.15 MeV", "1⁺→0⁺ M1 (same as thermal ³He)", "Γ<sub>X</sub>/Γ<sub>γ</sub> = 6×10⁻⁶", f"{sci(be8)}"),
         ("¹²C 17.23 MeV", "1⁻→0⁺ E1", "Γ<sub>X</sub>/Γ<sub>γ</sub> = 3.6×10⁻⁶", f"{sci(c12)}"),
         ("⁴He, ³H(p,e⁺e⁻)", "0⁻/1⁻ p-wave + E0, E<sub>p</sub> 0.5–0.9 MeV", "X17/E0 pairs ≈ 0.2", "not comparable: those states are absent at thermal energy")]
tbl = "".join(f'<tr><td style="padding:8px 18px 8px 0;font-weight:600">{a}</td><td style="padding:8px 18px;color:{MUT}">{b}</td>'
              f'<td style="padding:8px 18px;font-family:{MONO}">{c}</td><td style="padding:8px 0 8px 18px;font-family:{MONO};color:{ORANGE}">{d}</td></tr>' for a, b, c, d in rows_)
body = title(f"If ³He behaves like ⁸Be, the X17 is ~{R_DES / be8:.0f}× below our reach",
             "Our reach next to ATOMKI's claims, on one log axis. Lower means a weaker signal. Hover the points.")
body += f'''{scale_svg}
<div style="display:flex;gap:48px;align-items:flex-start">
<table style="font-size:23px;border-collapse:collapse;flex:1.25"><tr style="border-bottom:2px solid {INK};font-weight:600"><td style="padding:6px 0">ATOMKI</td><td style="padding:6px 18px">transition</td><td style="padding:6px 18px">measured</td><td style="padding:6px 0 6px 18px">as X17/IPC(M1) in ³He</td></tr>{tbl}</table>
<div style="flex:1">{sd.callout(f"<b>Even with zero background, one cycle would not reach ⁸Be's level</b> (floor {sci(R_FLOOR)} vs {sci(be8)}): that needs ~{(R_FLOOR / be8) ** 2:.0f} cycles. <b>Why ³He may still win:</b> its thermal M1 photon is strongly hindered (55 µb; the one-body M1 nearly cancels). A boson with different isospin couplings need not be, so X17/γ could be far above ⁸Be's. Nobody has computed the thermal point.", ORANGE, 23)}</div>
</div>'''
slides["reach_atomki"] = sec("reach_atomki", body,
    "ATOMKI values: ⁸Be Γ_X/Γ_γ = 6(1)×10⁻⁶ with IPC coefficient 3.9×10⁻³ for the 18.15 MeV M1 (so X17/IPC ≈ 1.5×10⁻³ in ⁸Be itself); ¹²C 17.23 MeV Γ_X/Γ_γ = 3.6(3)×10⁻⁶; ⁴He (Krasznahorkay et al., PRC 104, 044003 (2021) and arXiv:1910.10459): σ(X17)/σ(E0) ≈ 0.20. "
    "The conversion to ³He assumes equal Γ_X/Γ_γ and uses ³He's own M1 pair coefficient (3.66×10⁻³). That is an assumption, not a prediction: the X17 couplings are isospin dependent, and the thermal ³He M1 is a hindered transition dominated by meson-exchange currents (FACILITY.md, theory context). "
    "Viviani et al. (PRC 105, 014001 (2022)) computed n+³He only from E_n = 0.17 MeV; a run of their code at thermal energy would turn this slide from a comparison into a prediction. "
    "Cycles to reach ⁸Be's level at the floor: (floor/⁸Be)², since the floor scales as 1/√exposure.",
    foot="ATOMKI: Krasznahorkay et al., PRL 116, 042501 (2016); PRC 104, 044003 (2021); arXiv:1910.10459. ¹²C: PRC 106, L061601 (2022).")

# ---- verdict
_b = pd.read_csv(ILL / "sim/analysis_v3/cons/bo_ringCFRP.csv")
R_FL_NT = float(_b[(_b.hw == "nTOF 5 ns, no veto, strict") & (_b.scenario == "oracle: IPC only")].reach3.iloc[0])
gap = [("n_TOF hardware + CFRP, as is", R_DES, BLUE), ("same, every background removed", R_FL_NT, "#7d8796"),
       ("200 ps design, every background removed", R_FLOOR, "#b0b6c0")]
gx = 1 / be8
grow = "".join(f'''<div style="display:flex;align-items:center;gap:18px;height:58px">
<p style="width:500px;flex-shrink:0;font-size:25px;text-align:right">{n}</p>
<div style="width:{55 * v * gx:.0f}px;height:36px;background:{c};border-radius:5px;flex-shrink:0"></div>
<p style="font-family:{MONO};font-size:26px;font-weight:600;white-space:nowrap">×{v * gx:.1f}</p></div>''' for n, v, c in gap)
grow += f'''<div style="display:flex;align-items:center;gap:18px;height:40px"><p style="width:500px;flex-shrink:0;font-size:25px;text-align:right;color:{ORANGE}">ATOMKI ⁸Be level</p>
<div style="width:55px;height:4px;background:{ORANGE}"></div><p style="font-family:{MONO};font-size:26px;color:{ORANGE}">×1</p></div>'''
lev = [("More cycles", f"floor ∝ 1/√N: ~{(R_FLOOR / be8) ** 2:.0f}–{(R_FL_NT / be8) ** 2:.0f} cycles of 50 d. Years of PF1B time."),
       ("X17 efficiency", "the Esum cut keeps ~25% (stack holds ~40% of the energy). ×4 containment ≈ ×2 on the floor."),
       ("Spin selection", "E0 is ~60% of the pairs left and comes only from the singlet. Polarised n + ³He: floor ÷ ~1.6, and the boson's J<sup>π</sup>.")]
levs = "".join(f'<p style="font-size:24px;line-height:1.35"><b>{a}:</b> {b}</p>' for a, b in lev)
nxt = [("1", "Thermal theory point", "The thermal ³He M1 is hindered (55 µb). Ask Viviani et al. for X17/γ at E<sub>n</sub> ≈ 25 meV: it decides whether ³He sits above or below ⁸Be."),
       ("2", "Polarised ³He at PF1B", "Tyrex cell + polarised beam: E0 suppression and the J<sup>π</sup> handle. Cell compatibility, polarisation, and lifetime in beam."),
       ("3", "Simulate the levers", "E0-removed oracle and an efficiency (containment) scan in the budget mode, to replace the ×2 and ÷1.6 estimates.")]
nxts = "".join(f'''<div style="flex:1;display:flex;flex-direction:column;gap:8px;border-top:4px solid {BLUE};padding-top:16px">
<p style="font-size:26px;font-weight:600"><span style="color:{BLUE}">{k}</span>  {a}</p><p style="font-size:22px;color:{MUT};line-height:1.35">{b}</p></div>''' for k, a, b in nxt)
body = title("Unpolarised, the current apparatus cannot reach ⁸Be's level in one cycle",
             "How far each design sits above the ATOMKI ⁸Be-equivalent X17/IPC (1.6×10⁻³), per 50-day cycle. Even with zero background the gap stays ×3–4 (×2.7 at 200 ps).")
body += f'''<div style="display:flex;gap:48px;align-items:flex-start">
<div style="display:flex;flex-direction:column;gap:2px">{grow}</div>
{card(f"<p style='font-size:26px;font-weight:600'>What can still close it</p>{levs}<p style='font-size:22px;color:{MUT}'>Efficiency + spin together ≈ 2×10⁻³ (scaling estimate, not simulated; both optimistic).</p>", w=700)}
</div>
<div style="display:flex;gap:36px">{nxts}</div>'''
slides["reach_verdict"] = sec("reach_verdict", body,
    "Gap = reach / (6e-6 / 3.66e-3). Rows: CFRP design (n_TOF hardware, 3° segments, collinearity 20°, no panel, Esum > 13; pooled estimator 1.2e-2), its IPC-only floor (bo_ringCFRP oracle), and the 200 ps design's floor (FEASIBILITY_SIM §3). "
    "Background removal cannot go below the floor: it is the M1 + E0 pairs of the same transition. Floor scaling: Fisher σ(μ) ∝ √B / S, with S ∝ ε_X and B ∝ ε_IPC, so a common efficiency gain k gives 1/√k. "
    "E0 removal: B falls to ~40%, so the floor falls by ~1/√0.4 ≈ 1.6 if the X17 (triplet only) is kept; real polarisations (n ~99.7%, ³He ~70–75%) leave part of the E0. "
    "The ⁸Be comparison assumes equal Γ_X/Γ_γ; the thermal ³He M1 is a hindered, meson-exchange-dominated transition, so X17/γ could be much larger or smaller. That is the M1 caveat, and the reason for next step 1. "
    "The bars on the left are simulated; the right-hand card is scaling estimates.")

# =========================================================================== 2 funnel
NABS = 0.9e10 * 50 * 86400
other = 1.83e-3
rows = [
    ("³He(n,p) captures", NABS, "p + t stop in the gas within a few cm; never reach the arms", MUT),
    ("Captures elsewhere", NABS * other, "Air, window, caps, detector. γ ≤ 10.8 MeV: trigger + accidentals", MUT),
    ("³He(n,γ) 20.58 MeV", NABS * 1.03e-8, "1.03×10⁻⁸ per absorbed neutron", C["g"]),
    ("e⁺e⁻ pairs (IPC M1+E0)", NABS * 4.81e-11, "4.8×10⁻¹¹ per n: the continuum under the X17", C["ipc"]),
    ("X17 at reference ratio", NABS * 0.025 * 3.78e-11, "2.5% of M1 pairs: a normalisation, not a prediction", BLUE),
    ("X17 detected", 700, "1.9% acc × ε after trigger, Esum > 13 MeV, pile-up", BLUE),
]
lo, hi = 2, 17
bars = []
for name, v, note, col in rows:
    wpx = 600 * (math.log10(v) - lo) / (hi - lo)
    tp = f"{name}: {v:.3g} per 50-day cycle\n{note}"
    bars.append(f'''<div{tipattr(tp)} style="display:flex;align-items:center;gap:24px">
<p style="width:320px;font-size:28px;font-weight:600;text-align:right">{name}</p>
<div style="width:780px;display:flex;align-items:center;gap:16px"><div style="width:{wpx:.0f}px;height:44px;background:{col};border-radius:6px"></div>
<p style="font-family:{MONO};font-size:28px;font-weight:600;white-space:nowrap">{sci(v) if v > 1e4 else f"~{v:.0f}"}</p></div>
<p style="width:500px;font-size:24px;color:{MUT};line-height:1.25">{note}</p></div>''')
body = title("One cycle: 4×10¹⁶ neutrons → ~700 detected X17",
             f"Per 50-day cycle at the optimum 0.9×10¹⁰ absorbed n/s ({T_G1}, 200 ps + veto). Bar length is log₁₀(count). "
             "Hover dotted terms, bars and points for details.")
body += '\n<div style="display:flex;flex-direction:column;gap:16px">' + "\n".join(bars) + "</div>"
body += f'''\n<div style="display:flex;gap:16px;align-items:center"><p style="font-size:26px;color:{INK}"><b>Acceptance ladder for X17:</b> leptons in two different arms 32% → SiPM fires in both 12% → Esum &gt; 12 MeV 3.1%.</p></div>'''
slides["funnel"] = sec("funnel", body,
    "Counts per 50-day cycle at 0.9e10 absorbed n/s (3.9e16 absorbed). Every neutron is absorbed in the 3He; 94% of beam primaries give 3He(n,p). The (n,p) products are 573 keV p + 191 keV t; their range in 3He is roughly 5 cm at 1 bar (estimate, not from the MC), so they stay inside the cell. Captures elsewhere: 1.8e-3 per absorbed n for G1, of which the detector (LS, plastics, Al frames) ~1.2e-3 and air 2.7e-4. Pair yields from the Born IPC: M1 3.78e-11, E0 1.03e-11 per absorbed n. The Esum cut keeps only ~25% of the X17 pairs because the stack contains a median of 40% of the lepton energy.",
    foot="Sources: FEASIBILITY_SIM.md §2, results/scan_v1.csv (G1).")

# =========================================================================== 3 what is left
comp = [("Cosmic μ", 1_150_000, 360, C["cos"]), ("Accidentals", 87_000, 5_100, C["acc"]),
        ("IPC pairs", 14_600, 9_700, C["ipc"]), ("³He(n,γ) fakes", 1_070, 710, C["g"]),
        ("X17 (reference)", 1_050, 700, C["x17"])]
lo, hi = 2, 6.3
def hb(v, col, alpha=1.0, tip=None):
    w = 620 * (math.log10(v) - lo) / (hi - lo)
    return (f'<div{tipattr(tip)} style="display:flex;align-items:center;gap:12px"><div style="width:{w:.0f}px;height:34px;background:{col};opacity:{alpha};border-radius:5px"></div>'
            f'<p style="font-family:{MONO};font-size:26px;white-space:nowrap">{v:,}</p></div>')
rws = "".join(f'''<div style="display:flex;align-items:center;gap:24px;padding:10px 0;border-bottom:1px solid {RULE}">
<p style="width:260px;font-size:28px;font-weight:600;text-align:right">{n}</p>
<div style="width:760px">{hb(a, col, 0.45, f"{n}, today's design: {a:,} per cycle")}</div><div style="width:760px">{hb(b, col, 1.0, f"{n}, 200 ps + μ veto: {b:,} per cycle")}</div></div>''' for n, a, b, col in comp)
body = title("After cuts, cosmics outnumber X17 1000 to 1",
             f"Expected events per 50-day cycle, {T_G1}, {T_ESUM}, at each design's best rate. Bars are log-scaled.")
body += f'''
<div style="display:flex;flex-direction:column">
<div style="display:flex;gap:24px;padding-bottom:8px;border-bottom:2px solid {INK}"><p style="width:260px"></p>
<p style="width:760px;font-size:28px;font-weight:600">Today: σt 0.5 ns, no veto, 1.9×10¹⁰ n/s</p>
<p style="width:760px;font-size:28px;font-weight:600;color:{BLUE}">200 ps + μ veto, 0.9×10¹⁰ n/s</p></div>
{rws}
<div style="display:flex;gap:24px;padding-top:16px"><p style="width:260px;font-size:28px;font-weight:600;text-align:right">3σ reach</p>
<p style="width:760px;font-family:{MONO};font-size:40px;font-weight:600;color:{C["cos"]}">5.2×10⁻²</p>
<p style="width:760px;font-family:{MONO};font-size:40px;font-weight:600;color:{BLUE}">8.4×10⁻³</p></div></div>'''
slides["leftover"] = sec("leftover", body,
    "From the FEASIBILITY_SIM table. With good timing the optimum rate drops from the beam maximum to ~1e10 because accidentals scale as R^2 * 2tau and become the largest background once cosmics are gone. Single-neutron fakes (wall, air, detector captures) are zero above 12-13 MeV: no capture except 3He(n,g) releases more than 10.83 MeV (14N).",
    foot="Other single-neutron fakes: 0, since every capture except ³He(n,γ) is ≤ 10.83 MeV (¹⁴N).")

# =========================================================================== 4 spectra vs angle
def spec_svg(sp, ttl, w=800, h=500):
    x0, y0, pw, ph = 100, 20, w - 130, h - 120
    lo_, hi_ = 0.1, 2e5
    xm = lambda v: x0 + (v - 40) / 140 * pw
    ym = lambda v: y0 + ph - (math.log10(max(v, lo_)) - math.log10(lo_)) / (math.log10(hi_) - math.log10(lo_)) * ph
    o = [axes(x0, y0, pw, ph, [(v, f"{v}°") for v in (40, 60, 80, 100, 120, 140, 160, 180)],
              [(10 ** k, ("10" + str(k).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")))) for k in range(-1, 6)],
              "reconstructed opening angle", "events / 4° / cycle", xm, ym)]
    ser = [("cos", sp.COS), ("acc", sp.ACC), ("ipc", sp.M1 + sp.E0), ("g", sp.G), ("x17", sp.X17_ref)]
    for k, v in ser:
        xs, ys = step_xy(BINS, np.asarray(v))
        o.append(poly([xm(a) for a in xs], [ym(b) for b in ys], C[k], 4 if k == "x17" else 3))
    nm = dict(cos="cosmics", acc="accidentals", ipc="IPC M1+E0", g="³He(n,γ)", x17="X17 @ ref")
    for i in range(len(CEN)):
        tp = f"{BINS[i]:.0f}–{BINS[i+1]:.0f}°, events per cycle:\n" + "\n".join(
            f"{nm[k]}: {float(np.asarray(v)[i]):,.0f}" for k, v in ser[::-1])
        o.append(f'<rect class="hit" x="{xm(BINS[i]):.1f}" y="{y0}" width="{xm(BINS[i+1]) - xm(BINS[i]):.1f}" '
                 f'height="{ph}" fill="transparent"{tipattr(tp)}/>')
    return svg(w, h, "".join(o), ttl)
body = title("X17 sits on the IPC tail; today cosmics bury it",
             f"{T_G1}, {T_SIPM2}, Esum > 12 MeV, one cycle. Same axes in both panels; hover a bin for the counts.")
body += f'''
<div style="display:flex;gap:48px">
<div style="display:flex;flex-direction:column;gap:8px"><p style="font-size:28px;font-weight:600">Today (σt 0.5 ns, no veto)</p>{spec_svg(spB, "today")}</div>
<div style="display:flex;flex-direction:column;gap:8px"><p style="font-size:28px;font-weight:600;color:{BLUE}">200 ps + μ veto</p>{spec_svg(spT, "timing")}</div>
</div>
{legend_row([("X17 at reference", C["x17"]), ("IPC M1+E0", C["ipc"]), ("³He(n,γ)", C["g"]), ("accidentals", C["acc"]), ("cosmics", C["cos"])])}'''
slides["angle"] = sec("angle", body,
    "Spectra are the expected counts per 4 degree bin at each design's optimum rate (v3_base and v3_timing, spectrum_G1). X17 true opening angle is 110/121/151 deg (p16/50/84) with a hard edge at 110 deg; IPC M1 is 52/77/111 deg. The reconstructed (nomline) angle resolution is ~7 deg sigma68, which only rounds the edge. The fit floats M1, E0, 3He(n,g) and fixes accidentals and cosmics.")

# =========================================================================== 5 why timing
dt = np.array(X["cos_dt_hist"]); dte = np.arange(0, 6.01, 0.25)
w, h = 700, 520
x0, y0, pw, ph = 100, 20, w - 130, h - 120
xm = lambda v: x0 + v / 5 * pw
ymax = dt.max() / dt.sum() * 1.1
ym = lambda v: y0 + ph - v / ymax * ph
o = []
o.append(f'<rect x="{xm(0):.1f}" y="{y0}" width="{xm(1.5)-xm(0):.1f}" height="{ph}" fill="{C["cos"]}" opacity="0.10"/>')
o.append(f'<rect x="{xm(0):.1f}" y="{y0}" width="{xm(0.6)-xm(0):.1f}" height="{ph}" fill="{BLUE}" opacity="0.22"/>')
o.append(axes(x0, y0, pw, ph, [(v, f"{v}") for v in range(6)], [(v, f"{v*100:.0f}%") for v in (0, 0.1, 0.2, 0.3, 0.4)],
              "|Δt| between the two arms, true [ns]", "fraction of faking muons", xm, ym))
f = dt / dt.sum()
xs, ys = step_xy(dte[:21], f[:20])
o.append(poly([xm(a) for a in xs] + [xm(5), xm(0)], [ym(b) for b in ys] + [ym(0), ym(0)], None, fill=C["cos"]))
o.append(T(xm(3.25), y0 + 40, "μ: median 2.8 ns", 19, fill="#9e2b3b", anchor="start", weight=700))
o.append(T(xm(3.25), y0 + 110, "today: |Δt| &lt; 1.5 ns", 19, fill=C["cos"], anchor="start"))
o.append(T(xm(3.25), y0 + 150, "200 ps: |Δt| &lt; 0.6 ns", 19, fill=BLUE, anchor="start", weight=700))
o.append(T(xm(3.25), y0 + 190, "pairs: |Δt| ≈ 0.05 ns", 19, fill=INK, anchor="start"))
dtsvg = svg(w, h, "".join(o), "cosmic dt")
# end-view diagram
w2, h2 = 520, 520
cx, cy = 260, 260
g = []
for (ax, ay, aw, ah) in [(cx - 150, cy - 230, 300, 26), (cx - 150, cy + 204, 300, 26), (cx - 230, cy - 150, 26, 300), (cx + 204, cy - 150, 26, 300)]:
    g.append(f'<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" fill="{BG2}" stroke="{MUT}" stroke-width="2" rx="4"/>')
g.append(f'<circle cx="{cx}" cy="{cy}" r="40" fill="#dfe8f3" stroke="{BLUE}" stroke-width="2"/>')
g.append(f'<line x1="{cx-130}" y1="10" x2="{cx-40}" y2="{h2-10}" stroke="{C["cos"]}" stroke-width="4" stroke-dasharray="12 6"/>')
for (ex, ey) in [(cx + 40, cy - 217), (cx + 217, cy + 110)]:
    g.append(f'<line x1="{cx}" y1="{cy}" x2="{ex}" y2="{ey}" stroke="{BLUE}" stroke-width="4"/>')
g.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{BLUE}"/>')
g.append(T(cx + 52, cy - 238, "t₀", 22, fill=BLUE, anchor="start", weight=700))
g.append(T(cx + 186, cy + 150, "t₀", 22, fill=BLUE, anchor="end", weight=700))
g.append(T(cx - 136, cy - 238, "t₀", 22, fill=C["cos"], anchor="end", weight=700))
g.append(T(cx - 60, cy + 196, "t₀ + 2.8 ns", 22, fill=C["cos"], anchor="end", weight=700))
g.append(T(cx + 20, cy + 64, "cell", 20, fill=BLUE, anchor="start"))
diag = svg(w2, h2, "".join(g), "end view: pair vs muon timing")
body = title("Why 200 ps: a muon takes ~3 ns to cross",
             "End view, beam into the page. Faking muons hit top + bottom (57%) or top/bottom + side (43%); pair leptons hit their arms together.")
body += f'''
<div style="display:flex;gap:24px;align-items:start">{diag}{dtsvg}
<div style="display:flex;flex-direction:column;gap:20px;width:396px">
{card(f'<p style="font-size:25px;line-height:1.35"><b>Time-of-flight, not Micromegas pile-up.</b> At 0.5 ns per arm the 1.5 ns window keeps the muon tail (3%). At 0.2 ns, only the 0.15% with true |Δt| &lt; 0.5 ns survive.</p>', pad=28)}
{card(f'<p style="font-size:25px;line-height:1.35"><b>Bonus: accidentals</b>, two unrelated hits in 2τ, scale as R²·2τ. 5 → 1.2 ns cuts them ×4. MM occupancy (≤ 0.3/µs) is only a signal loss.</p>', pad=28)}
</div></div>'''
slides["timing"] = sec("timing", body,
    f"Cosmic two-arm rate passing sipm2 + Esum>12 MeV: {X['cos_rate_Hz']:.1f} Hz before timing (~3e7 per cycle). Arm pairs: top-bottom 57%, top/bottom-side 43%, side-side 0.1% (zenith along z). Through-going muons deposit ~8 MeV per arm, so the Esum cut does not help, and the LS cannot be used as a veto because X17 leptons reach it too (median 5.8 MeV). Timing alone (0.2 ns) takes the reach from 5.2e-2 to 1.2e-2; adding a 1e-2 veto gives 8.4e-3. The 2.8 ns median is the arm-to-arm flight path at c.",
    foot="K1: 1.3×10⁸ sea-level μ (1 live day), G5 geometry, no hall overburden. Δt from the scintillator times.")

# =========================================================================== 6 levers
var = [("Today: σt 0.5 ns, 2τ 5 ns, no veto", 5.18e-2, C["cos"]),
       ("2τ 3 ns", 5.09e-2, MUT), ("Ideal vertex (true, per event)", 4.48e-2, MUT),
       ("μ veto 10⁻² only", 1.50e-2, MUT), ("σt 0.3 ns", 1.53e-2, MUT), ("σt 0.2 ns", 1.23e-2, MUT),
       ("σt 0.2 ns + μ veto 10⁻²", 8.34e-3, BLUE), ("No cosmics (oracle)", 1.27e-2, "#b0b6c0"),
       ("No cosmics, no accidentals", 4.87e-3, "#b0b6c0"), ("IPC only: statistics floor", 4.72e-3, "#b0b6c0")]
sc = 1000 / 0.055
rr = []
for n, v, col in var:
    tp = f"{n}: 3σ reach {sci(v, 2)} per cycle ({v / 0.025:.2f} × the reference ratio)"
    rr.append(f'''<div{tipattr(tp)} style="display:flex;align-items:center;gap:20px;height:52px">
<p style="width:520px;font-size:27px;text-align:right">{n}</p>
<div style="display:flex;align-items:center;gap:14px"><div style="width:{v*sc:.0f}px;height:34px;background:{col};border-radius:5px"></div>
<p style="font-family:{MONO};font-size:26px;white-space:nowrap">{sci(v)}</p></div></div>''')
xref = 540 + 0.025 * sc
body = title("The levers: timing and a veto, not the vertex",
             "3σ reach per cycle, G1, Esum > 13 MeV, one assumption changed at a time. Lower is better.")
body += f'''
<div style="position:relative;width:1664px;height:560px">
<div style="position:absolute;left:{xref:.0f}px;top:0px;width:3px;height:540px;background:{ORANGE};opacity:0.7"></div>
<p style="position:absolute;left:{xref+12:.0f}px;top:0px;width:420px;font-size:24px;color:{ORANGE}">reference ratio 2.5×10⁻²</p>
<div style="position:absolute;left:0px;top:20px;width:1664px;display:flex;flex-direction:column;gap:2px">{"".join(rr)}</div>
</div>'''
slides["levers"] = sec("levers", body,
    "variants_v3.csv, G1 sipm2 Esum>13. Each row re-optimises the rate. The true-vertex row uses the generated vertex instead of the assumed cell centre: only ~13% better, because the X17 opening-angle spread (110-150 deg) is much wider than the ~7 deg resolution. Grey rows are oracles that remove a background entirely, to show what limits each regime.")

# =========================================================================== 7 opening angle doesn't help vs cosmics
ch = np.array(X["cos_theta_hist"]); xr = np.asarray(spT.X17_ref)
w, h = 980, 520
x0, y0, pw, ph = 100, 20, w - 140, h - 120
xm = lambda v: x0 + (v - 40) / 140 * pw
fc, fx = ch / ch.sum(), xr / xr.sum()
ymax = max(fc.max(), fx.max()) * 1.12
ym = lambda v: y0 + ph - v / ymax * ph
o = [axes(x0, y0, pw, ph, [(v, f"{v}°") for v in range(40, 181, 20)], [(v, f"{v*100:.0f}%") for v in (0, 0.04, 0.08, 0.12)],
          "chord opening angle (vertex assumed at the cell centre)", "fraction / 4°", xm, ym)]
xs, ys = step_xy(BINS, fc); o.append(poly([xm(a) for a in xs] + [xm(180), xm(40)], [ym(b) for b in ys] + [ym(0), ym(0)], None, fill=C["cos"]))
xs, ys = step_xy(BINS, fx); o.append(poly([xm(a) for a in xs], [ym(b) for b in ys], C["x17"], 4.5))
o.append(T(xm(62), ym(fc[3]) - 18, "cosmic μ", 24, fill="#9e2b3b", weight=700))
o.append(T(xm(150), ym(fx.max()) - 14, "X17", 24, fill=BLUE, weight=700))
asvg = svg(w, h, "".join(o), "cosmic vs X17 chord angle")
dca = np.array(X["cos_dca_hist"]); dcs = np.array(X["G1_X17_dca_hist"])
body = title("A through-going muon fakes a 110–150° pair",
             "The chord estimator joins each hit to the assumed vertex. Any straight line through two arms becomes a ‘pair’.")
body += f'''
<div style="display:flex;gap:40px;align-items:start">{asvg}
<div style="display:flex;flex-direction:column;gap:20px;width:640px">
{card(f'<p style="font-size:26px;line-height:1.35"><b>Back-to-back only if it crosses the cell.</b> The median muon line misses the centre by 17 cm; ~1% pass within 2 cm.</p>')}
{card(f'<p style="font-size:26px;line-height:1.35"><b>Arms at ±22 cm:</b> a vertical muon 6–15 cm off-axis gives 2·atan(22/offset) = 110–150°.</p>')}
{card(f'<p style="font-size:26px;line-height:1.35">The handle has to be the <b>track direction in each arm</b> (next slide).</p>')}
</div></div>'''
slides["angle_cos"] = sec("angle_cos", body,
    "Cosmic chord-angle distribution from K1 after sipm2 + Esum>12 (before timing). X17 is the reconstructed nomline spectrum (G1). The distance of the muon line from the cell centre: p10/50/90 = 65/168/287 mm. For signal, the line joining the two Micromegas hits misses the centre by r*cos(theta/2), about 10 cm, so that distance does not separate them either.")

# =========================================================================== 8 collinearity veto
la = np.array(X["G1_X17_lineang_hist"], float); lae = np.arange(0, 90.01, 2.5)
w, h = 860, 520
x0, y0, pw, ph = 100, 20, w - 140, h - 120
xm = lambda v: x0 + v / 90 * pw
fl = la / la.sum(); ymax = fl.max() * 1.15
ym = lambda v: y0 + ph - v / ymax * ph
o = [axes(x0, y0, pw, ph, [(v, f"{v}°") for v in range(0, 91, 15)], [(v, f"{v*100:.0f}%") for v in (0, 0.02, 0.04, 0.06, 0.08)],
          "angle between the two Micromegas segments", "X17 fraction / 2.5°", xm, ym)]
o.append(f'<rect x="{xm(0):.1f}" y="{y0}" width="{xm(20)-xm(0):.1f}" height="{ph}" fill="{C["cos"]}" opacity="0.12"/>')
xs, ys = step_xy(lae, fl); o.append(poly([xm(a) for a in xs] + [xm(90), xm(0)], [ym(b) for b in ys] + [ym(0), ym(0)], None, fill=BLUE))
o.append(f'<line x1="{xm(20):.1f}" y1="{y0}" x2="{xm(20):.1f}" y2="{y0+ph}" stroke="{C["cos"]}" stroke-width="3" stroke-dasharray="8 5"/>')
o.append(T(xm(10), y0 + ph - 150, "μ: 0°", 22, fill="#9e2b3b", weight=700))
o.append(T(xm(21) + 6, y0 + 66, "cut 20°: keeps 91% of X17", 22, fill=INK, anchor="start"))
lsvg = svg(w, h, "".join(o), "segment line angle")
L = X["cos_lineang_leak_vs_sigma"]
def pct(v):
    return "&lt;0.1%" if v < 1e-3 else f"{100*v:.1f}%" if v < 0.1 else f"{100*v:.0f}%"
trs = "".join(f'<tr><td>{c}°</td><td>{100*X[f"G1_X17_eff_lineang_gt{c}"]:.0f}%</td><td>{pct(L["2"][str(c)])}</td><td>{pct(L["5"][str(c)])}</td><td>{pct(L["10"][str(c)])}</td></tr>'
              for c in (10, 15, 20, 25))
tbl = f'''<table style="font-size:26px;font-family:{SANS};color:{INK}">
<tr><th style="width:16%">cut</th><th style="width:21%">X17 kept</th><th style="width:21%">μ, σ 2°</th><th style="width:21%">μ, σ 5°</th><th style="width:21%">μ, σ 10°</th></tr>{trs}</table>'''
body = title("A free data veto: are the two segments one line?",
             "X17 legs leave radially, so their segments meet at 180° − θ ≈ 30–70°. A muon's segments are parallel.")
body += f'''
<div style="display:flex;gap:40px;align-items:start">{lsvg}
<div style="display:flex;flex-direction:column;gap:24px;width:760px">
{tbl}
<p style="font-size:24px;color:{MUT};line-height:1.3">σ is the per-segment direction resolution on a muon (toy model, Gaussian in 2D).</p>
{card(f'<p style="font-size:27px;line-height:1.35"><b>Decisive unknown: Micromegas direction resolution on a MIP.</b> At ≲ 5° this rivals a panel veto (×50 at 91% signal). n_TOF electron tracks gave 11–26°, mostly scattering. <b>Measure it on the cosmic bench.</b></p>', bg="#eef3fa")}
</div></div>'''
slides["collinear"] = sec("collinear", body,
    "X17 line angle uses the simulation's ideal PCA segment directions (S1, G1, sipm2, Esum>12), so it includes the lepton scattering in the Micromegas entrance and air. Cosmic leak is a toy: the true muon segments are exactly collinear (GeV muons do not scatter), and the measured line angle is the 2D difference of two independent direction errors, Rayleigh with scale sqrt(2)*sigma. A related cut: each segment should point back to the cell; muon segments miss the radial direction by a median of 35 deg (10% below 14 deg). This works offline, on data we already record, with no extra hardware.",
    foot="Signal from S1 (G1, 3.4×10⁶ X17, ideal segment directions incl. scattering). μ leak is a resolution toy.")

# =========================================================================== 9 panel veto
H6, H10 = X["veto_H600"], X["veto_H1000"]
def pc(v): return f"{100*v:.1f}%"
vt = f'''<table style="font-size:27px;font-family:{SANS};color:{INK}">
<tr><th style="width:34%">panel, height</th><th style="width:22%">1 × 1 m</th><th style="width:22%">2 × 2 m</th><th style="width:22%">3 × 3 m</th></tr>
<tr><td>ceiling, +0.6 m</td><td>{pc(H6["ceiling_1000"])}</td><td><b>{pc(H6["ceiling_2000"])}</b></td><td>{pc(H6["ceiling_3000"])}</td></tr>
<tr><td>ceiling, +1.0 m</td><td>{pc(H10["ceiling_1000"])}</td><td>{pc(H10["ceiling_2000"])}</td><td><b>{pc(H10["ceiling_3000"])}</b></td></tr>
<tr><td>floor, −0.6 m</td><td>{pc(H6["floor_1000"])}</td><td>{pc(H6["floor_2000"])}</td><td><b>{pc(H6["floor_3000"])}</b></td></tr>
<tr><td>floor, −1.0 m</td><td>{pc(H10["floor_1000"])}</td><td>{pc(H10["floor_2000"])}</td><td>{pc(H10["floor_3000"])}</td></tr></table>'''
# side-view schematic
w, h = 620, 600
g = [f'<rect x="60" y="40" width="500" height="22" fill="{BLUE}" opacity="0.85" rx="4"/>',
     f'<rect x="200" y="230" width="220" height="140" fill="{BG2}" stroke="{MUT}" stroke-width="2" rx="8"/>',
     f'<rect x="60" y="500" width="500" height="34" fill="#8b8f97" rx="3"/>',
     f'<rect x="60" y="540" width="500" height="22" fill="{BLUE}" opacity="0.5" rx="4"/>',
     f'<line x1="250" y1="10" x2="372" y2="590" stroke="{C["cos"]}" stroke-width="4" stroke-dasharray="12 6"/>',
     f'<line x1="310" y1="300" x2="470" y2="140" stroke="{BLUE}" stroke-width="3.5"/>',
     T(310, 296 + 110, "arms + cell", 22, fill=INK), T(310, 30, "ceiling scintillator", 22, fill=BLUE, weight=700),
     T(310, 590, "absorber + floor scintillator", 22, fill=INK), T(484, 134, "escaping e±", 20, fill=BLUE, anchor="start"),
     T(240, 160, "μ", 26, fill=C["cos"], weight=700)]
vsvg = svg(w, h, "".join(g), "veto panel side view")
body = title("Your panel idea works; put it on the ceiling",
             "Fraction of pair-faking muons (after Esum > 12 MeV) whose line crosses a panel. A 10⁻² veto needs ≥ 99%.")
body += f'''
<div style="display:flex;gap:48px;align-items:start">{vsvg}
<div style="display:flex;flex-direction:column;gap:24px;width:1000px">
{vt}
<div style="display:flex;gap:20px">
{card(f'<p style="font-size:25px;line-height:1.35"><b>Ceiling:</b> the muon hits the panel <i>before</i> the arms. Escaping pair leptons could only hit it <i>after</i>. A time-ordered veto needs no electron stopper.</p>', bg="#eef3fa")}
{card(f'<p style="font-size:25px;line-height:1.35"><b>Floor:</b> muons and escaping leptons both arrive after the arms. It needs an absorber, and a few cm of steel or Pb still leaks bremsstrahlung γ.</p>')}
</div></div></div>'''
slides["panels"] = sec("panels", body,
    "Muon trajectories from K1 (the line through the two arms' Micromegas hits), extrapolated to a horizontal plane above or below the detector centre. Muons are steep (zenith p10/50/90 = 8/22/44 deg), so a 2x2 m ceiling panel 0.6 m up catches 99.3%. Combine with scintillator efficiency (>=99.5% typical for thick plastic) for the total. The random-veto rate from the hall gamma background times the veto window sets the dead time; measure that on site. Caveats: sea-level flux, no overburden; the K1 generator plane is 3x3 m at 1.5 m. Ceiling plus floor would cover both and allow a 2-of-2 or 1-of-2 logic.",
    foot="K1 muon lines extrapolated to horizontal planes; the hall overburden is not included.")

# =========================================================================== accidentals: where they come from
# Inputs: sim/analysis_v3/acc_sources_<cfg>.json from sim/lxplus/acc_sources.py
ACCF = ILL / "sim/analysis_v3/acc_sources_G1.json"
AJ = json.load(open(ACCF))
ACC5 = ILL / "sim/analysis_v3/acc_sources_G5.json"
AJ5 = json.load(open(ACC5)) if ACC5.exists() else None
MCOL = {"Al": ORANGE, "air (¹⁴N)": "#2f8a5b", "Cu": "#8a5a2b", "Be": "#4a86c5", "³He": C["g"], "other": "#9aa1ad"}
MSHORT = {"air (¹⁴N)": "air ¹⁴N"}
inv = AJ["involvement_material"]
inv_src = AJ["involvement_source"]
sing = AJ["singles"]
rch = AJ["reach"]["timing"]
r_now = rch["none"]["reach3"]
acc_now = rch["none"]["acc"]
T_SINGLE = term("single", "One lepton arm with a Micromegas gap hit and ≥ 0.5 MIP in its SiPM bars, from one neutron, "
                "with nothing in the opposite arms.")
T_CAPVOL = term("capture volume", "The Geant4 volume where the event's neutron was captured (the table's capvol). "
                "The attribution is by that volume, not traced particle by particle.")

# ---- A: what accidentals are
w, h = 980, 560
g = []
tx0, tx1 = 150, 940
tm = lambda t: tx0 + (t + 1.5) / 4.5 * (tx1 - tx0)       # ns -> px
for yy, lab in ((170, "arm A"), (380, "arm B")):
    g.append(f'<rect x="{tx0}" y="{yy - 30}" width="{tx1 - tx0}" height="60" fill="{BG2}" rx="8"/>')
    g.append(T(tx0 - 20, yy + 8, lab, 24, fill=INK, anchor="end", weight=600))
g.append(f'<rect x="{tm(-0.6):.1f}" y="110" width="{tm(0.6) - tm(-0.6):.1f}" height="340" fill="{C["acc"]}" opacity="0.13"/>')
g.append(sd.line(tm(-0.6), 104, tm(0.6), 104, C["acc"], 3))
g.append(T(tm(0), 92, "2τ = 1.2 ns (200 ps per arm)", 22, fill="#8a6410", weight=700))
# hits
hA, hB = 0.0, 0.35
g.append(f'<circle cx="{tm(hA):.1f}" cy="170" r="16" fill="{ORANGE}"{tipattr("Single 1: a neutron captured in the 8 mm Al end cap; its 7.72 MeV capture γ Compton-scatters in arm A.")}/>')
g.append(f'<circle cx="{tm(hB):.1f}" cy="380" r="16" fill="{MCOL["air (¹⁴N)"]}"{tipattr("Single 2: a different neutron, captured on ¹⁴N in the air; its 10.83 MeV γ deposits in arm B.")}/>')
g.append(T(tm(hA), 226, "n₁ captured in Al", 22, fill=ORANGE, weight=700))
g.append(T(tm(hA), 252, "7.7 MeV γ → ~6.5 MeV", 21, fill=INK))
g.append(T(tm(hB), 436, "n₂ captured in air", 22, fill=MCOL["air (¹⁴N)"], weight=700))
g.append(T(tm(hB), 462, "10.8 MeV γ → ~7 MeV", 21, fill=INK))
g.append(sd.line(tx0, 500, tx1, 500, MUT, 1.5))
for t in (-1, 0, 1, 2, 3):
    g.append(sd.line(tm(t), 500, tm(t), 508, MUT, 1.5))
    g.append(T(tm(t), 534, f"{t}", 21))
g.append(T((tx0 + tx1) / 2, 556, "time [ns]", 22, fill=INK))
g.append(T(tm(2.3), 300, "Esum ≈ 13.5 MeV", 26, fill=INK, weight=700))
g.append(T(tm(2.3), 332, "passes the cut", 22, fill=INK))
tl = svg(w, h, "".join(g), "two unrelated singles inside the coincidence window")
bk = [("IPC pairs", 9_700, C["ipc"]), ("Accidentals", 5_100, C["acc"]), ("³He(n,γ) fakes", 710, C["g"]),
      ("Cosmic μ", 360, C["cos"]), ("1-neutron fakes", 0.5, "#b0b6c0")]
bars = sd.hbars([(n, v, c, f"{n}: {v:,.0f} per 50-day cycle (G1, 200 ps + μ veto, 0.9×10¹⁰ n/s)" if v >= 1
                  else "Single-neutron fakes above 13 MeV: 0 by kinematics; the MC has none in any configuration.")
                 for n, v, c in bk], vmax=12_000, width=330, h=32, label_w=230, size=24,
                fmt=lambda v: f"{v:,.0f}" if v >= 1 else "0")
body = title("With cosmics vetoed, accidentals are the next background, and they are pile-up",
             f"Two {T_SINGLE}s from two different neutrons inside {T_2TAU}. No single neutron makes them.")
body += f'''
<div style="display:flex;gap:40px;align-items:start">{tl}
<div style="display:flex;flex-direction:column;gap:20px;width:640px">
<p style="font-size:26px;font-weight:600">Per cycle, 200 ps + μ veto ({T_G1}, {T_ESUM})</p>
{bars}
{card(f'<p style="font-size:25px;line-height:1.35"><b>Rate ∝ R² · 2τ.</b> This is what sets the optimum at 0.9×10¹⁰ n/s rather than the beam maximum, and why 200 ps helps twice.</p>', pad=26)}
</div></div>'''
sec("acc_what", body,
    "The model (sim_feasibility.py, ACC): ACC = R² · 2τ · Σ over arm pairs Σ_ij p_i p_j P(E_i + E_j > cut), binned in the chord angle of the two gap hits. "
    "Singles come from C1 (analog) and C1w (walls ×300, air ×100), plus the ³He(n,γ) singles from C1g. "
    "Energies and positions are paired event by event, so the angular shape is the real one. "
    "Single-neutron correlated fakes (both arms from one capture) are a separate term, WALL, and are zero above 12 MeV: see the next slide.",
    foot="FEASIBILITY_SIM.md §2 table; the timeline is illustrative, the energies are typical of the passing pairs.")

# ---- B: capture lines vs the cut
QL = [("¹H", 2.224, "LS, plastics, PCB: 2.22 MeV"), ("¹²C", 4.946, "plastics, LS, CFRP: 4.95 MeV"),
      ("⁹Be", 6.812, "Be entrance window: 6.81 MeV"), ("²⁷Al", 7.724, "end caps, frames, flange: 7.72 MeV"),
      ("⁶³Cu", 7.916, "PCB pads, cathode, mesh: 7.92 MeV"), ("¹⁴N", 10.829, "air, Kapton: 10.83 MeV, the hardest single line"),
      ("Al + Al", 2 * 7.724, "two Al captures inside 2τ: up to 15.4 MeV"), ("Al + ¹⁴N", 7.724 + 10.829, "up to 18.6 MeV"),
      ("³He(n,γ)", 20.578, "the irreducible 1-neutron fake, floated in the fit")]
P = sd.Plot(700, 560, x=(0, 22), y=(0, len(QL)), xlabel="highest γ energy from the capture(s) [MeV]", margin=(24, 30, 92, 130))
P.xticks([(v, str(v)) for v in (0, 5, 10, 13, 15, 20)])
for i, (n, e, tp) in enumerate(QL):
    y = len(QL) - i - 0.5
    col = (MCOL["Al"] if "Al" in n else MCOL["air (¹⁴N)"] if "N" in n else MCOL["Be"] if "Be" in n
           else MCOL["Cu"] if "Cu" in n else C["g"] if "He" in n else "#9aa1ad")
    op = 0.55 if "+" in n else 1.0
    P.raw(f'<rect x="{P.X(0):.1f}" y="{P.Y(y) - 17:.1f}" width="{P.X(e) - P.X(0):.1f}" height="34" fill="{col}" '
          f'fill-opacity="{op}" rx="4"{tipattr(n + ": " + tp)}/>')
    P.raw(T(P.X(0) - 12, P.Y(y) + 8, n, 22, fill=INK, anchor="end", weight=600))
P.raw(sd.line(P.X(0), P.Y(3), P.X(22), P.Y(3), MUT, 1.5, "4 5"))
P.vline(13, C["cos"], label="cut 13 MeV", tip="Esum > 13 MeV: 3.5σ above ¹⁴N for a fully contained capture (σ/E ≈ 6 % at 11 MeV).")
qsv = P.svg("capture lines vs the energy cut")
eb = np.array(AJ["ebins"]); ec = 0.5 * (eb[1:] + eb[:-1])
S = sd.Plot(900, 560, x=(0, 14), y=(1e-12, 1e-6, "log"), xlabel="energy in one arm's scintillators [MeV]",
            ylabel="singles / arm / absorbed n / MeV")
S.xticks([(v, str(v)) for v in (0, 2, 4, 6, 8, 10, 12, 14)]).yticks(sd.log_ticks(-12, -6))
S.band([6.5, 14], [1e-12, 1e-12], [1e-6, 1e-6], C["acc"], 0.08,
       tip="A pair passes Esum > 13 MeV only if one single carries > 6.5 MeV: the hard tail is what matters.")
for m in ("other", "Be", "Cu", "air (¹⁴N)", "Al"):
    v = np.array(AJ["spectra"].get(m, []), float)
    if not len(v):
        continue
    sel = ec <= 14
    xs, ys = step_xy(eb[:sel.sum() + 1], np.clip(v[sel], 1e-12, None))
    S.line(xs, ys, MCOL[m], w=3, markers=False)
    tips = [f"{MSHORT.get(m, m)}, {eb[i]:.1f}–{eb[i + 1]:.1f} MeV: {v[i]:.2g} /arm/n/MeV" + (" (0: drawn at the floor)" if v[i] <= 0 else "")
            for i in range(sel.sum())]
    S.points(ec[sel], np.clip(v[sel], 1e-12, None), "transparent", r=4, tips=tips)
S.text(6.7, 4e-7, "can reach 13 MeV with a partner", 20, "#8a6410")
ssv = S.svg("single-arm energy by capture material")
body = title("No single capture reaches 13 MeV; two of them can",
             f"Left: per-arm energy of {T_SINGLE}s by the material that captured the neutron ({T_G1}). Right: the capture lines.")
body += f'''
<div style="display:flex;flex-direction:column;gap:6px">
<div style="display:flex;gap:40px;align-items:start">{ssv}{qsv}</div>
{sd.legend([(MSHORT.get(m, m), MCOL[m]) for m in ("Al", "air (¹⁴N)", "Cu", "Be", "other")], size=22)}</div>'''
sec("acc_lines", body,
    "This is why the n_TOF aluminium e⁺e⁻ background does not appear here as a correlated fake. At ILL the neutrons are thermal, so a capture releases at most its Q-value. Al gives at most 7.72 MeV, ¹⁴N 10.83 MeV, and the two-arm energy sum from one capture stays below the 13 MeV cut. The MC agrees: with the walls ×300 and the air ×100, there is no correlated wall, air or detector event above 12 MeV in any configuration (FEASIBILITY_SIM §4). "
    "\n\nAl comes back through pile-up instead. Two Al captures inside 2τ can sum to 15.4 MeV, and Al + ¹⁴N to 18.6 MeV. A passing accidental pair needs both singles near full containment of their lines, so it is the hard tail of the per-arm spectrum, above ~6 MeV, that matters, not the total singles rate. "
    "\n\nSpectra: rate-weighted, per arm (average of the four), per absorbed neutron, 0.5 MeV bins, from C1 + C1w. 'other' is LS, plastics, PCB/Kapton/Mylar, gas and the cell skin. Empty bins are drawn at the 10⁻¹² floor. The Al entries at 11–12 MeV are above the Al line, so that arm also holds energy from something else in the same event; this was not traced. Capture-line energies are the highest prompt γ of each isotope (thermal).",
    foot="Arm energy = SiPM bars + plastic + LS, unsmeared. C1 + C1w, sipm2 arm condition.")

# ---- C: which materials
mats = ["Al", "air (¹⁴N)", "Cu", "Be", "other"]
fold = lambda m: "other" if m == "³He" else m
src_rows = sorted(inv_src.items(), key=lambda kv: -kv[1])
src_rows = [(k, v) for k, v in src_rows if v >= 0.005]
hb_rows = [(k, 100 * v, MCOL[sing[k]["material"]] if k in sing else C["g"],
            f"{k}: in {100 * v:.1f}% of the accidental pairs (Esum > 13 MeV, 60–180°).\\n"
            f"Singles: {sing[k]['rate_per_arm']:.2g} per arm per n, {sing[k]['hard_rate_per_arm']:.2g} above 6 MeV." if k in sing else k)
           for k, v in src_rows]
hb_rows = [(a, b, c, d.replace("\\n", "\n")) for a, b, c, d in hb_rows]
hbs = sd.hbars(hb_rows, vmax=100, width=380, h=30, label_w=360, size=23, fmt=lambda v: f"{v:.0f}%")
pm = {}
for d in AJ["pairs_material"]:
    a_, b_ = fold(d["a"]), fold(d["b"])
    if mats.index(a_) > mats.index(b_):
        a_, b_ = b_, a_
    pm[(a_, b_)] = pm.get((a_, b_), 0.0) + d["share"]
pm.update({(b, a): s for (a, b), s in list(pm.items())})
n = len(mats); cs = 96
hx0, hy0 = 150, 70
g = []
for i, a in enumerate(mats):
    g.append(T(hx0 - 14, hy0 + i * cs + cs / 2 + 8, MSHORT.get(a, a), 22, fill=INK, anchor="end", weight=600))
    g.append(T(hx0 + i * cs + cs / 2, hy0 - 16, MSHORT.get(a, a), 22, fill=INK, weight=600))
    for j, b in enumerate(mats):
        if j < i:
            continue
        s = pm.get((a, b), 0.0)
        a_ = min(1.0, s / 0.30)
        fill = ORANGE if s > 0 else BG2
        lab = f"{100 * s:.0f}%" if s >= 0.005 else ("<1%" if s > 0 else "–")
        tp = f"{a} × {b}: {100 * s:.1f}% of the accidental background"
        g.append(f'<rect x="{hx0 + j * cs + 2}" y="{hy0 + i * cs + 2}" width="{cs - 4}" height="{cs - 4}" rx="6" '
                 f'fill="{fill}" fill-opacity="{0.08 + 0.8 * a_:.2f}"{tipattr(tp)}/>')
        g.append(T(hx0 + j * cs + cs / 2, hy0 + i * cs + cs / 2 + 9, lab, 24, fill=INK if a_ < 0.6 else "#fff", weight=600))
hm = svg(hx0 + n * cs + 10, hy0 + n * cs + 10, "".join(g), "material pair matrix")
al = inv.get("Al", 0)
body = title(f"Aluminium is in {100 * al:.0f}% of the accidental pairs",
             f"Share of the accidental background ({T_G1}, {T_SIPM2}, {T_ESUM}, 60–180°) with at least one single from each {T_CAPVOL}.")
body += f'''
<div style="display:flex;gap:56px;align-items:start">
<div style="display:flex;flex-direction:column;gap:14px;width:900px"><p style="font-size:26px;font-weight:600">By source (a pair counts for both its singles)</p>{hbs}
<div style="height:16px"></div>
{sd.callout(f"The <b>8 mm Al upstream end cap and ring</b> alone is in {100 * inv_src.get('Al cell end caps + ring', 0):.0f}% of pairs. It is the same cap that shadows backward leptons (slides 15–16), so lining or trimming it helps twice.", ORANGE, 25)}</div>
<div style="display:flex;flex-direction:column;gap:10px"><p style="font-size:26px;font-weight:600">By material pair (sums to 100%)</p>{hm}</div></div>'''
top = sorted(((k, v) for k, v in pm.items() if k[0] <= k[1]), key=lambda kv: -kv[1])[:6]
toprows = "".join(f"<tr><td>{a} × {b}</td><td>{100 * v:.1f}%</td></tr>" for (a, b), v in top)
srows = "".join(f"<tr><td>{k}</td><td>{s['material']}</td><td>{s['rate_per_arm']:.2g}</td><td>{s['hard_rate_per_arm']:.2g}</td><td>{100 * inv_src.get(k, 0):.1f}%</td></tr>"
                for k, s in sorted(sing.items(), key=lambda kv: -inv_src.get(kv[0], 0)))
g5 = ""
if AJ5:
    g5 = (f"<p>G5 (3 bar, R 40, Kapton) for comparison: Al {100 * AJ5['involvement_material'].get('Al', 0):.0f}%, "
          f"air {100 * AJ5['involvement_material'].get('air (¹⁴N)', 0):.0f}%, Cu {100 * AJ5['involvement_material'].get('Cu', 0):.0f}%, "
          f"Be {100 * AJ5['involvement_material'].get('Be', 0):.0f}%.</p>")
sec("acc_sources", body,
    f"<p>Each accidental pair is two singles; each single is labelled by the capture volume of its neutron. The bars count a pair once for each of its sources, so they add to more than 100%. The matrix splits the background exactly (the cells sum to 100%).</p>"
    f"<p>The Al cell end cap and ring is the 8 mm upstream cap already suspected of shadowing backward leptons (vertex and radius slides), so trimming or lining it would help twice.</p>"
    "<p>'other' in the matrix includes ³He(n,γ) singles (C1g), which are &lt; 1% of the pairs.</p>"
    f"<table><tr><th>material pair</th><th>share</th></tr>{toprows}</table>"
    f"<table><tr><th>source</th><th>material</th><th>singles /arm/n</th><th>&gt; 6 MeV /arm/n</th><th>in pairs</th></tr>{srows}</table>{g5}"
    "<p>Command: <code>python3 sim/lxplus/acc_sources.py --cfg G1 -o acc_sources_G1.json</code> on lxplus (reads /eos/experiment/ntof/data/x17/ill/contracts).</p>",
    foot="C1 + C1w (+ C1g for ³He(n,γ)) singles, paired exactly as in sim_feasibility. Labels are capture volumes, not traced particles.")

# ---- D: how well the MC knows it
st_rows = [(k, s) for k, s in sorted(sing.items(), key=lambda kv: -kv[1]["hard_rate_per_arm"]) if s["hard_raw"] > 0]
st = []
for k, s in st_rows:
    tp = (f"{k}: {s['hard_rate_per_arm']:.2g} singles > 6 MeV per arm per n\n"
          f"{s['hard_raw']} raw MC rows, n_eff = {s['hard_neff']:.1f}, {100 * s['hard_from_biased']:.0f}% of the weight from the biased run C1w")
    st.append((k, s["hard_rate_per_arm"], MCOL.get(s["material"], "#9aa1ad"), tp,
               f"<span style='white-space:nowrap'>n_eff {s['hard_neff']:.0f} ({s['hard_raw']} raw)</span>"))
sbars = sd.hbars(st, vmax=3e-8, vmin=1e-12, log=True, width=340, h=46, label_w=330, size=25,
                 fmt=lambda v: sci(v, 1))
cu = sing.get("Cu (PCB, cathode, mesh)", {})
i5 = AJ5["involvement_material"] if AJ5 else {}
G5TXT = (f"G1: Al {100 * inv['Al']:.0f}%, air {100 * inv['air (¹⁴N)']:.0f}%. G5 (independent MC): Al {100 * i5.get('Al', 0):.0f}%, "
         f"air {100 * i5.get('air (¹⁴N)', 0):.0f}%." if AJ5 else "")
CU5 = f"; in G5 it is {100 * i5.get('Cu', 0):.0f}%" if AJ5 else ""
alc = sing.get("Al cell end caps + ring", {})
T_NEFF = term("effective MC events", "n_eff = (Σw)² / Σw² over the weighted MC rows: the number of unweighted events with the same statistical power.")
body = title("The ranking is solid; the split rests on few MC events",
             f"Rate of hard singles (> 6 MeV in one arm) per arm per absorbed neutron, and the {T_NEFF} behind each.")
body += f'''
<div style="display:flex;gap:48px;align-items:start">
<div style="width:1080px">{sbars}</div>
<div style="display:flex;flex-direction:column;gap:20px;width:540px">
{card(f'<p style="font-size:25px;line-height:1.35"><b>Robust:</b> Al and air ¹⁴N carry it. {G5TXT}</p>', pad=26)}
{card(f'<p style="font-size:25px;line-height:1.35"><b>Not robust:</b> Cu’s {100 * inv.get("Cu", 0):.0f}% in G1 is {cu.get("hard_raw", 0)} event{CU5}. Treat every share as ±×2.</p>', pad=26)}
{card('<p style="font-size:25px;line-height:1.35"><b>Cheap fix:</b> a γ-source run with each material’s capture lines, thrown from its volumes, or C1w with the bias on the frames.</p>', bg="#eef3fa", pad=26)}
</div></div>'''
sec("acc_stats", body,
    "n_eff = (Σw)² / Σw² over the MC rows with a single above 6 MeV, by source. The accidental tail above 13 MeV is carried entirely by these rare hard singles (every passing pair has one member above half the cut), so the attribution inherits their statistics. "
    "C1 is analog (10⁸ primaries per cell); C1w biases the cell walls ×300, the 8 mm Al and ⁶LiF ×20 and the air ×100. The frames, flange and Cu sit in the detector and were not biased, which is why they have so few events. "
    "A targeted run would fix this: throw each material's capture γ cascade (Al, ¹⁴N, Cu, Be) isotropically from its volumes, weighted by the capture rates in the accounting (these are well known: ~10⁴ per 10⁸ per volume), and measure the per-arm hard-single probability directly.",
    foot="6 MeV is a diagnostic threshold, not a cut. Bars on a log scale.")

# ---- E: what removing each would buy
rem = [("none", "as simulated"), ("Al", "no Al"), ("air (¹⁴N)", "no air"), ("Cu", "no Cu"),
       ("Be", "no Be"), ("Al + air", "no Al + air")]
rem = [(k, lab) for k, lab in rem if k in rch]
R = sd.Plot(980, 560, x=(-0.5, len(rem) - 0.5), y=(0, 0.01), ylabel="3σ reach, X17 / IPC(M1) [10⁻³]", margin=(30, 130, 110, 100))
R.yticks([(v, f"{v * 1e3:.0f}") for v in (0, 0.002, 0.004, 0.006, 0.008, 0.010)])
R.hline(R_FLOOR, MUT, tip="Statistics floor 4.4×10⁻³: only IPC in the fit, no cosmics, no accidentals.")
R.raw(T(R.x0 + R.pw + 10, R.Y(R_FLOOR) - 4, "IPC-only", 20, fill=MUT, anchor="start"))
R.raw(T(R.x0 + R.pw + 10, R.Y(R_FLOOR) + 20, "floor", 20, fill=MUT, anchor="start"))
for i, (k, lab) in enumerate(rem):
    d = rch[k]
    col = C["acc"] if k == "none" else MCOL.get(k, ORANGE if "Al" in k else MUT)
    tp = (f"{lab}: 3σ reach {sci(d['reach3'], 2)} at {d['R']:.2g} n/s\naccidentals {d['acc']:,.0f}, cosmics {d['cos']:,.0f}, "
          f"IPC {d['ipc']:,.0f} per cycle (60–180°)")
    R.vbar(i, d["reach3"], 110, col, tip=tp, label=f"{d['reach3'] * 1e3:.1f}")
    R.raw(T(R.X(i), R.y0 + R.ph + 34, lab, 22, fill=INK))
rsv2 = R.svg("reach with one material's singles removed")
ral = rch.get("Al", rch["none"])
body = title(f"Without the Al singles: reach {r_now * 1e3:.1f} → {ral['reach3'] * 1e3:.1f} ×10⁻³",
             f"3σ reach per cycle, {T_G1}, 200 ps + μ veto, best rate each. Oracle: all singles from that material removed.")
body += f'''
<div style="display:flex;gap:44px;align-items:start">{rsv2}
<div style="display:flex;flex-direction:column;gap:18px;width:640px">
{card(f'<p style="font-size:25px;line-height:1.35"><b>Line the Al that sees neutrons</b> with ⁶LiF (⁶Li(n,t): no γ) or B₄C (0.48 MeV γ). The upstream end cap is the priority, and trimming it also recovers acceptance.</p>', pad=24)}
{card(f'<p style="font-size:25px;line-height:1.35"><b>He or vacuum flight tube</b> on the 30 cm beam air path, where ~90% of the ¹⁴N captures happen. Removes the ¹⁴N line and widens the 1-neutron energy margin.</p>', pad=24)}
{card(f'<p style="font-size:25px;line-height:1.35"><b>Timing still pays</b>: accidentals fall as 2τ whatever their source.</p>', pad=24)}
</div></div>'''
rtab = "".join(f"<tr><td>{lab}</td><td>{sci(rch[k]['reach3'], 2)}</td><td>{rch[k]['R']:.2g}</td><td>{rch[k]['acc']:,.0f}</td><td>{rch[k]['ipc']:,.0f}</td></tr>"
               for k, lab in rem)
rb = AJ["reach"].get("baseline", {})
r5 = AJ5["reach"]["timing"] if AJ5 else {}
g5tab = "".join(f"<tr><td>{lab}</td><td>{sci(r5[k]['reach3'], 2)}</td><td>{r5[k]['acc']:,.0f}</td></tr>" for k, lab in rem if k in r5)
btab = "".join(f"<tr><td>{lab}</td><td>{sci(rb[k]['reach3'], 2)}</td></tr>" for k, lab in rem if k in rb)
sec("acc_fix", body,
    "<p>Each bar re-runs the sim_feasibility model with the accidental histogram minus every pair that involves the removed material, then re-optimises the rate. "
    "It is an oracle: a real lining reduces those captures by a large factor but not to zero, and a liner adds its own (soft) lines.</p>"
    f"<table><tr><th>200 ps + μ veto</th><th>3σ reach</th><th>best R [n/s]</th><th>accidentals</th><th>IPC</th></tr>{rtab}</table>"
    f"<p>For today's design (σt 0.5 ns, no veto) cosmics dominate, so removing materials barely moves it:</p><table><tr><th>today</th><th>3σ reach</th></tr>{btab}</table>"
    f"<p>G5 (3 bar, R 40, Kapton), same design: air leads there, so removing air helps more than removing Al.</p><table><tr><th>G5, 200 ps + μ veto</th><th>3σ reach</th><th>accidentals</th></tr>{g5tab}</table>"
    "<p>The model here reproduces the reach in FEASIBILITY_SIM to rounding (8.4×10⁻³, from <code>variants_v3.csv</code>); small differences come from the rate grid.</p>",
    foot="sim/lxplus/acc_sources.py (G1, sipm2, Esum > 13 MeV); shares carry the ±×2 statistical caveat of the previous slide.")

# =========================================================================== 10 vertices
w, h = 1040, 600
x0, pw = 70, 940
ymin_, ymax_ = -60, 300
xm = lambda v: x0 + (v - ymin_) / (ymax_ - ymin_) * pw
zc, zs = 300, 0.95   # mm -> px vertical
zm = lambda z: zc - z * zs
g = []
g.append(f'<rect x="{xm(-180):.1f}" y="{zm(240):.1f}" width="{xm(180)-xm(-180):.1f}" height="{20*zs:.1f}" fill="{MUT}" opacity="0.55"/>')
g.append(f'<rect x="{xm(-180):.1f}" y="{zm(-220):.1f}" width="{xm(180)-xm(-180):.1f}" height="{20*zs:.1f}" fill="{MUT}" opacity="0.55"/>')
g.append(T(xm(0), zm(240) - 10, "Micromegas arm, active ±180 mm (z = ±224 mm)", 21, fill=MUT))
# cells
for (yw, L, col, lab) in [(-21.6, 300, ORANGE, "G1: 1 bar, 300 mm"), (-7.2, 100, BLUE, "G5: 3 bar, 100 mm")]:
    g.append(f'<rect x="{xm(yw):.1f}" y="{zm(40):.1f}" width="{xm(yw+L)-xm(yw):.1f}" height="{80*zs:.1f}" fill="none" stroke="{col}" stroke-width="2.5" rx="3"/>')
g.append(f'<rect x="{xm(-60):.1f}" y="{zm(10):.1f}" width="{xm(-21.6)-xm(-60):.1f}" height="{20*zs:.1f}" fill="{BLUE}" opacity="0.15"/>')
g.append(T(xm(-58), zm(10) - 8, "beam", 20, fill=BLUE, anchor="start"))
# densities (normalised peak) drawn above axis line z=0 band
for p, yw, col in [(1.0, -21.6, ORANGE), (3.0, -7.2, BLUE)]:
    s = depth[depth.p_bar == p]
    yy = s.depth_cm.values * 10 + yw; pdf = s.pdf_per_cm.values
    sel = yy <= 300
    amp = 70 / depth[depth.p_bar == 3.0].pdf_per_cm.max()
    zz = -120 + pdf[sel] * amp
    xs = [xm(a) for a in yy[sel]]; ys = [zm(b) for b in zz]
    g.append(poly([xm(yy[sel][0])] + xs + [xs[-1]], [zm(-120)] + ys + [zm(-120)], None, fill=col).replace('fill="', 'opacity="0.35" fill="'))
    g.append(poly(xs, ys, col, 3))
g.append(f'<line x1="{xm(-60):.1f}" y1="{zm(-120):.1f}" x2="{xm(300):.1f}" y2="{zm(-120):.1f}" stroke="{MUT}" stroke-width="1.5"/>')
g.append(T(xm(175), zm(-95), "vertex density along the beam (common scale)", 21, fill=INK))
g.append(T(xm(200), zm(40) - 8, "G1 cell", 20, fill=ORANGE, weight=700))
g.append(T(xm(60), zm(40) - 8, "G5 cell", 20, fill=BLUE, weight=700))
for v in (-50, 0, 50, 100, 150, 200, 250, 300):
    g.append(T(xm(v), zm(-120) + 30, str(v), 20))
g.append(T(xm(120), zm(-120) + 58, "position along the beam y [mm] (0 = detector centre)", 21, fill=INK))
vs = svg(w, h, "".join(g), "side view with vertex distributions")
# acceptance vs y
acc = {}
edges = np.arange(-60, 301, 5)
for cfg, p, yw in (("G1", 1.0, -21.6), ("G5", 3.0, -7.2)):
    s = depth[depth.p_bar == p]
    cdf = np.interp((edges - yw) / 10, s.depth_cm, s.cdf, left=0, right=1)
    pg = np.diff(cdf) * X[cfg + "_N"]; a = np.array(X[cfg + "_vy_acc_hist"])
    acc[cfg] = np.where(pg > 15000, a / np.maximum(pg, 1), np.nan)
w2, h2 = 560, 600
ax0, ay0, apw, aph = 90, 30, 440, 440
axm = lambda v: ax0 + (v + 30) / 210 * apw
aym = lambda v: ay0 + aph - v / 0.045 * aph
o = [axes(ax0, ay0, apw, aph, [(v, str(v)) for v in (0, 50, 100, 150)], [(v, f"{v*100:.0f}%") for v in (0, 0.01, 0.02, 0.03, 0.04)],
          "vertex y [mm]", "X17 acc × ε", axm, aym)]
cen = 0.5 * (edges[1:] + edges[:-1])
for cfg, col in (("G1", ORANGE), ("G5", BLUE)):
    ok = np.isfinite(acc[cfg]) & (cen <= 180)
    o.append(poly([axm(v) for v in cen[ok]], [aym(v) for v in acc[cfg][ok]], col, 3.5))
o.append(T(axm(95), aym(0.012), "dip just behind the window:", 20, fill=INK))
o.append(T(axm(95), aym(0.012) + 26, "backward leptons hit the", 20, fill=INK))
o.append(T(axm(95), aym(0.012) + 52, "8 mm Al upstream cap", 20, fill=INK))
asv = svg(w2, h2, "".join(o), "acceptance vs vertex position")
body = title("Pairs are born in a Ø2 cm pencil, a few cm long",
             "Side view to scale. Every neutron is absorbed in the gas; pressure sets the depth, the beam spot sets the width.")
body += f'''
<div style="display:flex;gap:24px;align-items:start">{vs}{asv}</div>'''
slides["vertex"] = sec("vertex", body,
    "Depth PDFs from cell_depth.csv, validated by V0 (Geant median depth 2.16/1.08/0.72 cm at 1/2/3 bar vs analytic, identical). Along the beam the vertex sigma is 43 mm at 1 bar and 14 mm at 3 bar; across, r50/r90 = 7/10 mm in every configuration (the beam spot plus penumbra), independent of the cell radius. The cell is placed so the median vertex is at y=0. Acceptance vs vertex y is the accepted S1 X17 count (sipm2, Esum>12) divided by the generated count expected from the depth PDF. The dip in the first ~15 mm behind the window is consistent with backward-going leptons being blocked by the 8 mm Al upstream end cap and ring. That is an inference, not traced in the MC.",
    foot="G1 orange, G5 blue. Acceptance = accepted S1 X17 / vertices expected from the validated depth PDF.")

# =========================================================================== 11 radius
accs = {g_: X[f"{g_}_acc"] for g_ in ("G1", "G2", "G3", "G4", "G5", "G6")}
CELLS = dict(G1="1 bar, R 40 mm, mylar", G2="1 bar, R 100 mm, mylar", G3="2 bar, R 40 mm, Kapton",
             G4="2 bar, R 100 mm, Kapton", G5="3 bar, R 40 mm, Kapton", G6="3 bar, R 100 mm, Kapton")
def accbar(g_, col):
    v = accs[g_]; hpx = v / 0.035 * 360
    tp = f"{g_} ({CELLS[g_]}): X17 acc × ε {100 * v:.2f}% (sipm2, Esum > 12 MeV)"
    return (f'<div{tipattr(tp)} style="display:flex;flex-direction:column;align-items:center;gap:8px;width:110px"><p style="font-family:{MONO};font-size:24px">{100*v:.1f}%</p>'
            f'<div style="width:72px;height:{hpx:.0f}px;background:{col};border-radius:6px 6px 0 0"></div><p style="font-size:24px;font-weight:600">{g_}</p></div>')
grp = ""
for p_, a_, b_ in (("1 bar", "G1", "G2"), ("2 bar", "G3", "G4"), ("3 bar", "G5", "G6")):
    grp += (f'<div style="display:flex;flex-direction:column;align-items:center;gap:8px"><div style="display:flex;align-items:end;gap:8px;height:430px">'
            f'{accbar(a_, BLUE)}{accbar(b_, "#9db7d8")}</div><p style="font-size:24px;color:{MUT}">{p_}</p></div>')
# ratio G2/G1 vs cos
c1 = np.array(X["G1_lep_cosy_acc_hist"], float); c2 = np.array(X["G2_lep_cosy_acc_hist"], float)
ce = np.linspace(-1, 1, 21); cc = 0.5 * (ce[1:] + ce[:-1])
rat = np.where(c1 > 500, c2 / np.maximum(c1, 1) / (c2.sum() / c1.sum()) * (accs["G2"] / accs["G1"]), np.nan)
w, h = 700, 380
x0, y0, pw, ph = 100, 20, 560, 250
xm = lambda v: x0 + (v + 1) / 2 * pw
ym = lambda v: y0 + ph - (v - 0.4) / 0.7 * ph
o = [axes(x0, y0, pw, ph, [(v, f"{v:g}") for v in (-1, -0.5, 0, 0.5, 1)], [(v, f"{v:.1f}") for v in (0.4, 0.6, 0.8, 1.0)],
          "lepton cos θ to the beam (−1 = backward)", "R100 / R40", xm, ym)]
o.append(f'<line x1="{xm(-1)}" y1="{ym(1):.1f}" x2="{xm(1)}" y2="{ym(1):.1f}" stroke="{MUT}" stroke-dasharray="6 5" stroke-width="1.5"/>')
ok = np.isfinite(rat)
o.append(poly([xm(v) for v in cc[ok]], [ym(v) for v in rat[ok]], BLUE, 4))
o.append(T(xm(-0.45), ym(0.5), "backward leptons lost", 21, fill=INK))
rsv = svg(w, h, "".join(o), "G2/G1 accepted lepton ratio")
body = title("Radius changes acceptance, not the vertex",
             "X17 acc × ε (sipm2, Esum > 12 MeV). The vertex is the same Ø2 cm pencil in every cell.")
body += f'''
<div style="display:flex;gap:56px;align-items:start">
<div style="display:flex;flex-direction:column;gap:12px"><div style="display:flex;gap:40px">{grp}</div>{legend_row([("R = 40 mm", BLUE), ("R = 100 mm", "#9db7d8")])}</div>
<div style="display:flex;flex-direction:column;gap:20px;width:720px">{rsv}
<p style="font-size:26px;line-height:1.35"><b>R = 100 mm loses 20–25%</b>, nearly all in backward leptons, likely the larger upstream Al cap. It also needs 6× the ³He and a thicker wall.</p></div></div>'''
slides["radius"] = sec("radius", body,
    "Production per absorbed neutron does not depend on the radius: the cell is opaque, so every neutron is absorbed. The radius therefore changes only what reaches the arms. The ratio plot compares the accepted-lepton polar-angle distributions of G2 (R100) and G1 (R40), normalised to the overall acceptance ratio; the loss sits at cos theta between -0.8 and -0.2. Small R is not needed to fix the vertex: the transverse vertex is the beam spot, the longitudinal one is the absorption depth, and an ideal vertex buys only ~13% in reach anyway.",
    foot="S1 (3.4×10⁶ X17 per cell). The upstream-cap explanation is inferred from the angle and depth dependence, not traced.")

# =========================================================================== n_TOF hardware (FEASIBILITY_SIM §10)
CONS = ILL / "sim/analysis_v3/cons"
def creach(f, hw, endcap=False):
    d = pd.read_csv(CONS / f"{f}.csv")
    return float(d[(d.hw == hw) & (d.endcap_off == endcap)].reach3.iloc[0])
HW_V, HW_NV = "nTOF 5 ns + veto, per-arm coinc (strict)", "nTOF 5 ns, no veto, strict"
lad = [("n_TOF hardware, ceiling panel", creach("noseg_G1", HW_V), C["cos"],
        "~5 ns per arm (7 ns on Δt), per-arm SiPM × plastic trigger, DREAM live time, panel inefficiency 10⁻². No Micromegas condition."),
       ("+ MM segments 3°, D < 30 mm", creach("coll_3_30_0_c0", HW_V), MUT,
        "Each arm's Micromegas segment must point back to within 30 mm of the beam axis. Accidentals fall ~20×, cosmics ~7×."),
       ("collinearity 20° instead of panel", creach("coll_3_30_0_c20", HW_NV), MUT,
        "No ceiling panel. Events whose two segments lie within 20° of one straight line (a through-going muon) are vetoed. Costs ~8% of the X17."),
       ("+ CFRP ring and upstream cap", creach("ringCFRP_3_30_np", HW_NV), BLUE,
        "The Al ring and upstream cap made of CFRP: upstream-cap captures 1.7→0.6×10⁻⁴ per n; the best rate rises 1.2→1.9×10¹⁰ n/s."),
       ("… and keep the panel too", creach("ringCFRP_3_30_np", HW_V), BLUE,
        "Panel + collinearity 20° + CFRP. The panel removes cosmics the collinearity veto misses (~10% gain)."),
       ("Al + ⁶LiF gas-side liner (no panel)", creach("ringLiF_3_30_np", HW_NV), "#b0b6c0",
        "No gain: the liner does not shield the upstream cap from neutrons arriving from outside, and the liner region itself adds some accidentals."),
       ("200 ps + panel (slide 1 design)", R_GOOD, "#b0b6c0", "The original requirement, without segments, for comparison.")]
sc = 1000 / 0.055
rr = []
for n, v, col, tp in lad:
    rr.append(f'''<div{tipattr(f"{n}: 3σ reach {sci(v, 2)} ({v / 0.025:.2f} × the reference ratio)\\n{tp}")} style="display:flex;align-items:center;gap:20px;height:60px">
<p style="width:560px;flex-shrink:0;font-size:27px;text-align:right">{n}</p>
<div style="display:flex;align-items:center;gap:14px"><div style="width:{v*sc:.0f}px;height:38px;background:{col};border-radius:5px"></div>
<p style="font-family:{MONO};font-size:26px;white-space:nowrap;background:{BG};padding:0 6px;position:relative;z-index:1">{sci(v)}</p></div></div>''')
xref = 580 + 0.025 * sc
body = title("n_TOF hardware is enough once the Micromegas segments are used",
             f"3σ reach per 50-day cycle, {T_G1}, Esum &gt; 13 MeV offline, best rate per row. Each step adds to the one above. Lower is better.")
body += f'''
<div style="position:relative;width:1664px;height:500px">
<div style="position:absolute;left:{xref:.0f}px;top:30px;width:3px;height:460px;background:{ORANGE};opacity:0.7"></div>
<p style="position:absolute;left:{xref-210:.0f}px;top:-6px;width:420px;text-align:center;font-size:24px;color:{ORANGE}">reference ratio 2.5×10⁻²</p>
<div style="position:absolute;left:0px;top:46px;width:1664px;display:flex;flex-direction:column;gap:2px">{"".join(rr)}</div>
</div>
{sd.callout("Bench Micromegas resolution is &lt; 3°, so the 3° rows apply. At 5° the collinearity veto falls 10–20% behind the panel. MC uncertainty ~15%: estimating the biased volumes from the biased run alone moves these values by 13–19%.", ORANGE, 25)}'''
slides["ntof_hw"] = sec("ntof_hw", body,
    "FEASIBILITY_SIM.md §10; CSVs sim/analysis_v3/cons/ (noseg_G1, coll_3_30_0_c*, ringCFRP/ringLiF/base_3_30_np). Driver sim/lxplus/conservative.py. "
    "Timing: n_TOF SiPM wall ~5 ns per arm, |Δt| < 2.5σ_Δt, accidental window equal to the cut. Trigger: two arms each with SiPM × plastic coincidence, ~40–200 Hz, DREAM live time 1/(1 + f·298 µs) ≈ 0.94–0.99. "
    "Segments: dominant-track line fit per arm, direction smeared by 3°, must pass within 30 mm of the beam axis inside the cell; X17 keeps ~81–85% even with perfect direction because of scattering in the MM window. "
    "Segments also make 200 ps unnecessary: with segments and the panel, 1/2/5 ns give 8.7e-3/9.7e-3/1.1e-2 with the end cap off.",
    foot="End-cap variants: 10⁸ n each (narrow C1 + wide-halo C1w), Geant branch ill_ring.")

# =========================================================================== what blocks us (FEASIBILITY_SIM §11)
def bud(f, scen, hw=HW_NV):
    d = pd.read_csv(CONS / f"{f}.csv")
    return float(d[(d.hw == hw) & (d.scenario == scen)].reach3.iloc[0])
lad2 = [("CFRP design as is", bud("bo_ringCFRP", "as is"), C["acc"],
         "n_TOF hardware, 3° segments, collinearity 20°, CFRP end cap, no panel, Esum > 13 MeV. Accidentals 7.6k, cosmics 10k, IPC 5.4k per cycle.",
         "Accidentals are Be window + air only"),
        ("− air (¹⁴N, 10.8 MeV)", bud("bo_ringCFRP", "no air"), C["acc"],
         "All captures in air removed: a He or vacuum flight tube on the beam path (he4_bag study).", "He / vacuum flight tube"),
        ("− Be window (6.8 MeV)", bud("bo_ringCFRP", "no Be window + air"), C["acc"],
         "Be window captures removed too: accidentals 7.6k → 45. Partial versions: a thinner window (Be×Be pairs ∝ t²) or Esum > 14 MeV, above the Be×Be endpoint 13.6 MeV (−16% X17).",
         "thinner window, or Esum > 14"),
        ("− cosmics", bud("e13", "no Be window + air", HW_V), C["cos"],
         "The ceiling panel takes the ~10k cosmics that leak through segments + collinearity down to ~100.", "ceiling panel"),
        ("IPC only: the floor", bud("bo_ringCFRP", "oracle: IPC only"), C["ipc"],
         "Only M1 + E0 pairs left: the same nuclear transition. Statistics only, ∝ 1/√(exposure × X17 efficiency).", "physics: same transition")]
sc2 = 1000 / 0.0155
rr = []
for n, v, col, tp, how in lad2:
    rr.append(f'''<div{tipattr(f"{n}: 3σ reach {sci(v, 2)}\\n{tp}")} style="display:flex;align-items:center;gap:20px;height:64px">
<p style="width:380px;flex-shrink:0;font-size:27px;text-align:right">{n}</p>
<div style="width:{v*sc2:.0f}px;height:40px;background:{col};border-radius:5px;flex-shrink:0"></div>
<p style="font-family:{MONO};font-size:26px;white-space:nowrap;width:120px;flex-shrink:0">{sci(v)}</p>
<p style="font-size:24px;color:{MUT}">{how}</p></div>''')
body = title("What blocks us: two materials on the beam path, then cosmics, then physics",
             f"3σ reach per cycle, CFRP design, {T_G1}, Esum &gt; 13 MeV. Each row removes one more background. Lower is better.")
body += f'''<div style="display:flex;flex-direction:column;gap:4px">{"".join(rr)}</div>
<div style="display:flex;gap:32px">
{card(f"<p style='font-size:25px;line-height:1.38'><b>Accidentals are not irreducible.</b> After the segment cut and the CFRP cap, 99% come from captures in the <b>Be entrance window</b> and the <b>air</b> in front of the cell. They sit on the beam axis, so pointing cannot reject them. Both can be engineered away.</p>")}
{card(f"<p style='font-size:25px;line-height:1.38'><b>The floor is IPC statistics.</b> The only levers left: X17 efficiency (the stack holds ~40% of the energy), more cycles, and <b>spin selection</b>. E0 pairs are ~60% of the IPC after cuts and come only from the singlet; polarised beam + ³He suppress them.</p>", bg="#eef3fa")}
</div>'''
slides["blocking"] = sec("blocking", body,
    "FEASIBILITY_SIM.md §11; conservative.py --budget --biased-only (CSVs bo_ringCFRP, e13). Capture sources are removed by zeroing the weight of every neutron captured there; oracles zero a background class in the fit. "
    "Volumes biased in C1w (cell walls ×300, end parts ×20, air ×100) are estimated from C1w alone; this moves the reaches 13–19% relative to the plain C1+C1w pool (as is: 1.39e-2 vs 1.23e-2 on the n_TOF hardware slide), which is the size of the MC uncertainty. "
    "Removing Be + air lands slightly below the no-accidentals oracle because the trigger rate also drops (more live time). The last two rows are equal within that effect. "
    "Esum scan with the panel: 13 / 13.5 / 14 / 15 MeV give 1.18 / 1.08 / 1.01 / 0.99e-2 as is.",
    foot="Same rows with the plain C1+C1w pool: as is 1.2×10⁻², without Be + air 8.3×10⁻³ (unchanged).")

# =========================================================================== 12 next
nx = [("1", "Confirm ≤ 3° Micromegas segments on muons", "The bench says &lt; 3°. At ≤ 3° the segment cut plus a 20° collinearity veto replaces both 200 ps and the ceiling panel (n_TOF hardware slide)."),
      ("2", "CFRP ring and upstream cap", "Replaces the 8 mm Al cap: 80–90% of the gain of removing it entirely. A gas-side ⁶LiF liner does not help. A He tube on the beam path removes air ¹⁴N."),
      ("3", "He flight tube; Esum &gt; 14 MeV", "With CFRP, the accidentals are the air (¹⁴N) and the Be window only (What blocks us slide). A He/vacuum tube removes the first; Esum &gt; 14 kills Be×Be pairs."),
      ("4", "Calorimeter geometry run", "The stack holds 40% of the energy and Esum keeps 25% of X17. Containment could give ×4 signal."),
      ("5", "Optional: faster timing, ceiling panel", "Each gains ~10–20% on top of the n_TOF design; needed only if the segment resolution comes out worse than ~3°.")]
items = "".join(f'''<div style="display:flex;gap:28px;align-items:start;padding:20px 0;border-top:1px solid #333b4a">
<p style="font-family:{MONO};font-size:44px;font-weight:600;color:#6aa6e8;width:60px;flex-shrink:0">{n}</p>
<div style="display:flex;flex-direction:column;gap:6px"><p style="font-size:34px;font-weight:600">{a}</p><p style="font-size:26px;color:{DMUT}">{b}</p></div></div>''' for n, a, b in nx)
body = f'<h2 style="font-size:60px;font-weight:600;line-height:1.1">Next steps, cheapest first</h2>\n<div style="display:flex;flex-direction:column">{items}</div>'
slides["next"] = sec("next", body, "Still open from README: the thermal X17 rate itself (ask Viviani/Marcucci/Schiavilla for E_n < 10 eV), and the site background in the PF1B casemate.", dark=True)

order = ["cover", "reach_what", "reach_atomki", "reach_verdict", "funnel", "leftover", "angle", "timing", "levers", "angle_cos", "collinear", "panels",
         "acc_what", "acc_lines", "acc_sources", "acc_stats", "acc_fix", "vertex", "radius", "ntof_hw", "blocking", "next"]
SHORT = dict(cover="Answer", reach_what="What reach means", reach_atomki="vs ATOMKI", reach_verdict="Verdict", funnel="One cycle", leftover="What is left", angle="Spectra", timing="Why 200 ps",
             levers="Levers", angle_cos="Muon fakes", collinear="Collinearity veto", panels="Veto panels",
             acc_what="Accidentals", acc_lines="Capture lines", acc_sources="Al sources", acc_stats="MC statistics",
             acc_fix="Removing Al", vertex="Vertices", radius="Radius", ntof_hw="n_TOF hardware", blocking="What blocks us", next="Next steps")
for k in order:
    (SL / f"{k}.html").write_text(sec(k, *SEC[k]))
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-02T12:00:00Z"}, "lists": "css", "title": "ILL X17 Feasibility",
        "order": order, "cover": "cover",
        "sections": {"s1": {"description": "The answer and the statistics", "start": "cover"},
                     "s2": {"description": "Why timing matters and how to kill cosmics", "start": "timing"},
                     "s3a": {"description": "Where the accidentals come from", "start": "acc_what"},
                     "s3": {"description": "Where the pairs are born; the target radius", "start": "vertex"},
                     "s5": {"description": "Update 7 Oct: n_TOF hardware, segments, end cap", "start": "ntof_hw"},
                     "s4": {"description": "Next steps", "start": "next"}},
        "faces": {"ibm-plex-sans": {"family": "IBM Plex Sans", "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&display=swap"},
                  "ibm-plex-mono": {"family": "IBM Plex Mono", "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap"}},
        "designSystems": []}
(OUT / "deck.json").write_text(json.dumps(deck, indent=1))
for k in order:
    print(k, len((SL / f"{k}.html").read_text()))


# --------------------------------------------------------------------------- standalone HTML (slidedoc)
D = sd.Deck("ILL X17 Feasibility",
            "Overnight ILL Geant4 campaign in slides: reach, statistics, why 200 ps timing, cosmic vetoes "
            "(panels, segment collinearity), where the accidentals come from (Al), vertex and cell radius.")
for k in order:
    body, notes, dark, foot = SEC[k]
    D.slide(k, body, notes, dark=dark, foot=foot, short=SHORT[k])
D.write(ILL / "out" / "feasibility_deck.html", note_meta=dict(
    title="ILL X17 feasibility: the Geant4 campaign in slides",
    summary="Reach, event statistics, why 200 ps timing, cosmic vetoes (ceiling panel, segment collinearity), "
            "where the accidentals come from (aluminium), vertex and cell radius.",
    tags="X17,ILL,simulation", date="2026-10-02"),
    footer="Built by x17_facility_search/ill/deck/build_deck.py from the lxplus Geant4 campaign (sim/analysis_v3).")
print("wrote", ILL / "out" / "feasibility_deck.html")
