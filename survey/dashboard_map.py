#!/usr/bin/env python3
"""
dashboard_map.py -- the world map behind the facility dashboard, pre-projected.

    curl -sSfLO https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/land-110m.json
    curl -sSfLO https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json
    python -I survey/dashboard_map.py land-110m.json countries-110m.json \
        ~/PycharmProjects/dylan-cern-site/data/world-map.json

Natural Earth 1:110m (public domain, via world-atlas 2.0.2), Equal Earth projection, Antarctica
dropped.  Writes two SVG path strings, land and country borders, in projected units (x right,
y down, λ = ±π maps to x = ±2.7064).  js/facilities-survey.js projects the markers with the same
formula (equalEarth there), so both must change together.  Run once; the map does not change.
"""
import json
import math
import sys

A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
M = math.sqrt(3) / 2


def equal_earth(lon, lat):
    lam, phi = math.radians(lon), math.radians(lat)
    th = math.asin(M * math.sin(phi))
    t2 = th * th
    t6 = t2 * t2 * t2
    x = lam * math.cos(th) / (M * (A1 + 3 * A2 * t2 + t6 * (7 * A3 + 9 * A4 * t2)))
    y = th * (A1 + A2 * t2 + t6 * (A3 + A4 * t2))
    return x, -y


def decode_arcs(topo):
    sx, sy = topo['transform']['scale']
    tx, ty = topo['transform']['translate']
    arcs = []
    for arc in topo['arcs']:
        x = y = 0
        pts = []
        for dx, dy in arc:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    return arcs


def ring(arcs, idx):
    pts = []
    for i in idx:
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.extend(a if not pts else a[1:])
    return pts


def cut_antimeridian(pts, closed):
    """Split a lon/lat line where it crosses ±180° (Chukotka, Fiji), so the projected path does
    not jump across the map and smear a band of fill.  Each piece of a ring is closed along the
    edge meridian it touches."""
    if not any(abs(b[0] - a[0]) > 180 for a, b in zip(pts, pts[1:])):
        return [pts]
    if closed:                                        # start the walk at a crossing
        k = next(i for i in range(1, len(pts)) if abs(pts[i][0] - pts[i - 1][0]) > 180)
        pts = pts[k:] + pts[1:k + 1] if pts[0] == pts[-1] else pts[k:] + pts[:k]
    pieces, cur = [], [pts[0]]
    for a, b in zip(pts, pts[1:]):
        if abs(b[0] - a[0]) > 180:
            edge = 180.0 if a[0] > 0 else -180.0
            bl = b[0] + (360 if edge > 0 else -360)
            lat = a[1] if bl == a[0] else a[1] + (b[1] - a[1]) * (edge - a[0]) / (bl - a[0])
            cur.append((edge, lat))
            pieces.append(cur)
            cur = [(-edge, lat), b]
        else:
            cur.append(b)
    pieces.append(cur)
    if not closed:
        return pieces
    out = []
    for pc in pieces:
        if len(pc) < 3:
            continue
        e, l0, l1 = pc[-1][0], pc[-1][1], pc[0][1]   # walk the edge meridian back to the start
        out.append(pc + [(e, l0 + (l1 - l0) * i / 8) for i in range(1, 9)])
    return out


def path(lines, closed):
    out = []
    for pts in (p for line in lines for p in cut_antimeridian(line, closed)):
        if closed and all(lat < -60 for _, lat in pts):
            continue                                  # Antarctica
        xy = [equal_earth(lo, la) for lo, la in pts]
        seg = [f'{x:.3f} {y:.3f}' for x, y in xy]
        ded = [s for i, s in enumerate(seg) if i == 0 or s != seg[i - 1]]
        if len(ded) < 2:
            continue
        out.append('M' + 'L'.join(ded) + ('Z' if closed else ''))
    return ''.join(out)


def main(land_f, countries_f, out_f):
    land = json.load(open(land_f))
    arcs = decode_arcs(land)
    rings = []
    for g in land['objects']['land']['geometries']:
        polys = g['arcs'] if g['type'] == 'MultiPolygon' else [g['arcs']]
        for poly in polys:
            rings += [ring(arcs, r) for r in poly]
    # country borders: arcs shared by two countries (topojson.mesh(a !== b))
    ctry = json.load(open(countries_f))
    carcs = decode_arcs(ctry)
    use = {}
    for g in ctry['objects']['countries']['geometries']:
        polys = g['arcs'] if g['type'] == 'MultiPolygon' else [g['arcs']] if g['type'] == 'Polygon' else []
        for poly in polys:
            for r in poly:
                for i in r:
                    use[i if i >= 0 else ~i] = use.get(i if i >= 0 else ~i, 0) + 1
    borders = [carcs[i] for i, n in use.items() if n > 1 and not all(la < -60 for _, la in carcs[i])]
    x0, _ = equal_earth(-180, 0)
    _, y0 = equal_earth(0, 84)
    _, y1 = equal_earth(0, -58)
    doc = dict(projection='equalEarth', source='Natural Earth 1:110m via world-atlas@2.0.2',
               bounds=[x0, y0, -x0, y1], land=path(rings, True), borders=path(borders, False))
    json.dump(doc, open(out_f, 'w'), separators=(',', ':'))
    print(out_f, sum(len(v) for v in (doc['land'], doc['borders'])) // 1024, 'kB of path')


if __name__ == '__main__':
    main(*sys.argv[1:4])
