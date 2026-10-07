"""Extrapolate the §11 budget rows past R_MAX with a counting surrogate of the Fisher fit:
   (sigma*X17)^2 = a*(IPC+G) + b*ACC + c*COS, calibrated on oracle rows; then
   X17,IPC,G ∝ R*live*exp(-2kR); ACC ∝ R^2*live; COS ∝ live; live = 1/(1+f tau), f = pR + qR^2."""
import csv, math, sys
import numpy as np
D = str(__import__("pathlib").Path(__file__).resolve().parent / "analysis_v3" / "cons") + "/"
TAU = 298e-6
def rows(f, panel):
    out = {}
    for r in csv.DictReader(open(D + f)):
        isp = float(r["COS"]) < 1000 or r["scenario"].startswith("oracle: no c") and False
        out.setdefault(r["scenario"], []).append({k: (float(r[k]) if k not in ("hw", "scenario", "seg", "variant") else r[k]) for k in r if k not in ("biased_only",)})
    return out

def analyse(f, pick):
    rs = {}
    for r in csv.DictReader(open(D + f)):
        rs.setdefault(r["scenario"], []).append({k: float(r[k]) for k in ("best_R", "live", "trig_Hz", "reach3", "X17", "M1", "E0", "G", "ACC", "COS")})
    g = lambda s: rs[s][pick]
    ipc, nacc, ncos, asis = g("oracle: IPC only"), g("oracle: no accidentals"), g("oracle: no cosmics"), g("as is")
    V = lambda r: (r["reach3"] / 3 * r["X17"]) ** 2
    a = V(ipc) / (ipc["M1"] + ipc["E0"])
    c = (V(nacc) - a * (nacc["M1"] + nacc["E0"] + nacc["G"])) / max(nacc["COS"], 1e-9)
    b = (V(ncos) - a * (ncos["M1"] + ncos["E0"] + ncos["G"])) / max(ncos["ACC"], 1e-9)
    pred = math.sqrt(a * (asis["M1"] + asis["E0"] + asis["G"]) + b * asis["ACC"] + c * asis["COS"]) / asis["X17"] * 3
    # trigger rate f = pR + qR^2 from (as-is R0) and (IPC-only R_MAX); occupancy k from X17 ratio
    r0, r1 = asis, ipc
    A = np.array([[r0["best_R"], r0["best_R"] ** 2], [r1["best_R"], r1["best_R"] ** 2]])
    p, q = np.linalg.solve(A, [r0["trig_Hz"], r1["trig_Hz"]]) if r0["best_R"] != r1["best_R"] else (r1["trig_Hz"] / r1["best_R"], 0.0)
    k = None
    if r0["best_R"] != r1["best_R"]:
        rat = (r1["X17"] / r0["X17"]) / (r1["best_R"] / r0["best_R"] * r1["live"] / r0["live"])
        k = -math.log(rat) / (2 * (r1["best_R"] - r0["best_R"]))
    return dict(a=a, b=b, c=c, p=p, q=q, k=k, asis=asis, ipc=ipc, pred=pred, rows=rs, pick=pick)

def scan(m, ref, k, scen, occ=True, dead=True, Rs=np.logspace(9.5, 12.3, 300)):
    """ref: a row giving per-R normalisations; scen zeroes classes."""
    R0 = ref["best_R"]
    out = []
    for R in Rs:
        f = m["p"] * R + m["q"] * R * R
        lv = 1 / (1 + f * TAU) if dead else 1.0
        lv0 = ref["live"] if dead else 1.0
        e = math.exp(-2 * k * R) if occ else 1.0
        e0 = math.exp(-2 * k * R0) if occ else 1.0
        sS = R / R0 * lv / lv0 * e / e0
        X = ref["X17"] * sS
        I = (ref["M1"] + ref["E0"] + ref["G"]) * sS
        Acc = ref["ACC"] * (R / R0) ** 2 * lv / lv0 * ("acc" in scen)
        Cos = ref["COS"] * lv / lv0 * ("cos" in scen)
        out.append((R, 3 * math.sqrt(m["a"] * I + m["b"] * Acc + m["c"] * Cos) / X, lv, e))
    return out

for f, pick, lab in (("bo_ringCFRP.csv", 0, "no panel, Esum>13"), ("e14.csv", 0, "panel, Esum>14")):
    m = analyse(f, pick)
    k = m["k"] or 1.16e-11
    print(f"\n== {lab}: a={m['a']:.3g} b={m['b']:.3g} c={m['c']:.3g}  trig p={m['p']:.3g}/n q={m['q']:.3g}  k={k:.3g} (occ@1.9e10={k*1.9e10:.2f})")
    print(f"   as-is check: model {m['pred']:.3e} vs fit {m['asis']['reach3']:.3e}")
    ref = m["ipc"]  # at R_MAX; carries ACC=COS=0, so take ACC/COS from as-is scaled
    asis = m["asis"]
    ref = dict(ref)
    ref["ACC"] = asis["ACC"] * (ref["best_R"] / asis["best_R"]) ** 2 * ref["live"] / asis["live"]
    ref["COS"] = asis["COS"] * ref["live"] / asis["live"]
    for scen, nm in ((("acc", "cos"), "as is"), (("cos",), "no accidentals (He tube + no Be)"), ((), "IPC only")):
        for occ, dead, tag in ((True, True, "MM occ + DAQ dead"), (False, True, "DAQ dead only"), (False, False, "neither")):
            s = scan(m, ref, k, scen, occ, dead)
            at = lambda RR: min(s, key=lambda t: abs(t[0] - RR))
            best = min(s, key=lambda t: t[1])
            print(f"   {nm:34s} {tag:18s} @1.9e10 {at(1.9e10)[1]:.2e}  @1e11 {at(1e11)[1]:.2e}  @1e12 {at(1e12)[1]:.2e}   best {best[1]:.2e} at R={best[0]:.2g} (live {best[2]:.2f}, eff_occ {best[3]:.2f})")
