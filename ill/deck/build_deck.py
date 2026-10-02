"""Build the ILL X17 feasibility slide deck from the sim outputs.

Writes the Slides-artifact files to deck/build/project/ (deck.json + one
section per slide) and a standalone HTML version to out/feasibility_deck.html
(for dylan-neff.web.cern.ch/notes).  Inputs: sim/analysis_v3/ (spectra and
xtra_artifact.json from sim/lxplus/xtra_artifact.py) and out/cell_depth.csv.

    python ill/deck/build_deck.py
"""
import json, math
from pathlib import Path
import numpy as np, pandas as pd

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

def sec(id_, body, notes, dark=False, foot=None):
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

# =========================================================================== 1 cover
R_BASE, R_GOOD, R_FLOOR = 5.2e-2, 8.4e-3, 4.4e-3
def bignum(v, lab, col, note):
    return (f'<div style="flex:1;display:flex;flex-direction:column;gap:12px;border-top:4px solid {col};padding:28px 0 0 0">'
            f'<p style="font-family:{MONO};font-size:72px;font-weight:600;color:{col}">{v}</p>'
            f'<p style="font-size:30px;color:{DINK};line-height:1.3">{lab}</p>'
            f'<p style="font-size:24px;color:{DMUT};line-height:1.35">{note}</p></div>')
body = f'''<p style="font-size:26px;letter-spacing:3px;text-transform:uppercase;color:{DMUT}">ILL PF1B · Geant4 campaign G1–G6 · 2 Oct 2026</p>
<h1 style="font-size:88px;font-weight:600;line-height:1.08;letter-spacing:-2px;width:1500px">X17 at the ILL is feasible, but only with 200 ps timing and a cosmic veto</h1>
<div style="flex:1"></div>
<p style="font-size:28px;color:{DMUT}">3σ reach in X17 / IPC(M1), one 50-day cycle. The reference ratio is 2.5×10⁻².</p>
<div style="display:flex;gap:64px">
{bignum("5.2×10⁻²", "Today's design", "#e07a86", "σt 0.5 ns, no veto. Cosmics dominate; the reference ratio would be ~1.5σ.")}
{bignum("8.4×10⁻³", "200 ps + μ veto 10⁻²", "#6aa6e8", "Same cell (G1), ~10¹⁰ n/s. The reference ratio becomes a 6–9σ effect.")}
{bignum("4.4×10⁻³", "Pure IPC statistics", "#b9c1cc", "The floor if every non-IPC background vanished.")}
</div>'''
slides["cover"] = sec("cover", body, "Bottom line of the overnight campaign (FEASIBILITY_SIM.md). The limit is cosmic rays, not neutron backgrounds, lepton scattering or raw statistics. G1 = 1 bar, R 40 mm, 12 µm mylar cell; Esum > 13 MeV, sipm2 trigger menu.", dark=True)

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
    bars.append(f'''<div style="display:flex;align-items:center;gap:24px">
<p style="width:320px;font-size:28px;font-weight:600;text-align:right">{name}</p>
<div style="width:780px;display:flex;align-items:center;gap:16px"><div style="width:{wpx:.0f}px;height:44px;background:{col};border-radius:6px"></div>
<p style="font-family:{MONO};font-size:28px;font-weight:600;white-space:nowrap">{sci(v) if v > 1e4 else f"~{v:.0f}"}</p></div>
<p style="width:500px;font-size:24px;color:{MUT};line-height:1.25">{note}</p></div>''')
body = title("One cycle: 4×10¹⁶ neutrons → ~700 detected X17",
             "Per 50-day cycle at the optimum 0.9×10¹⁰ absorbed n/s (G1, 200 ps + veto). Bar length is log₁₀(count).")
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
def hb(v, col, alpha=1.0):
    w = 620 * (math.log10(v) - lo) / (hi - lo)
    return (f'<div style="display:flex;align-items:center;gap:12px"><div style="width:{w:.0f}px;height:34px;background:{col};opacity:{alpha};border-radius:5px"></div>'
            f'<p style="font-family:{MONO};font-size:26px;white-space:nowrap">{v:,}</p></div>')
rws = "".join(f'''<div style="display:flex;align-items:center;gap:24px;padding:10px 0;border-bottom:1px solid {RULE}">
<p style="width:260px;font-size:28px;font-weight:600;text-align:right">{n}</p>
<div style="width:760px">{hb(a, col, 0.45)}</div><div style="width:760px">{hb(b, col)}</div></div>''' for n, a, b, col in comp)
body = title("After cuts, cosmics outnumber X17 1000 to 1",
             "Expected events per 50-day cycle, G1, Esum > 13 MeV, at each design's best rate. Bars are log-scaled.")
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
    return svg(w, h, "".join(o), ttl)
