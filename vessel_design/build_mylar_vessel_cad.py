"""Build the mylar-wrap 3He cell as real solids and export STEP + per-part STL.

Run with FreeCAD's interpreter, not the system one:

    freecadcmd vessel_design/build_mylar_vessel_cad.py

Outputs land in vessel_design/out/.  The mylar is drawn at p.t_skin_render
(0.2 mm) rather than its true 12 um, otherwise it is invisible in any viewer;
every material-budget number uses the real thickness.
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "out")

import FreeCAD as App
import Mesh
import Part
from FreeCAD import Vector

from mylar_wrap_vessel import (LAND_DEFAULT, VesselParams, flat_rod_corners,
                               offset_polygon, skin_section)

LAND = LAND_DEFAULT
TESS = 0.08        # STL tessellation tolerance, mm


def prism(poly, z0, z1):
    """Solid prism from a closed 2D polygon, spanning z0..z1."""
    pts = [Vector(float(x), float(y), z0) for x, y in poly]
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(Vector(0, 0, z1 - z0))


def shell(poly_in, poly_out, z0, z1):
    return prism(poly_out, z0, z1).cut(prism(poly_in, z0, z1))


def rod_solids(p):
    """The five round carbon rods, as solids along z."""
    out = []
    for th in p.rod_angles()[1:]:
        c = p.r_centre * np.array([np.cos(th), np.sin(th)])
        out.append(Part.makeCylinder(p.r_thin, p.l_cyl,
                                     Vector(float(c[0]), float(c[1]), -0.5 * p.l_cyl),
                                     Vector(0, 0, 1)))
    return out


def flat_rod_solid(p, z0=None, z1=None):
    z0 = -0.5 * p.l_cyl if z0 is None else z0
    z1 = 0.5 * p.l_cyl if z1 is None else z1
    return prism(flat_rod_corners(p), z0, z1)


def build(p):
    """Return an ordered list of (name, shape, stl_flag)."""
    inner = skin_section(p)                                  # foil inner face
    outer = offset_polygon(inner, p.t_skin_render)
    over = offset_polygon(outer, p.t_skin_render)             # seam second layer
    half = 0.5 * p.l_cyl

    parts = []

    # --- the gas barrier: one wrap, plus the mylar-on-mylar seam over the flat rod
    parts.append(("mylar_skin", shell(inner, outer, -half, half)))

    th = p.rod_angles()[0]
    rad = np.array([np.cos(th), np.sin(th)])
    tan = np.array([-np.sin(th), np.cos(th)])
    w = 0.5 * (p.w_flat + p.seam_overlap)
    seam_poly = np.array([
        (p.r_env + p.t_skin_render) * rad + w * tan,
        (p.r_env + p.t_skin_render) * rad - w * tan,
        (p.r_env + 2 * p.t_skin_render) * rad - w * tan,
        (p.r_env + 2 * p.t_skin_render) * rad + w * tan,
    ])
    parts.append(("mylar_seam_overlap", prism(seam_poly, -half, half)))

    # glue lines: first bond to the rod, second bond foil-on-foil
    for tag, r0 in (("bond_rod_to_foil", p.r_env),
                    ("bond_foil_to_foil", p.r_env + p.t_skin_render)):
        g = np.array([r0 * rad + 0.5 * p.w_flat * tan,
                      r0 * rad - 0.5 * p.w_flat * tan,
                      (r0 + p.t_glue) * rad - 0.5 * p.w_flat * tan,
                      (r0 + p.t_glue) * rad + 0.5 * p.w_flat * tan])
        parts.append(("glue_" + tag, prism(g, -half, half)))

    # --- the rod cage
    cage = rod_solids(p)
    parts.append(("carbon_rods_round", Part.Compound(cage)))
    parts.append(("carbon_rod_flat", flat_rod_solid(p)))

    # --- endcaps: material TBD, geometry is a placeholder joint concept.
    # A disc plus a land shaped like the cell cross-section, so the mylar skirt
    # has something to be bonded down onto, with pockets for the rod ends.
    r_disc = p.r_env + p.endcap_margin
    caps = []
    for sgn in (-1, 1):
        z_face = sgn * half
        disc = Part.makeCylinder(r_disc, p.t_endcap,
                                 Vector(0, 0, z_face if sgn > 0 else z_face - p.t_endcap),
                                 Vector(0, 0, 1))
        land = prism(offset_polygon(inner, -0.10),
                     *sorted([z_face, z_face - sgn * LAND]))
        cap = disc.fuse(land)
        pockets = rod_solids(p) + [flat_rod_solid(p)]
        for pk in pockets:
            cap = cap.cut(pk)
        caps.append(cap)
    parts.append(("endcaps_TBD", Part.Compound(caps)))

    # gas fill / pump-out port on the downstream cap
    port = Part.makeCylinder(3.0, 25.0, Vector(0, -r_disc + 4, half + 0.5 * p.t_endcap),
                             Vector(0, -1, 0))
    parts.append(("fill_port", port))

    # --- reference volumes, not hardware
    gas = prism(inner, -half, half)
    for pk in rod_solids(p) + [flat_rod_solid(p)]:
        gas = gas.cut(pk)
    parts.append(("he3_gas_volume", gas))
    parts.append(("beam_envelope", Part.makeCylinder(
        0.5 * p.d_beam, p.l_cyl + 4 * p.t_endcap + 120,
        Vector(0, 0, -(half + 2 * p.t_endcap + 60)), Vector(0, 0, 1))))
    return parts


def main():
    p = VesselParams()
    os.makedirs(OUT, exist_ok=True)
    parts = build(p)

    # STEP export needs document objects, not bare shapes, and naming them here
    # is what makes the assembly readable once it is opened downstream.
    doc = App.newDocument("he3_mylar_vessel")
    objs = {}
    for name, shape in parts:
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        obj.Label = name
        objs[name] = obj
    doc.recompute()

    for name, shape in parts:
        Mesh.Mesh(shape.tessellate(TESS)).write(os.path.join(OUT, name + ".stl"))

    volumes = [(n, s.Volume) for n, s in parts]

    hardware = [objs[n] for n, _ in parts
                if n not in ("he3_gas_volume", "beam_envelope")]
    Part.export(hardware, os.path.join(OUT, "he3_mylar_vessel.step"))
    Part.export([objs[n] for n, _ in parts],
                os.path.join(OUT, "he3_mylar_vessel_with_volumes.step"))
    doc.saveAs(os.path.join(OUT, "he3_mylar_vessel.FCStd"))

    App.Console.PrintMessage("\nRESULTS\n")
    for n, v in volumes:
        App.Console.PrintMessage("  %-22s vol = %10.1f mm3\n" % (n, v))
    App.Console.PrintMessage("  wrote he3_mylar_vessel.step / _with_volumes.step / .FCStd\n")


main()