body = title("X17 sits on the IPC tail; today cosmics bury it",
             "G1, sipm2, Esum > 12 MeV, one cycle. Same axes in both panels.")
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
    rr.append(f'''<div style="display:flex;align-items:center;gap:20px;height:52px">
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
def accbar(g_, col):
    v = accs[g_]; hpx = v / 0.035 * 360
    return (f'<div style="display:flex;flex-direction:column;align-items:center;gap:8px;width:110px"><p style="font-family:{MONO};font-size:24px">{100*v:.1f}%</p>'
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

# =========================================================================== 12 next
nx = [("1", "Measure Micromegas direction resolution on muons", "Cosmic bench, existing hardware. It decides whether the collinearity veto comes for free."),
      ("2", "200–300 ps per arm", "2 cm plastics with SiPMs at both bar ends. The single biggest lever."),
      ("3", "Ceiling veto panel, ~2 × 2 m", "Time-ordered, before the arms. Plus a reactor-off cosmic run for the template."),
      ("4", "Calorimeter geometry run", "The stack holds 40% of the energy and Esum keeps 25% of X17. Containment could give ×4 signal."),
      ("5", "Trim the upstream cap; add a He bag", "Recover the acceptance lost behind the window, and remove air ¹⁴N (2.7×10⁻⁴ per n).")]
items = "".join(f'''<div style="display:flex;gap:28px;align-items:start;padding:20px 0;border-top:1px solid #333b4a">
<p style="font-family:{MONO};font-size:44px;font-weight:600;color:#6aa6e8;width:60px">{n}</p>
<div style="display:flex;flex-direction:column;gap:6px"><p style="font-size:34px;font-weight:600">{a}</p><p style="font-size:26px;color:{DMUT}">{b}</p></div></div>''' for n, a, b in nx)
body = f'<h2 style="font-size:60px;font-weight:600;line-height:1.1">Next steps, cheapest first</h2>\n<div style="display:flex;flex-direction:column">{items}</div>'
slides["next"] = sec("next", body, "Still open from README: the thermal X17 rate itself (ask Viviani/Marcucci/Schiavilla for E_n < 10 eV), and the site background in the PF1B casemate.", dark=True)

order = ["cover", "funnel", "leftover", "angle", "timing", "levers", "angle_cos", "collinear", "panels", "vertex", "radius", "next"]
for k, v in slides.items():
    (SL / f"{k}.html").write_text(v)
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-02T12:00:00Z"}, "lists": "css", "title": "ILL X17 Feasibility",
        "order": order, "cover": "cover",
        "sections": {"s1": {"description": "The answer and the statistics", "start": "cover"},
                     "s2": {"description": "Why timing matters and how to kill cosmics", "start": "timing"},
                     "s3": {"description": "Where the pairs are born; the target radius", "start": "vertex"},
                     "s4": {"description": "Next steps", "start": "next"}},
        "faces": {"ibm-plex-sans": {"family": "IBM Plex Sans", "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&display=swap"},
                  "ibm-plex-mono": {"family": "IBM Plex Mono", "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap"}},
        "designSystems": []}
(OUT / "deck.json").write_text(json.dumps(deck, indent=1))
for k in order:
    print(k, len((SL / f"{k}.html").read_text()))


# --------------------------------------------------------------------------- standalone HTML
head = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ILL X17 Feasibility</title>
<meta name="description" content="Overnight ILL Geant4 campaign in slides: reach, statistics, why 200 ps timing, cosmic vetoes (panels, segment collinearity), vertex and cell radius.">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Mono:wght@400;600&display=swap">
<style>
:root{{color-scheme:light}}
body{{margin:0;background:#2a2f3a;font-family:{SANS};}}
.wrap{{max-width:1400px;margin:0 auto;padding:24px 16px 64px;display:flex;flex-direction:column;gap:28px}}
.frame{{position:relative;width:100%;aspect-ratio:16/9;overflow:hidden;border-radius:10px;box-shadow:0 6px 24px rgba(0,0,0,.35)}}
.frame>section{{position:absolute;left:0;top:0;width:1920px;height:1080px;box-sizing:border-box;transform-origin:0 0}}
section *{{margin:0;box-sizing:border-box}}
section table{{border-collapse:collapse;width:100%}}
section th,section td{{padding:.35em .6em;border-bottom:1px solid #d8d3c8;text-align:left}}
section th{{font-weight:600;border-bottom:2px solid #1c2230}}
section aside{{display:none}}
details{{color:#d6dae2;font-size:15px;line-height:1.5}} summary{{cursor:pointer;color:#a3abb9}}
</style></head><body><div class="wrap">
"""
import re
parts = []
for k in order:
    html = slides[k]
    m = re.search(r"<aside>(.*?)</aside>", html, re.S)
    note = m.group(1) if m else ""
    parts.append(f'<div class="frame">{html}</div>\n<details><summary>Notes</summary><p>{note}</p></details>')
tail = """</div><script>
function fit(){document.querySelectorAll('.frame').forEach(f=>{const s=f.firstElementChild;s.style.transform='scale('+(f.clientWidth/1920)+')';});}
addEventListener('resize',fit);fit();
</script></body></html>"""
(ILL / "out" / "feasibility_deck.html").write_text(head + "\n".join(parts) + tail)
print("wrote", ILL / "out" / "feasibility_deck.html")
